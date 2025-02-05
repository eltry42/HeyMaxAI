import os
import psycopg2
from psycopg2 import sql

# Database connection details
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

db = None

def setup_db():
    global db
    db = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def shutdown_db():
    db.close()

def get_messages(keywords, offset):
    cursor = db.cursor()
    query = sql.SQL("""
        SELECT * FROM scrapedmessages
        WHERE content ILIKE ALL(%s)
        ORDER BY posted_at DESC
        OFFSET %s LIMIT 1;
        """)
    cursor.execute(query, (keywords, offset))
    result = cursor.fetchone()
    cursor.close()
    return result[2] if result else None
