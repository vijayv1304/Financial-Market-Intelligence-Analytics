
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(dotenv_path=".env")

try:
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=10
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user;")
        database, user = cursor.fetchone()

        print("Connection Status: SUCCESS")
        print("Database:", database)
        print("User:", user)

    connection.close()

except Exception as error:
    print("Connection Status: FAILED")
    print("Error Type:", type(error).__name__)
    print("Error:", str(error).splitlines()[0])
