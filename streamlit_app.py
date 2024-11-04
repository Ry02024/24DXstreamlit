# Save this file as `streamlit_app.py`
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

# Load and merge data
def load_and_merge_data(sales_file, item_file, category_file):
    # Load each dataset
    sales_df = pd.read_csv(sales_file)
    item_df = pd.read_csv(item_file)
    category_df = pd.read_csv(category_file)

    # Merge sales data with item categories
    sales_df = sales_df.merge(item_df, on='商品ID', how='left')

    # Merge with category names to get 商品カテゴリ名
    sales_df = sales_df.merge(category_df, on='商品カテゴリID', how='left')

    return sales_df

# Create pie chart for category sales distribution
def plot_pie_chart(sales_df):
    category_sales = sales_df.groupby('商品カテゴリ名')['売上個数'].sum()
    fig, ax = plt.subplots()
    ax.pie(category_sales, labels=None, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.legend(category_sales.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize='small')
    plt.title("売上カテゴリの割合")
    return fig

import matplotlib.dates as mdates

# Updated function to process dates correctly and plot in monthly intervals
def plot_line_chart(sales_df, y_column, title):
    # Ensure the '日付' column is in datetime format
    sales_df['日付'] = pd.to_datetime(sales_df['日付'])
    
    # Aggregate data by month for readability
    sales_by_date = sales_df.set_index('日付').resample('M')[y_column].sum().reset_index()
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))  # Wider figure
    ax.plot(sales_by_date['日付'], sales_by_date[y_column])
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(y_column)

    # Set x-axis to show monthly ticks and format the dates
    ax.xaxis.set_major_locator(mdates.MonthLocator())  # Major ticks every month
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format as Year-Month
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability

    return fig


# Create bar chart for top products by sales amount
def plot_bar_chart(sales_df):
    top_products = sales_df.groupby(['商品ID', '商品カテゴリ名'])['商品価格'].sum().nlargest(10).reset_index()
    fig, ax = plt.subplots()
    ax.barh(top_products['商品カテゴリ名'], top_products['商品価格'])
    ax.set_xlabel("売上金額")
    ax.set_ylabel("商品カテゴリ名")
    return fig

# Streamlit app main function
def main():
    st.title('売上ダッシュボード')

    # File uploaders
    st.sidebar.title("データファイルのアップロード")
    sales_file = st.sidebar.file_uploader("売上データファイル (sales_history.csv)", type=["csv"])
    item_file = st.sidebar.file_uploader("商品データファイル (item_categories.csv)", type=["csv"])
    category_file = st.sidebar.file_uploader("カテゴリデータファイル (category_names.csv)", type=["csv"])

    # Load and process data if all files are uploaded
    if sales_file and item_file and category_file:
        sales_df = load_and_merge_data(sales_file, item_file, category_file)

        # Display KPIs
        total_sales_quantity = sales_df['売上個数'].sum()
        total_sales_amount = (sales_df['商品価格'] * sales_df['売上個数']).sum()
        st.metric(label="売上個数", value=f"{total_sales_quantity:,}")
        st.metric(label="売上金額", value=f"{total_sales_amount:,.0f}")

        # Pie Chart
        st.subheader("売上カテゴリの割合")
        st.pyplot(plot_pie_chart(sales_df))

        # Line Charts
        st.subheader("売上金額の推移")
        st.pyplot(plot_line_chart(sales_df, '商品価格', '売上金額'))
        st.subheader("売上個数の推移")
        st.pyplot(plot_line_chart(sales_df, '売上個数', '売上個数'))

        # Bar Chart
        st.subheader("商品別売上金額トップ")
        st.pyplot(plot_bar_chart(sales_df))

        # Data Table
        st.subheader("売上トップ10商品")
        top_products_df = sales_df.groupby(['商品ID', '商品カテゴリ名'])['商品価格'].sum().nlargest(10).reset_index()
        st.dataframe(top_products_df)
    else:
        st.warning("すべてのデータファイルをアップロードしてください。")

if __name__ == '__main__':
    main()
