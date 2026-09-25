# The Persistent SQLite Database Setup allows your application to save 
# clients, workers, and bookings locally on your machine without requiring a heavy external database server.
# Run this script once to initialize your persistent database tables, 
# automatically creating the data structure with built-in Birmingham postcode validation.
# It enforces foreign key constraints to ensure that deleting a worker automatically 
# clears their listed service postcodes and available time slots.

import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Best practice: Use an environment variable, fall back to the string if testing locally
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_XmJVl3ZNir1b@ep-broad-star-b5rnz3ym-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

# Start the engine (Postgres does not need the sqlite connect_args)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def init_db():
#     conn = sqlite3.connect(DATABASE_URL)
#     cursor = conn.cursor()

#     # Enable foreign keys and enforce database integrity rules
#     cursor.execute("PRAGMA foreign_keys = ON;")

#     # 1. Clients Table (Scoped to Residential Homeowners/Renters only for MVP)
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS clients (
#         client_id TEXT PRIMARY KEY,
#         name TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         phone TEXT NOT NULL,
#         postcode TEXT NOT NULL
#     );
#     """)

#      # 2. Cleaners/Workers Table
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS workers (
#         worker_id TEXT PRIMARY KEY,
#         name TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         phone TEXT NOT NULL,
#         hourly_rate REAL NOT NULL
#     );
#     """)

#     # 3. Worker Service Zones Table (Valid Birmingham MVP postcodes)
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS worker_zones (
#         worker_id TEXT,
#         postcode TEXT,
#         PRIMARY KEY (worker_id, postcode),
#         FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
#     );
#     """)

#     # 4. Worker Availability Slots Table
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS worker_availability (
#         worker_id TEXT,
#         date_str TEXT,        -- Format: YYYY-MM-DD
#         time_slot TEXT,       -- Format: '09:00-11:00', '11:00-13:00', etc.
#         PRIMARY KEY (worker_id, date_str, time_slot),
#         FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
#     );
#     """)

#     # 5. Financial Ledger & Bookings Table
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS bookings (
#         booking_id TEXT PRIMARY KEY,
#         client_id TEXT,
#         worker_id TEXT,
#         date_str TEXT,
#         time_slot TEXT,
#         gross_amount REAL,
#         platform_fee REAL,
#         worker_payout REAL,
#         status TEXT DEFAULT 'Confirmed',
#         FOREIGN KEY (client_id) REFERENCES clients(client_id),
#         FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
#     );
#     """)

#     conn.commit()
#     conn.close()
#     print("💾 Persistent SQLite database initialized successfully for Birmingham city centre MVP.")

# if __name__ == "__main__":
#     init_db()

# def get_db_connection():
#     """Yields a safe connection context for FastAPI routes."""
#     conn = sqlite3.connect(DATABASE_URL)
#     # This magic line changes database rows from tuples () into dictionary keys []
#     conn.row_factory = sqlite3.Row 
#     try:
#         yield conn
#     finally:
#         conn.close()