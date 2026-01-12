import pyodbc

def get_connection(server, database, username, password):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")
