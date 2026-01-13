import streamlit as st

# =========================
# SQL Server imports
# =========================
from db_connection import get_connection as get_sqlserver_connection
from metadata_reader import (
    get_all_views,
    get_all_procedures,
    get_object_definition
)

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
# PAGE CONFIG
# =========================
st.set_page_config(page_title="View & Proc Analyzer", layout="wide")

st.title("📊 SQL View & Procedure Analyzer (Read-Only)")
st.info("🔒 Read-only tool. No database objects are modified or executed.")

# =========================
# SESSION STATE INIT
# =========================
for key in ["conn", "view_doc", "proc_doc", "last_db_type", "last_sf_context"]:
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

# 🔥 Reset connection if DB type changes
if st.session_state.last_db_type and st.session_state.last_db_type != db_type:
    st.session_state.conn = None
st.session_state.last_db_type = db_type

st.sidebar.divider()
st.sidebar.header("🔐 Database Connection")

# =========================
# CONNECTION INPUTS
# =========================
if db_type == "SQL Server":
    server = st.sidebar.text_input("Server")
    database = st.sidebar.text_input("Database")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

elif db_type == "Snowflake":
    account = st.sidebar.text_input("Account (e.g. ab12345.ap-south-1)")
    warehouse = st.sidebar.text_input("Warehouse")
    database = st.sidebar.text_input("Database")
    schema = st.sidebar.text_input("Schema")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    # 🔥 Reset Snowflake connection if DB or schema changes
    sf_key = f"{account}_{database}_{schema}"
    if st.session_state.last_sf_context and st.session_state.last_sf_context != sf_key:
        st.session_state.conn = None
    st.session_state.last_sf_context = sf_key

# =========================
# CONNECT
# =========================
if st.sidebar.button("Connect"):
    try:
        if db_type == "SQL Server":
            conn = get_sqlserver_connection(
                server.strip(),
                database.strip(),
                username.strip(),
                password.strip()
            )

        else:
            conn = get_snowflake_connection(
                account.strip(),
                username.strip(),
                password.strip(),
                warehouse.strip(),
                database.strip(),
                schema.strip()
            )

            # 🔥 HARD RESET CONTEXT (VERY IMPORTANT)
            cursor = conn.cursor()
            cursor.execute(f"USE DATABASE {database}")
            cursor.execute(f"USE SCHEMA {schema}")
            cursor.close()

        st.session_state.conn = conn
        st.sidebar.success(f"Connected to {db_type}")

    except Exception as e:
        st.sidebar.error(str(e))

# =========================
# MAIN UI
# =========================
if st.session_state.conn:

    conn = st.session_state.conn
    col1, col2 = st.columns(2)

    try:
        if db_type == "SQL Server":
            views = get_all_views(conn)
            procs = get_all_procedures(conn)
        else:
            views = get_all_views_sf(conn)
            procs = get_all_procedures_sf(conn)
    except Exception as e:
        st.error(f"Failed to fetch metadata: {e}")
        st.stop()

    with col1:
        selected_view = st.selectbox("📄 Select a View", [""] + views)

    with col2:
        selected_proc = st.selectbox("⚙️ Select a Stored Procedure", [""] + procs)

    # =========================
    # VIEW DOC
    # =========================
    if selected_view:
        sql_text = (
            get_object_definition(conn, selected_view)
            if db_type == "SQL Server"
            else get_object_definition_sf(conn, selected_view, "view")
        )

        st.subheader(f"📝 View Documentation: {selected_view}")

        if st.button("Generate View Documentation"):
            st.session_state.view_doc = generate_sql_documentation(
                selected_view, "view", sql_text
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
    # PROC DOC
    # =========================
    if selected_proc:
        sql_text = (
            get_object_definition(conn, selected_proc)
            if db_type == "SQL Server"
            else get_object_definition_sf(conn, selected_proc, "procedure")
        )

        st.subheader(f"📝 Procedure Documentation: {selected_proc}")

        if st.button("Generate Procedure Documentation"):
            st.session_state.proc_doc = generate_sql_documentation(
                selected_proc, "procedure", sql_text
            )

        if st.session_state.proc_doc:
            st.markdown(st.session_state.proc_doc)
            st.download_button(
                "⬇️ Download Procedure Documentation (TXT)",
                st.session_state.proc_doc,
                f"{selected_proc}_PROCEDURE.txt",
                "text/plain"
            )
