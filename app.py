import streamlit as st
import requests

# =========================
# Snowflake imports
# =========================
from snowflakeconnector import get_snowflake_connection
from snowflake_metadata_reader import (
    get_all_views_sf,
    get_all_procedures_sf,
    get_object_definition_sf
)

from llm_summary import generate_sql_documentation

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="View & Proc Analyzer", layout="wide")

st.title("📊 SQL View & Procedure Analyzer (Read-Only)")
st.info(
    "🔒 Read-only documentation tool. "
    "No SQL objects are executed or modified."
)

# =========================
# SQL SERVER BACKEND API
# =========================
# 👉 Replace this with your backend URL
SQLSERVER_API_BASE = "http://YOUR_BACKEND_IP:8000"

def get_sqlserver_views_api():
    return requests.get(f"{SQLSERVER_API_BASE}/views").json()

def get_sqlserver_procs_api():
    return requests.get(f"{SQLSERVER_API_BASE}/procedures").json()

def get_sqlserver_definition_api(object_name):
    resp = requests.get(
        f"{SQLSERVER_API_BASE}/definition",
        params={"object_name": object_name}
    )
    return resp.json().get("definition", "")

# =========================
# SESSION STATE
# =========================
for key in ["conn", "view_doc", "proc_doc"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "conn" else ""

# =========================
# SIDEBAR – DB TYPE
# =========================
st.sidebar.header("🗄️ Database Type")

db_type = st.sidebar.selectbox(
    "Select Database",
    ["SQL Server", "Snowflake"]
)

st.sidebar.divider()
st.sidebar.header("🔐 Database Connection")

# =========================
# CONNECTION INPUTS
# =========================
if db_type == "Snowflake":
    account = st.sidebar.text_input("Account (e.g. ab12345.ap-south-1)")
    warehouse = st.sidebar.text_input("Warehouse")
    database = st.sidebar.text_input("Database")
    schema = st.sidebar.text_input("Schema")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

else:
    st.sidebar.info(
        "ℹ️ SQL Server is accessed via a secured backend service.\n\n"
        "No direct DB connection is made from Streamlit Cloud."
    )

# =========================
# CONNECT
# =========================
if st.sidebar.button("Connect"):
    try:
        if db_type == "Snowflake":
            conn = get_snowflake_connection(
                account.strip(),
                username.strip(),
                password.strip(),
                warehouse.strip(),
                database.strip(),
                schema.strip()
            )

            # Set Snowflake context
            cursor = conn.cursor()
            cursor.execute(f"USE DATABASE {database}")
            cursor.execute(f"USE SCHEMA {schema}")
            cursor.close()

            st.session_state.conn = conn
            st.sidebar.success("Connected to Snowflake")

        else:
            # SQL Server uses backend API – no DB connection here
            st.session_state.conn = "SQLSERVER_API"
            st.sidebar.success("Connected to SQL Server (via backend API)")

    except Exception as e:
        st.sidebar.error(str(e))

# =========================
# MAIN CONTENT
# =========================
if st.session_state.conn:

    col1, col2 = st.columns(2)

    # =========================
    # FETCH METADATA
    # =========================
    try:
        if db_type == "Snowflake":
            views = get_all_views_sf(st.session_state.conn)
            procs = get_all_procedures_sf(st.session_state.conn)
        else:
            views = get_sqlserver_views_api()
            procs = get_sqlserver_procs_api()

    except Exception as e:
        st.error(f"Failed to fetch metadata: {e}")
        st.stop()

    with col1:
        selected_view = st.selectbox("📄 Select a View", [""] + views)

    with col2:
        selected_proc = st.selectbox("⚙️ Select a Stored Procedure", [""] + procs)

    # =========================
    # VIEW DOCUMENTATION
    # =========================
    if selected_view:
        if db_type == "Snowflake":
            sql_text = get_object_definition_sf(
                st.session_state.conn,
                selected_view,
                "view"
            )
        else:
            sql_text = get_sqlserver_definition_api(selected_view)

        st.subheader(f"📝 View Documentation: {selected_view}")

        if st.button("Generate View Documentation"):
            with st.spinner("Generating documentation..."):
                st.session_state.view_doc = generate_sql_documentation(
                    selected_view,
                    "view",
                    sql_text
                )

        if st.session_state.view_doc:
            st.markdown(st.session_state.view_doc)
            st.download_button(
                "⬇️ Download View Documentation (TXT)",
                st.session_state.view_doc,
                f"{selected_view}_VIEW.txt",
                "text/plain"
            )

    # =========================
    # PROCEDURE DOCUMENTATION
    # =========================
    if selected_proc:
        if db_type == "Snowflake":
            sql_text = get_object_definition_sf(
                st.session_state.conn,
                selected_proc,
                "procedure"
            )
        else:
            sql_text = get_sqlserver_definition_api(selected_proc)

        st.subheader(f"📝 Procedure Documentation: {selected_proc}")

        if st.button("Generate Procedure Documentation"):
            with st.spinner("Generating documentation..."):
                st.session_state.proc_doc = generate_sql_documentation(
                    selected_proc,
                    "procedure",
                    sql_text
                )

        if st.session_state.proc_doc:
            st.markdown(st.session_state.proc_doc)
            st.download_button(
                "⬇️ Download Procedure Documentation (TXT)",
                st.session_state.proc_doc,
                f"{selected_proc}_PROCEDURE.txt",
                "text/plain"
            )
