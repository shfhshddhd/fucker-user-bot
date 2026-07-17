import sqlite3
import os
import threading

DB_PATH = "database/fucker_bot.db"

# Thread lock for database writes
_db_lock = threading.Lock()

def get_connection():
    """Get database connection with WAL mode and timeout"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    
    # Enable WAL mode for concurrent reads/writes
    conn.execute("PRAGMA journal_mode=WAL")
    
    # Set busy timeout (ms)
    conn.execute("PRAGMA busy_timeout=30000")
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys=ON")
    
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table - hosted accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone TEXT,
            session_string TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Targets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_user_id INTEGER,
            target_user_id INTEGER,
            target_username TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (host_user_id) REFERENCES users(user_id)
        )
    """)
    
    # Groups table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_user_id INTEGER,
            group_id INTEGER,
            group_title TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (host_user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()

# --- User functions ---

def add_user(user_id, phone, session_string):
    """Add a new user"""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, phone, session_string) VALUES (?, ?, ?)",
            (user_id, phone, session_string)
        )
        conn.commit()
        conn.close()

def get_user(user_id):
    """Get user by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    """Get all active users"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_active = 1")
    users = cursor.fetchall()
    conn.close()
    return users

def remove_user(user_id):
    """Remove user and their targets"""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        # Delete user's targets first
        cursor.execute("DELETE FROM targets WHERE host_user_id = ?", (user_id,))
        # Delete user's groups
        cursor.execute("DELETE FROM groups WHERE host_user_id = ?", (user_id,))
        # Delete user
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

# --- Target functions ---

def add_target(host_user_id, target_user_id, target_username):
    """Add a target for a host"""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO targets (host_user_id, target_user_id, target_username) VALUES (?, ?, ?)",
            (host_user_id, target_user_id, target_username)
        )
        conn.commit()
        conn.close()

def remove_target(host_user_id, target_identifier):
    """Remove target by username or user_id"""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Try by username first (remove @ if present)
        target_clean = target_identifier.lstrip('@')
        cursor.execute(
            "DELETE FROM targets WHERE host_user_id = ? AND target_username = ?",
            (host_user_id, target_clean)
        )
        
        # If nothing deleted, try by user_id
        if cursor.rowcount == 0 and target_identifier.isdigit():
            cursor.execute(
                "DELETE FROM targets WHERE host_user_id = ? AND target_user_id = ?",
                (host_user_id, int(target_identifier))
            )
        
        conn.commit()
        conn.close()

def get_targets(host_user_id):
    """Get all targets for a specific host"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets WHERE host_user_id = ?", (host_user_id,))
    targets = cursor.fetchall()
    conn.close()
    return targets

def get_all_targets():
    """Get ALL targets from all hosts"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets")
    targets = cursor.fetchall()
    conn.close()
    return targets
