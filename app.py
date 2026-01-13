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
st.set_page_config(
    page_title="View & Proc Analyzer",
    layout="wide"
)

st.title("📊 SQL View & Procedure Analyzer (Read-Only)")
st.info(
    "🔒 Read-only documentation tool. "
    "No SQL objects are executed or modified."
)

# =========================
# SESSION STATE INIT
# =========================
for key in ["conn", "view_doc", "proc_doc"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "conn" else ""

# =========================
# SIDEBAR – DATABASE TYPE
# =========================
st.sidebar.header("🗄️ Database Type")

db_type = st.sidebar.selectbox(
    "Select Database",
    ["SQL Server", "Snowflake"]
)

st.sidebar.divider()

# =========================
# SIDEBAR – CONNECTION DETAILS
# =========================
st.sidebar.header("🔐 Database Connection")

if db_type == "SQL Server":
    server = st.sidebar.text_input("Server Name")
    database = st.sidebar.text_input("Database Name")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

elif db_type == "Snowflake":
    account = st.sidebar.text_input("Account (e.g. ab12345.ap-south-1)")
    warehouse = st.sidebar.text_input("Warehouse")
    database = st.sidebar.text_input("Database")
    schema = st.sidebar.text_input("Schema")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

# =========================
# CONNECT BUTTON
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

        elif db_type == "Snowflake":
            conn = get_snowflake_connection(
                account.strip(),
                username.strip(),
                password.strip(),
                warehouse.strip(),
                database.strip(),
                schema.strip()
            )

        st.session_state.conn = conn
        st.sidebar.success(f"Connected to {db_type}")

    except Exception as e:
        st.sidebar.error(f"Connection failed: {e}")

# =========================
# MAIN CONTENT
# =========================
if st.session_state.conn:

    conn = st.session_state.conn
    col1, col2 = st.columns(2)

    # -------- METADATA FETCH --------
    try:
        if db_type == "SQL Server":
            views = get_all_views(conn)
            procs = get_all_procedures(conn)

        elif db_type == "Snowflake":
            views = get_all_views_sf(conn)
            procs = get_all_procedures_sf(conn)

    except Exception as e:
        st.error(f"Failed to fetch metadata: {e}")
        st.stop()

    with col1:
        selected_view = st.selectbox(
            "📄 Select a View",
            [""] + views,
            key="view_select"
        )

    with col2:
        selected_proc = st.selectbox(
            "⚙️ Select a Stored Procedure",
            [""] + procs,
            key="proc_select"
        )

    # =========================
    # VIEW DOCUMENTATION
    # =========================
    if selected_view:
        if db_type == "SQL Server":
            sql_text = get_object_definition(conn, selected_view)
        else:
            sql_text = get_object_definition_sf(conn, selected_view, "view")

        st.subheader(f"📝 View Documentation: {selected_view}")

        if st.button("Generate View Documentation", key="gen_view"):
            with st.spinner("Generating view documentation..."):
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
                f"{selected_view}_VIEW_documentation.txt",
                "text/plain"
            )

    # =========================
    # PROCEDURE DOCUMENTATION
    # =========================
    if selected_proc:
        if db_type == "SQL Server":
            sql_text = get_object_definition(conn, selected_proc)
        else:
            sql_text = get_object_definition_sf(conn, selected_proc, "procedure")

        st.subheader(f"📝 Procedure Documentation: {selected_proc}")

        if st.button("Generate Procedure Documentation", key="gen_proc"):
            with st.spinner("Generating procedure documentation..."):
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
                f"{selected_proc}_PROCEDURE_documentation.txt",
                "text/plain"
            )
