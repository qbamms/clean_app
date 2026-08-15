# The SQLite Database Setup allows your application to save 
# clients, workers, and bookings locally on your machine without requiring a heavy external database server.
# Run this script once to initialize your persistent database tables, 
# automatically creating the data structure with built-in Birmingham postcode validation.

import sqlite3

def init_db():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Clients Table (Scoped to Residential Customers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        postcode TEXT NOT NULL
    );
    """)

     # 2. Workers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        worker_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        hourly_rate REAL NOT NULL
    );
    """)

    # 3. Worker Service Zones (Valid Birmingham MVP postcodes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS worker_zones (
        worker_id TEXT,
        postcode TEXT,
        PRIMARY KEY (worker_id, postcode),
        FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
    );
    """)

    # 4. Worker Availability Slots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS worker_availability (
        worker_id TEXT,
        date_str TEXT,        -- Format: YYYY-MM-DD
        time_slot TEXT,       -- Format: '09:00-11:00', '11:00-13:00', etc.
        PRIMARY KEY (worker_id, date_str, time_slot),
        FOREIGN KEY (worker_id) REFERENCES workers(worker_id) ON DELETE CASCADE
    );
    """)

    # 5. Bookings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id TEXT PRIMARY KEY,
        client_id TEXT,
        worker_id TEXT,
        date_str TEXT,
        time_slot TEXT,
        total_cost REAL,
        status TEXT DEFAULT 'Confirmed',
        FOREIGN KEY (client_id) REFERENCES clients(client_id),
        FOREIGN KEY (worker_id) REFERENCES workers(worker_id)
    );
    """)

    conn.commit()
    conn.close()
    print("💾 Database initialized successfully with MVP tables.")