import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = 'localhost'
DB_PORT = 5433
DB_NAME = 'heymax_db'
DB_USER = 'myuser'
DB_PASSWORD = 'mypassword'

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def insert_user(username, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        INSERT INTO Users (username, chat_id)
        VALUES (%s, %s)
        ON CONFLICT (chat_id) DO UPDATE SET last_active = CURRENT_TIMESTAMP;
    """)
    cursor.execute(query, (username, chat_id))
    conn.commit()
    cursor.close()
    conn.close()

def insert_channel(name, scrape_status=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = sql.SQL("""
        INSERT INTO Channels (name, scrape_status)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING;
    """)

    try:
        cursor.execute(query, (name, scrape_status))
        conn.commit()
        print(f"Inserted channel: {name}")
    except Exception as e:
        print(f"Channel Insert Error: {e}")

    cursor.close()
    conn.close()

def insert_scraped_message(channel_id, content, posted_at, media_url=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sql.SQL("""
        INSERT INTO ScrapedMessages (channel_id, content, media_url, posted_at)
        VALUES (%s, %s, %s, %s)
    """)

    try:
        cursor.execute(query, (channel_id, content, media_url, posted_at))
        conn.commit()
        print(f"Inserted message into DB: {content[:50]}...")  # Print first 50 chars
    except Exception as e:
        print(f"DB Insert Error: {e}")
    
    cursor.close()
    conn.close()


def insert_bot_interaction(user_id, command, response, upvote=0, downvote=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("""
        INSERT INTO BotInteractions (user_id, command, response, upvote, downvote)
        VALUES (%s, %s, %s, %s, %s)
    """)
    cursor.execute(query, (user_id, command, response, upvote, downvote))
    conn.commit()
    cursor.close()
    conn.close()

def get_channel_id(channel_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = sql.SQL("SELECT channel_id FROM Channels WHERE name = %s;")
    cursor.execute(query, (channel_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        print(f"Channel ID for {channel_name}: {result[0]}")
    else:
        print(f"Channel {channel_name} not found in DB!")

    return result[0] if result else None
