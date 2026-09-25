import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def get_db_connection():
    """Establece una conexión asíncrona con PostgreSQL."""
    return await asyncpg.connect(DATABASE_URL)
