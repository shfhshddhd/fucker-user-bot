import sqlite3
import os

DB_PATH = "database/fucker_bot.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
    
    # Groups table - jahan auto-tag kaam karega
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, phone, session_string) VALUES (?, ?, ?)",
        (user_id, phone, session_string)
    )
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_active = 1")
    users = cursor.fetchall()
    conn.close()
    return users

def remove_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- Target functions ---
def add_target(host_user_id, target_user_id, target_username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO targets (host_user_id, target_user_id, target_username) VALUES (?, ?, ?)",
        (host_user_id, target_user_id, target_username)
    )
    conn.commit()
    conn.close()

def remove_target(host_user_id, target_identifier):
    conn = get_connection()
    cursor = conn.cursor()
    # Try by username first, then by user_id
    cursor.execute(
        "DELETE FROM targets WHERE host_user_id = ? AND (target_username = ? OR target_user_id = ?)",
        (host_user_id, target_identifier, int(target_identifier) if target_identifier.isdigit() else 0)
    )
    conn.commit()
    conn.close()

def get_targets(host_user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets WHERE host_user_id = ?", (host_user_id,))
    targets = cursor.fetchall()
    conn.close()
    return targets

def get_all_targets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targets")
    targets = cursor.fetchall()
    conn.close()
    return targets
