import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Optional
from config import DATABASE_NAME

def get_connection():
    """Create and return a database connection"""
    try:
        return sqlite3.connect(DATABASE_NAME)
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def init_sample_reports():
    """Initialize sample reports for testing"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Sample reports for each category
        sample_reports = [
            ("FinTech", "2024 FinTech Market Analysis", "McKinsey Global", "fintech_report_2024.pdf"),
            ("FinTech", "Digital Banking Trends 2025", "Deloitte", "digital_banking_2025.pdf"),
            ("Automotive", "EV Market Report 2024", "Bloomberg", "ev_market_2024.pdf"),
            ("Automotive", "Future of Autonomous Vehicles", "Forbes", "autonomous_vehicles.pdf"),
            ("Retail", "E-commerce Trends 2025", "eMarketer", "ecommerce_2025.pdf"),
            ("Retail", "Digital Retail Innovation", "Gartner", "retail_innovation.pdf")
        ]

        cursor.execute("DELETE FROM reports")  # Clear existing sample reports
        cursor.executemany(
            "INSERT INTO reports (category, title, source, file_path) VALUES (?, ?, ?, ?)",
            sample_reports
        )

        conn.commit()
        logging.info("Sample reports initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing sample reports: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize database and create required tables"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                website TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
        ''')

        conn.commit()

        # Initialize sample reports after creating tables
        init_sample_reports()

    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise
    finally:
        if conn:
            conn.close()

def add_user(user_id: int, category: str, description: str, website: str) -> bool:
    """Add or update user profile"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, category, description, website)
            VALUES (?, ?, ?, ?)
        ''', (user_id, category, description, website))

        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error adding user: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_users() -> List[Tuple]:
    """Retrieve all registered users"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_reports(category: str) -> List[Tuple]:
    """Retrieve reports for a specific category"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, source, file_path FROM reports WHERE category=?",
            (category,)
        )
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error getting reports: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user(user_id: int) -> Optional[Tuple]:
    """Retrieve user by ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        return None
    finally:
        if conn:
            conn.close()