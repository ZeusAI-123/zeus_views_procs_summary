import snowflake.connector

def get_snowflake_connection(
    account,
    user,
    password,
    warehouse,
    database,
    schema,
    role=None
):
    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )
        return conn
    except Exception as e:
        raise Exception(f"Snowflake connection failed: {e}")
