def get_sqlserver_views_and_procs(conn):
    cursor = conn.cursor()

    # Views
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.VIEWS
    """)
    views = [row[0] for row in cursor.fetchall()]

    # Stored Procedures
    cursor.execute("""
        SELECT name 
        FROM sys.procedures
    """)
    procs = [row[0] for row in cursor.fetchall()]

    return views, procs


def get_snowflake_views_and_procs(conn, database, schema):
    cursor = conn.cursor()

    # Views
    cursor.execute(f"""
        SELECT TABLE_NAME 
        FROM {database}.INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = '{schema}'
    """)
    views = [row[0] for row in cursor.fetchall()]

    # Procedures
    cursor.execute(f"""
        SELECT PROCEDURE_NAME 
        FROM {database}.INFORMATION_SCHEMA.PROCEDURES
        WHERE PROCEDURE_SCHEMA = '{schema}'
    """)
    procs = [row[0] for row in cursor.fetchall()]

    return views, procs
