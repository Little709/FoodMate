from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2 import sql
import os

# Environment variables for database configuration
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "password")
DATABASE_IP = os.getenv("DATABASE_IP", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "chats")

# Default database for creating the target database
DEFAULT_DB = "postgres"

# Function to ensure the target database exists
def ensure_database_exists():
    try:
        # Connect to the default database
        conn = psycopg2.connect(
            dbname=DEFAULT_DB,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_IP,
            port=DATABASE_PORT,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [DATABASE_NAME],
        )
        exists = cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DATABASE_NAME)
                )
            )
            print(f"Database '{DATABASE_NAME}' created successfully.")
        else:
            print(f"Database '{DATABASE_NAME}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error ensuring database exists: {e}")

# Call the function before setting up the SQLAlchemy engine
ensure_database_exists()

# SQLAlchemy database URL
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_IP}:{DATABASE_PORT}/{DATABASE_NAME}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
