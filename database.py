import sqlite3
from contextlib import contextmanager

DATABASE = 'chat.db'

@contextmanager
def get_db():
    """Manages database connections safely (auto-commits or rollback)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows access to columns by name.
    conn.execute("PRAGMA foreign_keys = ON")    # Enable foreign keys.
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes the database by creating three tables: users, rooms, and messages."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,        
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                           
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            );
        ''')
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()