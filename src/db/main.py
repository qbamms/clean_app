#  Database (db/main.py): Run this db-backend using: uvicorn main:app --reload

# src/db/main.py
import sys
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

# Dynamically calculates the absolute root folder path and injects it into Python
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# Import the sqlite3 connection setups directly from database.py
from src.db.database import init_db, get_db_connection

# Import your Marketplace core directly from your engine file
from src.db.engine import CentralBirminghamMarketplace

# Initialize the marketplace backend engine
cleaning_engine = CentralBirminghamMarketplace(db_path="postgresql+psycopg2://neondb_owner:npg_XmJVl3ZNir1b@ep-broad-star-b5rnz3ym-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

app = FastAPI(title="Cleaning Engine API")

# Initialize database schema immediately on app launch
init_db()

# ==============================================================================
# PYDANTIC SCHEMAS (Data Validation Payloads)
# ==============================================================================
class ClientRegister(BaseModel):
    client_id: str
    name: str
    email: str
    phone: Optional[str] = None
    postcode: str

class WorkerRegister(BaseModel):
    worker_id: str
    name: str
    email: str
    phone: Optional[str] = None
    hourly_rate: float
    zones: List[str]  # e.g., ["B1", "B2"]

class AvailabilitySubmit(BaseModel):
    worker_id: str
    date: str
    slots: List[str]

class BookingCreate(BaseModel):
    client_id: str
    worker_id: str
    date: str
    slot: str

# ==============================================================================
# API ROUTE ENDPOINTS
# ==============================================================================
@app.get("/")
def home():
    return {
        "status": "Online",
        "system": "Birmingham City Centre MVP Cleaning Engine",
        "documentation": "Go to /docs to test endpoints"
    }

@app.post("/clients/register")
def register_client(client: ClientRegister, db: sqlite3.Connection = Depends(get_db_connection)):
    success = cleaning_engine.register_client(
        client.client_id, client.name, client.email, client.phone, client.postcode
    )
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed. Check postcode zone constraints or email duplication.")
    return {"success": True, "message": "Client account deployed."}
   

@app.post("/workers/register")
def register_worker(worker: WorkerRegister, db: sqlite3.Connection = Depends(get_db_connection)):
    success = cleaning_engine.register_worker(
        worker.worker_id, worker.name, worker.email, worker.phone, worker.hourly_rate, worker.zones
    )
    if not success:
        raise HTTPException(status_code=400, detail="Registration rejected. Worker must service central zones (B1-B5).")
    return {"success": True, "message": "Worker profile deployed."}

@app.post("/workers/availability")
def add_availability(avail: AvailabilitySubmit, db: sqlite3.Connection = Depends(get_db_connection)):
    try:
        cleaning_engine.add_worker_availability(avail.worker_id, avail.date, avail.slots)
        return {"success": True, "message": "Calendar inventory updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cleaners/search")
def api_search_cleaners(postcode: str, date: str, slot: str):
    # Calls your engine's search method directly
    results = cleaning_engine.search_available_cleaners(postcode, date, slot)
    return results

@app.post("/bookings/create")
def api_create_booking(booking: BookingCreate):
    result = cleaning_engine.book_cleaning(
        booking.client_id, booking.worker_id, booking.date, booking.slot
    )
    if not result:
        raise HTTPException(status_code=400, detail="Transaction declined. Slot unavailable or invalid Client ID.")
    return result

@app.get("/admin/metrics")
def api_get_admin_metrics():
    conn = cleaning_engine._get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Gather Client counts and detailed data records
        cursor.execute("SELECT client_id, name, email, phone, postcode FROM clients")
        clients = [dict(row) for row in cursor.fetchall()]
        
        # 2. Gather Worker counts and detailed data records
        cursor.execute("SELECT worker_id, name, email, phone, hourly_rate FROM workers")
        workers = [dict(row) for row in cursor.fetchall()]
        
        # 3. Gather Transaction counts and detailed ledger rows
        cursor.execute("SELECT * FROM bookings")
        bookings = [dict(row) for row in cursor.fetchall()]
        
        # 4. Optional: Calculate platform-wide financial KPIs using aggregate functions
        cursor.execute("SELECT SUM(gross_amount) as total_rev, SUM(platform_fee) as platform_cut FROM bookings")
        financials = cursor.fetchone()
        total_revenue = financials["total_rev"] if financials["total_rev"] else 0.0
        platform_earnings = financials["platform_cut"] if financials["platform_cut"] else 0.0
        
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")
        
    conn.close()
    
    # Pack both the summary counts and full data dictionaries into a single JSON package
    return {
        "summary": {
            "total_clients": len(clients),
            "total_workers": len(workers),
            "total_bookings": len(bookings),
            "gross_revenue_collected": round(total_revenue, 2),
            "platform_commission_collected": round(platform_earnings, 2)
        },
        "details": {
            "clients": clients,
            "workers": workers,
            "bookings": bookings
        }
    }
