def get_all_views(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sys.views
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_all_procedures(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM sys.procedures
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_object_definition(conn, object_name):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT OBJECT_DEFINITION(OBJECT_ID(?))
    """, object_name)
    row = cursor.fetchone()
    return row[0] if row else ""
