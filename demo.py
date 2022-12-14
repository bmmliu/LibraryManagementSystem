import streamlit as st

from router import router, args
from utils import query_db
from login import login_required

@router(path="/demo")
@login_required
def render():
    "## Read tables"
    st.markdown("# Args: id=" + args("id"))

    sql_all_table_names = "SELECT relname FROM pg_class WHERE relkind='r' AND relname !~ '^(pg_|sql_)';"
    try:
        all_table_names = query_db(sql_all_table_names)["relname"].tolist()
        table_name = st.selectbox("Choose a table", all_table_names)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if table_name:
        f"Display the table"

        sql_table = f"SELECT * FROM {table_name};"
        try:
            df = query_db(sql_table)
            st.dataframe(df)
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "## Query customers"

    sql_customer_names = "SELECT name FROM customers;"
    try:
        customer_names = query_db(sql_customer_names)["name"].tolist()
        customer_name = st.selectbox("Choose a customer", customer_names)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if customer_name:
        sql_customer = f"SELECT * FROM customers WHERE name = '{customer_name}';"
        try:
            customer_info = query_db(sql_customer).loc[0]
            c_age, c_city, c_state = (
                customer_info["age"],
                customer_info["city"],
                customer_info["state"],
            )
            st.write(
                f"{customer_name} is {c_age}-year old, and lives in {c_city}, {c_state}."
            )
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )

    "## Query orders"

    sql_order_ids = "SELECT order_id FROM orders;"
    try:
        order_ids = query_db(sql_order_ids)["order_id"].tolist()
        order_id = st.selectbox("Choose an order", order_ids)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if order_id:
        sql_order = f"""
            SELECT C.name, O.order_date
            FROM orders as O, customers as C 
            WHERE O.order_id = {order_id}
            AND O.customer_id = C.id;"""

        try:
            customer_info = query_db(sql_order).loc[0]
            customer_name, order_date = (
                customer_info["name"],
                customer_info["order_date"],
            )
            st.write(f"This order is placed by {customer_name} on {order_date}.")
        except:
            st.write(
                "Sorry! Something went wrong with your query, please try again."
            )
