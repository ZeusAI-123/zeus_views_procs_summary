from db_connection import get_connection

conn = get_connection("localhost", "your_db", "your_user", "your_pwd")
print("DB Connected Successfully")
