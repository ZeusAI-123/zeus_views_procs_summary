def get_impacted_views(conn, table_name):
    query = f"""
    SELECT name
    FROM sys.views
    WHERE OBJECT_DEFINITION(object_id) LIKE '%{table_name}%'
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]


def get_impacted_procedures(conn, table_name):
    query = f"""
    SELECT name
    FROM sys.procedures
    WHERE OBJECT_DEFINITION(object_id) LIKE '%{table_name}%'
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return [row[0] for row in cursor.fetchall()]
