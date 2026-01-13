def get_all_views_sf(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = CURRENT_SCHEMA()
            ORDER BY table_name
        """)
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()


def get_all_procedures_sf(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT procedure_name
            FROM information_schema.procedures
            WHERE procedure_schema = CURRENT_SCHEMA()
            ORDER BY procedure_name
        """)
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()


def get_object_definition_sf(conn, object_name, object_type):
    cursor = conn.cursor()
    try:
        if object_type.lower() == "view":
            cursor.execute(f"SHOW VIEWS LIKE '{object_name}'")
            row = cursor.fetchone()
            return row[6] if row else ""

        elif object_type.lower() == "procedure":
            cursor.execute(f"SHOW PROCEDURES LIKE '{object_name}'")
            row = cursor.fetchone()
            return row[7] if row else ""

        return ""
    finally:
        cursor.close()
