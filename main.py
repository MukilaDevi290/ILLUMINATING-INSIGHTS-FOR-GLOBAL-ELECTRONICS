import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt
from sqlalchemy import create_engine



# Streamlit Page Configuration
st.set_page_config(page_title="Customer Analysis Dashboard", page_icon="📊", layout="wide")
st.title("Customer Analysis Dashboard")

# Connection string details
host = "localhost"
port = "5432"
database = "homedb"
user = "postgres"
password = "mukisam290"

# Create the connection string (URL format) -> postgresql://username:password@host:port/database
engine_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Create SQLAlchemy engine
engine = create_engine(engine_string)


# --- Fetch Data from PostgreSQL ---
def fetch_customers_data():
    query = """
    SELECT "CustomerKey", "Gender", "Name", "City", "State", "Country",
           "Continent", "Birthday", "age", "location"
    FROM customers_info;
    """
    df = pd.read_sql(query, engine)
    return df


def fetch_sales_data():
    query = """
    SELECT "Order Number", "Order Date", "CustomerKey", "StoreKey", "ProductKey", "Quantity",
           "Currency Code", "OrderYear"
    FROM sales_info;
    """
    df = pd.read_sql(query, engine)
    return df


def fetch_products_data():
    query = """
    SELECT "ProductKey", "Product Name", "Brand", "Color", "Unit Cost USD", "Unit Price USD",
           "SubcategoryKey","Subcategory", "CategoryKey","Category"
    FROM products_info;
    """
    df = pd.read_sql(query, engine)
    return df


def fetch_stores_data():
    query = """
    SELECT "StoreKey", "Country", "State", "SquareMetres", "OpenDate","Open Year"
    FROM store_info;
    """
    df = pd.read_sql(query, engine)
    return df


def fetch_exchange_rate_data():
    query = """
    SELECT "Date", "Currency Code", "Exchange"
    FROM exchange_rates_info;
    """
    df = pd.read_sql(query, engine)
    return df

# --- Load Data ---
customers_df = fetch_customers_data()
sales_df = fetch_sales_data()
products_df = fetch_products_data()
stores_df = fetch_stores_data()
exchange_rate_df = fetch_exchange_rate_data()


# --- Tabs Section ---
tabs = st.tabs(["Customer Analysis", "Sales Analysis", "Product Analysis", "Store Analysis"])

# --- Customer Analysis Tab ---
with tabs[0]:
    st.header("Customer Analysis")
    
   # --- Gender Pie Chart ---
    gender_fig = px.pie(
    customers_df,
    names='Gender',
    title="Customer Distribution by Gender",
    hole=0.3,  # makes it a donut chart
    )
    st.plotly_chart(gender_fig, use_container_width=True)

    # Create Age Groups
    bins = [0, 18, 30, 40, 50, 60, 100]
    labels = ['0-18', '19-30', '31-40', '41-50', '51-60', '60+']
    customers_df.loc[:,'Age Group'] = pd.cut(customers_df['age'], bins=bins, labels=labels, right=False)



    # --- Age Group Line Graph ---
    age_group_counts = customers_df['age'].value_counts().sort_index()
    age_group_fig = px.line(
    age_group_counts,
    x=age_group_counts.index,
    y=age_group_counts.values,
    title="Customer Distribution by Age Group",
    labels={'x': 'Age Group', 'y': 'Customers Count'},
    )
    st.plotly_chart(age_group_fig, use_container_width=True,key="plot0")

    
    
    
    # --- Purchase Patterns ---
    st.subheader("Purchase Patterns: Average Order Value (AOV), Frequency, and Preferred Products")
    
    # Merge Sales Data with Customer Data
    merged_sc_df = pd.merge(sales_df, customers_df, on='CustomerKey')
    
    aov_df = merged_sc_df.groupby('CustomerKey').agg({
    'Order Number': 'nunique', 
    'Quantity': 'sum'
     }).reset_index()

    #Compute Average Order Value (AOV)
    aov_df['AOV'] = aov_df['Quantity'] / aov_df['Order Number']

    # Compute Purchase Frequency correctly using the number of orders per customer
    aov_df['Purchase Frequency'] = aov_df['Order Number']
    # Visualize AOV
    col1, col2 = st.columns(2)
    with col1:
        aov_fig = px.histogram(
        aov_df, 
        x='AOV', 
        nbins=20, 
        title="Average Order Value (AOV) Distribution", 
        labels={'AOV': 'Average Order Value', 'count': 'Number of Customers'}
    )
    st.plotly_chart(aov_fig)

    # Visualize Purchase Frequency
    with col2:
        frequency_fig = px.histogram(
        aov_df, 
        x='Purchase Frequency', 
        nbins=20, 
        title="Purchase Frequency Distribution", 
        labels={'Purchase Frequency': 'Frequency', 'count': 'Number of Customers'}
    )
    st.plotly_chart(frequency_fig)

    
    # --- Merge sales Data with Product Data ---
    merged_sp_df = pd.merge(sales_df, products_df, on='ProductKey')

    
    # --- Preferred Products Analysis ---
    st.subheader("Preferred Products by Customers")
    
    # Count the most preferred products
    preferred_products = merged_sp_df['Product Name'].value_counts().reset_index()
    preferred_products.columns = ['Product', 'Count']
    
    # Data visualization
    preferred_products_fig = px.bar(preferred_products.head(20), x='Product', y='Count', title=" Preferred Products",labels={'product':'products Name','Count':'Customers Count'})
    st.plotly_chart(preferred_products_fig, use_container_width=True,key="plot1")

   
   
   
    # --- Customer Segmentation ---
    st.subheader("Customer Segmentation Based on Demographics and Purchasing Behavior")
    
    segmentation_df = aov_df.copy()
    segmentation_df['Age Group'] = customers_df['Age Group']
    segmentation_df['Gender'] = customers_df['Gender']
    
    segmentation_fig = px.scatter(
        segmentation_df, x='AOV', y='Purchase Frequency', color='Age Group', symbol='Gender',
        title="Customer Segmentation by AOV and Frequency",
        hover_data=['Age Group', 'Gender', 'AOV', 'Purchase Frequency']
    )
    st.plotly_chart(segmentation_fig, use_container_width=True,key="plot2")





# --- Sales Analysis Tab ---
with tabs[1]:
    st.header("Sales Analysis")

    
    # Merge sales_df with exchange_rate_df on 'Currency Code'
    merged_se_df = pd.merge(sales_df, exchange_rate_df, on='Currency Code')
    
    # Calculate Revenue: Quantity * Exchange rate
    merged_se_df['Revenue'] = merged_se_df['Quantity'] * merged_se_df['Exchange']
    
    # Aggregate Revenue by OrderYear
    sales_performance = merged_se_df.groupby('OrderYear').agg({'Revenue': 'sum'}).reset_index()

    # Visualization of Sales Performance by Year
    #st.subheader("Overall Sales Analysis by Year")
    sales_performance_fig = px.line(
        sales_performance, 
        x='OrderYear', 
        y='Revenue', 
        title="Overall Sales Over the Years", 
        labels={'OrderYear': 'Year', 'Revenue': 'Total Revenue'},
        markers=True
    )
    
    st.plotly_chart(sales_performance_fig, use_container_width=True,key="plot3")

    
    
    
    # Sales by Product
    st.subheader("Sales by Product")

    # Merge Sales exchange Data with Products Data to get Product Names and other details
    merged_sp_df1 = pd.merge(merged_se_df, products_df, on='ProductKey', how='left')

    # Aggregate Sales exchange Data by Product
    sales_by_product = merged_sp_df1.groupby('Product Name').agg({'Revenue': 'sum'}).reset_index()

    # Sort by Revenue to get the top products by revenue
    top_sales_by_product = sales_by_product.sort_values('Revenue', ascending=False)#

    # Plot Sales by Product
    sales_by_product_fig = px.bar(
        top_sales_by_product, 
        x='Product Name', 
        y='Revenue', 
        #title="Products by Revenue", 
        color='Product Name', 
        labels={'Product Name': 'Product Name', 'Revenue': 'Total Revenue'},
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    st.plotly_chart(sales_by_product_fig,use_container_width=True,key="plot4")


    
    
    # Sales by Store
    st.subheader("Sales by Store")
    # Merge Sales exchange data with Store Data
    merged_ss_df = pd.merge(merged_se_df, stores_df, on='StoreKey', how='left')

    # Aggregate Sales exchange Data by Store
    sales_by_store1 = merged_ss_df.groupby('Country').agg({'Revenue': 'sum'}).reset_index()
    sales_by_store1 = sales_by_store1.sort_values('Revenue', ascending=False)

    #  Plot Sales by Store
    sales_by_store_fig = px.bar(sales_by_store1, x='Country', y='Revenue', color='Country')
    st.plotly_chart(sales_by_store_fig, use_container_width=True)

    
    
    
    # Sales by Currency
    st.subheader("Sales by Currency")

    # Aggregate Sales Data by Currency
    sales_by_currency = merged_se_df.groupby('Currency Code').agg({'Revenue': 'sum'}).reset_index()

    # Plot Sales by Currency
    sales_by_currency_fig = px.bar(sales_by_currency, x='Currency Code', y='Revenue', color='Currency Code')
    st.plotly_chart(sales_by_currency_fig, use_container_width=True,key="plot5")






# --- Product Analysis Tab ---
with tabs[2]:
    st.header("Product Analysis")
    
    # --- Product Popularity Analysis ---
    st.subheader("Product Popularity Analysis")

    # Merge Sales with Product Data 
    merged_sales_product_df = pd.merge(sales_df, products_df, on='ProductKey', how='left')

    # Calculate Product Popularity
    product_popularity = merged_sales_product_df.groupby('Product Name').agg({'Quantity': 'sum'}).reset_index()

    # Sort by Quantity Sold
    product_popularity_sorted = product_popularity.sort_values('Quantity', ascending=False)

    # Get Top  Most Popular and Bottom Least Popular Products
    top_10_products = product_popularity_sorted.head(10).copy()
    bottom_10_products = product_popularity_sorted.tail(10).copy()

    # Add a column indicating if it’s "Most" or "Least" Popular
    top_10_products.loc[:,'Popularity'] = 'Most Popular'
    bottom_10_products.loc[:,'Popularity'] = 'Least Popular'

    # Combine both dataframes for visualization
    combined_popularity = pd.concat([top_10_products, bottom_10_products])

    # Plot Product Popularity (Most and Least)
    product_popularity_fig = px.bar(
    combined_popularity,
    x='Product Name',
    y='Quantity',
    title=" Most and Least Popular Products by Quantity Sold",
    color='Popularity',
    barmode='group',
    labels={'Product Name': 'Product Name', 'Quantity': 'Units Sold'},
    color_discrete_map={'Most Popular': 'blue', 'Least Popular': 'red'}
     )
    st.plotly_chart(product_popularity_fig, use_container_width=True,key="plot6")



     
     
     # Profitability Analysis: Calculate profit margins for products by comparing unit cost and unit price
    st.subheader("Profitability Analysis")

    
    # Calculate profit margin (Unit Price - Unit Cost) / Unit Price
    products_df.loc[:,'ProfitMargin'] = (products_df['Unit Price USD'] - products_df['Unit Cost USD']) / products_df['Unit Price USD'] * 100

    # Sort by Profit Margin
    profitability = products_df.sort_values('ProfitMargin', ascending=False)

    # Plot Profitability Analysis (Top  most profitable products)
    profitability_fig = px.bar(profitability, x='Brand', y='ProfitMargin', title=" Most Profitable Products", color='Brand')
    st.plotly_chart(profitability_fig, use_container_width=True)

    
    
    
    
    # Category Analysis: Analyze sales performance across different product categories and subcategories
    st.subheader("Category Analysis")

    # Merge sales data with product data to get Category and SubCategory
    merged_category_sales_df = pd.merge(sales_df, products_df, on='ProductKey', how='left')

    # Aggregate sales by Category and SubCategory
    category_sales = merged_category_sales_df.groupby(['Category', 'Subcategory']).agg({'Quantity': 'sum'}).reset_index()

    # Sort by Quantity for better visualization
    category_sales = category_sales.sort_values('Quantity', ascending=False)

    # Plot Category Analysis: Sales by Category and SubCategory
    category_sales_fig = px.bar(
    category_sales, 
    x='Subcategory', 
    y='Quantity', 
    color='Category',
    title="Sales by Product Category and SubCategory",
    labels={'Subcategory': 'Subcategory', 'Quantity': 'Quantity Sold'},
    barmode='group'
    )

    st.plotly_chart(category_sales_fig, use_container_width=True,key="plot7")






# --- Store Analysis Tab ---
with tabs[3]:
    st.header("Store Analysis")
    st.subheader("Store Performance Based On Open Date (Years) and Size(Squaremetres)")

    
    #merged sales exchange data with stores data
    merged_sales_stores_df = pd.merge(merged_se_df, stores_df, on='StoreKey', how='left')

    # Step 2: Calculate Revenue
    merged_sales_stores_df.loc[:,'Revenue'] = merged_sales_stores_df['Quantity'] * merged_sales_stores_df['Exchange']

    # Step 3: Aggregate Sales Data by Store 
    store_performance = merged_sales_stores_df.groupby(['Open Year']).agg({'Revenue': 'sum', 'Quantity': 'sum', 'SquareMetres' : 'sum'}).reset_index()

    # Step 4: Plot Bar Graph for Square Meters and Revenue
    bar_fig = px.bar(
        store_performance,
        x='SquareMetres',    # Use Square Metres on the x-axis
        y='Revenue',         # Use Revenue on the y-axis
        labels={'SquareMetres': 'Square Meters', 'Revenue': 'Revenue'},
        color='Open Year',   # Color bars by the Open Year
        text='Revenue'       # Show revenue as text labels on bars
    )


    st.plotly_chart(bar_fig, use_container_width=True,key="plot8")


     
    
    
    
    # --- Geographical Analysis ---
    st.subheader("Geographical Analysis: Sales by Store Location")

    # Merge Sales exchange with Store Data to get Location
    merged_ss_df2 = pd.merge(merged_se_df, stores_df, on='StoreKey', how='left')

    
    #calculate the revenue
    merged_sales_stores_df.loc[:,'Revenue'] = merged_ss_df2['Quantity'] * merged_ss_df2['Exchange']

    # Aggregate Sales Data by Location (Country)....
    store_location_sales = merged_sales_stores_df.groupby('Country').agg({'Revenue': 'sum'}).reset_index()

    # Sort by Revenue to identify top-performing regions
    store_location_sales = store_location_sales.sort_values('Revenue', ascending=False)

    # Plot Geographical Analysis (Sales by Location)
    geographical_sales_fig = px.choropleth(
    store_location_sales, 
    locations="Country",  # Use the 'Country' column for store location
    color="Revenue", 
    hover_name="Country", 
    color_continuous_scale=px.colors.sequential.Plasma,
    locationmode="country names"  # Ensure 'Country' contains country names or ISO codes
    )

    st.plotly_chart(geographical_sales_fig, use_container_width=True,key="plot10")




