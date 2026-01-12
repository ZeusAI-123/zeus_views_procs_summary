from snowflakeconnector import connect_snowflake
import streamlit as st
from db_connection import get_connection
from db_metadata import (
    get_sqlserver_views_and_procs,
    get_snowflake_views_and_procs
)
from metadata_reader import (
    get_all_views,
    get_all_procedures,
    get_object_definition
)
from llm_summary import generate_10_point_summary

st.title("Database View / Procedure Explorer")

db_type = st.radio(
    "Select Database Type",
    ["SQL Server", "Snowflake"]
)

# ---------------- SQL SERVER ----------------
if db_type == "SQL Server":
    st.subheader("🔌 SQL Server Connection")

    server = st.text_input("Server")
    database = st.text_input("Database")
    user = st.text_input("User")
    password = st.text_input("Password", type="password")
    driver = st.text_input(
        "ODBC Driver",
        "ODBC Driver 17 for SQL Server"
    )

# ---------------- SNOWFLAKE ----------------
if db_type == "Snowflake":
    st.subheader("❄️ Snowflake Connection")

    account = st.text_input("Account (without .snowflakecomputing.com)")
    user = st.text_input("User")
    password = st.text_input("Password", type="password")
    warehouse = st.text_input("Warehouse")
    database = st.text_input("Database")
    schema = st.text_input("Schema")
    role = st.text_input("Role (optional)")

# ---------------- CONNECT ----------------
if st.button("Connect"):
    try:
        if db_type == "SQL Server":
            conn = get_connection(
                server, database, user, password, driver
            )
            views, procs = get_sqlserver_views_and_procs(conn)

        else:
            conn = connect_snowflake(
                account, user, password,
                warehouse, database, schema, role or None
            )
            views, procs = get_snowflake_views_and_procs(
                conn, database, schema
            )

        st.success("✅ Connected successfully")

        # ---------------- DROPDOWNS ----------------
        st.subheader("📂 Database Objects")

        object_type = st.radio(
            "Select Object Type",
            ["Views", "Procedures"]
        )

        if object_type == "Views":
            selected_view = st.selectbox(
                "Select a View",
                views
            )
            st.info(f"Selected View: {selected_view}")

        else:
            selected_proc = st.selectbox(
                "Select a Procedure",
                procs
            )
            st.info(f"Selected Procedure: {selected_proc}")

    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        st.stop()


    if selected_view:
        sql_text = get_object_definition(conn, selected_view)

        st.subheader(f"📝 View Summary: {selected_view}")

        if st.button("Generate View Summary"):
            summary = generate_10_point_summary(
                selected_view, "VIEW", sql_text
            )
            st.success(summary)

    if selected_proc:
        sql_text = get_object_definition(conn, selected_proc)

        st.subheader(f"📝 Procedure Summary: {selected_proc}")

        if st.button("Generate Procedure Summary"):
            summary = generate_10_point_summary(
                selected_proc, "STORED PROCEDURE", sql_text
            )
            st.success(summary)