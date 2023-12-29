import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

# Access environment variables for database configuration
db_username = os.getenv('DB_USERNAME', 'default_user')
db_password = os.getenv('DB_PASSWORD', 'default_password')
db_endpoint = os.getenv('DB_ENDPOINT', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

# Database URL for Async SQLAlchemy
DATABASE_URL = f'postgresql+asyncpg://{db_username}:{db_password}@{db_endpoint}:{db_port}/postgres'
DATABASE_URL_SYNC = f'postgresql://{db_username}:{db_password}@{db_endpoint}:{db_port}/postgres'


# Create Async Engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create Async Session
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Function to get a new session
@asynccontextmanager
async def async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Function to test database connection
async def test_db_connection():
    try:
        async with async_engine.connect() as conn:
            await conn.execute('SELECT 1')
        logging.info("Successfully connected to the database.")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
