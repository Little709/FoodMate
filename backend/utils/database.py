from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sql
import psycopg2
from dotenv import load_dotenv
import logging
import json
import asyncpg
from fastapi import WebSocket
from typing import Dict

# Setup Logging
logger = logging.getLogger("uvicorn")

# Load environment variables
load_dotenv()

# General database configuration
general_db_config = {
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "password"),
    "host": os.getenv("DATABASE_IP", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "name": os.getenv("GENERAL_DATABASE_NAME", "general"),
}

general_db_url = (
    f"postgresql://{general_db_config['user']}:{general_db_config['password']}"
    f"@{general_db_config['host']}:{general_db_config['port']}/{general_db_config['name']}"
)

# Chat database configuration
chat_db_config = {
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "password"),
    "host": os.getenv("DATABASE_IP", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "name": os.getenv("CHAT_DATABASE_NAME", "chats"),
}

chat_db_url = (
    f"postgresql://{chat_db_config['user']}:{chat_db_config['password']}"
    f"@{chat_db_config['host']}:{chat_db_config['port']}/{chat_db_config['name']}"
)

# Chat database configuration
recipe_db_config = {
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "password"),
    "host": os.getenv("DATABASE_IP", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
    "name": "recipes"
}

recipe_db_url = (
    f"postgresql://{chat_db_config['user']}:{chat_db_config['password']}"
    f"@{chat_db_config['host']}:{chat_db_config['port']}/{chat_db_config['name']}"
)

# Base for models
Base = declarative_base()

# Helper functions to ensure database existence
def ensure_database_exists(db_config):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"],
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the target database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            [db_config["name"]],
        )
        exists = cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cursor.execute(f"CREATE DATABASE {db_config['name']}")
            logger.info(f"Database '{db_config['name']}' created successfully.")
        else:
            logger.info(f"Database '{db_config['name']}' already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error ensuring database '{db_config['name']}' exists: {e}")

# Ensure both databases exist
ensure_database_exists(general_db_config)
ensure_database_exists(chat_db_config)
ensure_database_exists(recipe_db_config)

# SQLAlchemy session setup
general_engine = create_engine(general_db_url)
general_session = sessionmaker(autocommit=False, autoflush=False, bind=general_engine)

chat_engine = create_engine(chat_db_url)
chat_session = sessionmaker(autocommit=False, autoflush=False, bind=chat_engine)

recipe_engine = create_engine(recipe_db_url)
recipe_session = sessionmaker(autocommit=False, autoflush=False, bind=recipe_engine)

# Notification manager for chat database
class NotificationManager:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection = None
        self.listeners: Dict[str, WebSocket] = {}

    async def connect(self):
        try:
            logger.info("Attempting to connect to PostgreSQL...")
            self.connection = await asyncpg.connect(self.dsn)
            await self.connection.add_listener('new_message', self.notification_handler)
            logger.info("Successfully connected to PostgreSQL and added notification listener.")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.connection = None

    async def notification_handler(self, connection, pid, channel, payload):
        try:
            message_id, chat_id = payload.split(':')
            logger.info(f"New message in chat {chat_id} with ID: {message_id}")
            if chat_id in self.listeners:
                for websocket in self.listeners[chat_id]:
                    await websocket.send_text(json.dumps({"message_id": message_id, "chat_id": chat_id}))
        except Exception as e:
            logger.error(f"Error handling notification: {e}")

    def register_listener(self, chat_id: str, websocket: WebSocket):
        if chat_id not in self.listeners:
            self.listeners[chat_id] = []
        self.listeners[chat_id].append(websocket)

    def unregister_listener(self, chat_id: str, websocket: WebSocket):
        if chat_id in self.listeners:
            self.listeners[chat_id].remove(websocket)
            if not self.listeners[chat_id]:
                del self.listeners[chat_id]

# Initialize NotificationManager for chat database
notification_manager = NotificationManager(dsn=chat_db_url)

async def start_listening():
    await notification_manager.connect()
