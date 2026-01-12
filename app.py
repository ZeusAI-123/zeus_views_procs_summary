import streamlit as st
from db_connection import get_connection
from metadata_reader import (
    get_all_views,
    get_all_procedures,
    get_object_definition
)
from llm_summary import generate_sql_documentation  # ✅ FIXED IMPORT

st.set_page_config(page_title="View & Proc Analyzer", layout="wide")

st.title("📊 SQL Server View & Procedure Analyzer (Read-Only)")

# =========================
# SIDEBAR – DB CONNECTION
# =========================
st.sidebar.header("🔐 Database Connection")

server = st.sidebar.text_input("Server Name")
database = st.sidebar.text_input("Database Name")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Connect"):

    if not all([server, database, username, password]):
        st.sidebar.error("Fill all connection details")
    else:
        try:
            conn = get_connection(server, database, username, password)
            st.session_state.conn = conn
            st.sidebar.success("Connected successfully")
        except Exception as e:
            st.sidebar.error(str(e))

# =========================
# MAIN CONTENT
# =========================
if "conn" in st.session_state:

    conn = st.session_state.conn

    col1, col2 = st.columns(2)

    with col1:
        views = get_all_views(conn)
        selected_view = st.selectbox("📄 Select a View", [""] + views)

    with col2:
        procs = get_all_procedures(conn)
        selected_proc = st.selectbox("⚙️ Select a Stored Procedure", [""] + procs)

    # -------- VIEW DOCUMENTATION --------
    if selected_view:
        sql_text = get_object_definition(conn, selected_view)

        st.subheader(f"📝 View Documentation: {selected_view}")

        if st.button("Generate View Documentation"):
            with st.spinner("Generating documentation..."):
                summary = generate_sql_documentation(
                    selected_view,
                    "view",
                    sql_text
                )
            st.success("Documentation generated successfully")
            st.markdown(summary)

    # -------- PROCEDURE DOCUMENTATION --------
    if selected_proc:
        sql_text = get_object_definition(conn, selected_proc)

        st.subheader(f"📝 Procedure Documentation: {selected_proc}")

        if st.button("Generate Procedure Documentation"):
            with st.spinner("Generating documentation..."):
                summary = generate_sql_documentation(
                    selected_proc,
                    "procedure",
                    sql_text
                )
            st.success("Documentation generated successfully")
            st.markdown(summary)
