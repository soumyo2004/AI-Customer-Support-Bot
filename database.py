import sqlite3
import os

DATABASE_FILE = 'chatbot_support.db'

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'bot'
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        );
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_FILE}")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# Initialize the database when the module is imported or run directly
if __name__ == '__main__':
    init_db()
