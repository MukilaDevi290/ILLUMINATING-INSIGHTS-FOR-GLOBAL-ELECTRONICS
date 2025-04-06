import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Connection string details
host = "localhost"
port = "5432"
database = "homedb"
user = "postgres"
password = "mukisam290"

# Create the connection string (URL format)
engine_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(engine_string)

# Initialize session state variables if not already initialized
if 'query_result' not in st.session_state:
    st.session_state.query_result = None

if 'selected_question' not in st.session_state:
    st.session_state.selected_question = None

# Dropdown menu for questions and corresponding SQL queries
questions_and_queries = {
    "What percentage of customers are male and female?": """
        SELECT "Gender", COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS percentage
        FROM customers_info
        GROUP BY "Gender";
    """,
    "Where are the customers located?": """
        SELECT "Country", COUNT(*) AS total_customers
        FROM customers_info
        GROUP BY "Country"
        ORDER BY total_customers DESC;
    """,
    "Which age group prefers products most and least?": """
        SELECT 
            CASE 
                WHEN c."age" < 18 THEN 'Under 18'
                WHEN c."age" BETWEEN 18 AND 24 THEN '18-24'
                WHEN c."age" BETWEEN 25 AND 34 THEN '25-34'
                WHEN c."age" BETWEEN 35 AND 44 THEN '35-44'
                WHEN c."age" BETWEEN 45 AND 54 THEN '45-54'
                ELSE '55 and above'
            END AS "Age Group",
            p."Product Name",
            SUM(s."Quantity") AS total_quantity
        FROM sales_info s
        JOIN customers_info c ON s."CustomerKey" = c."CustomerKey"
        JOIN products_info p ON s."ProductKey" = p."ProductKey"
        GROUP BY "Age Group", p."Product Name"
        ORDER BY total_quantity DESC;
    """,
    
    
    "What products are preferred by customers based on subcategories?": """
        SELECT p."Subcategory", SUM(s."Quantity") AS total_quantity
        FROM sales_info s
        JOIN products_info p ON s."ProductKey" = p."ProductKey"
        GROUP BY p."Subcategory"
        ORDER BY total_quantity DESC;
    """,
    "What are the most profitable products?": """
        SELECT p."Product Name", SUM(s."Quantity" * e."Exchange") AS total_revenue
        FROM sales_info s
        JOIN products_info p ON s."ProductKey" = p."ProductKey"
        JOIN exchange_rates_info e ON s."Currency Code" = e."Currency Code"
        GROUP BY p."Product Name"
        ORDER BY total_revenue DESC
        LIMIT 10;
    """,
    "Which brands are preferred by customers?": """
        SELECT p."Brand", SUM(s."Quantity") AS total_quantity
        FROM sales_info s
        JOIN products_info p ON s."ProductKey" = p."ProductKey"
        GROUP BY p."Brand"
        ORDER BY total_quantity DESC;
    """,
    "Which countries have the highest sales by stores?": """
        SELECT st."Country", SUM(s."Quantity" * e."Exchange") AS total_sales
        FROM sales_info s
        JOIN store_info st ON s."StoreKey" = st."StoreKey"
        JOIN exchange_rates_info e ON s."Currency Code" = e."Currency Code"
        GROUP BY st."Country"
        ORDER BY total_sales DESC;
    """,
    "What is the overall sales over the years?": """
        SELECT "OrderYear", SUM("Quantity" * e."Exchange") AS total_sales
        FROM sales_info s
        JOIN exchange_rates_info e ON s."Currency Code" = e."Currency Code"
        GROUP BY "OrderYear"
        ORDER BY "OrderYear";
    """,
    "Which currency codes have the highest sales?": """
        SELECT s."Currency Code", SUM(s."Quantity" * e."Exchange") AS total_sales
        FROM sales_info s
        JOIN exchange_rates_info e ON s."Currency Code" = e."Currency Code"
        GROUP BY s."Currency Code"
        ORDER BY total_sales DESC;
    """,
    "What is the overall sales by products?": """
        SELECT p."Product Name", SUM(s."Quantity" * e."Exchange") AS total_sales
        FROM sales_info s
        JOIN products_info p ON s."ProductKey" = p."ProductKey"
        JOIN exchange_rates_info e ON s."Currency Code" = e."Currency Code"
        GROUP BY p."Product Name"
        ORDER BY total_sales DESC;
    """
}

# Streamlit UI
st.title("Sales Insights Dashboard")

# Dropdown menu for selecting the question
selected_question = st.selectbox("Select a Question:", list(questions_and_queries.keys()))

# Only run query if the selected question has changed
if selected_question != st.session_state.selected_question:
    st.session_state.selected_question = selected_question
    query = questions_and_queries[selected_question]

    try:
        # Run the query and fetch results
        result = pd.read_sql(query, engine)
        st.session_state.query_result = result
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Show the results stored in session state if available
if st.session_state.query_result is not None:
    st.write(st.session_state.query_result)
else:
    st.write("Please select a question to display the results.")
