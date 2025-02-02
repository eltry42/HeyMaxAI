import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection details
DB_USER = os.getenv("POSTGRES_USER", "myuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mypassword")
DB_NAME = os.getenv("POSTGRES_DB", "heymax_db")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Establish a connection pool to PostgreSQL."""
        self.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected to PostgreSQL Database")

    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            print("Database connection closed")

    async def add_user(self, username: str, chat_id: int):
        """Insert a new user into the database."""
        query = """
        INSERT INTO Users (username, chat_id) 
        VALUES ($1, $2)
        ON CONFLICT (chat_id) DO NOTHING;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, username, chat_id)

    async def get_user(self, chat_id: int):
        """Fetch user details by chat ID."""
        query = "SELECT * FROM Users WHERE chat_id = $1;"
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, chat_id)

    async def log_interaction(self, user_id: int, command: str, response: str):
        """Log bot interactions."""
        query = """
        INSERT INTO BotInteractions (user_id, command, response) 
        VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, user_id, command, response)

    async def upvote_interaction(self, interaction_id: int):
        """Increase upvote count."""
        query = "UPDATE BotInteractions SET upvote = upvote + 1 WHERE interaction_id = $1;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, interaction_id)

    async def downvote_interaction(self, interaction_id: int):
        """Increase downvote count."""
        query = "UPDATE BotInteractions SET downvote = downvote + 1 WHERE interaction_id = $1;"
        async with self.pool.acquire() as conn:
            await conn.execute(query, interaction_id)

# Create a global database instance
db = Database()