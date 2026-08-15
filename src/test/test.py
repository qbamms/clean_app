# This file would run an end-to-end test of the MVP platform in action.
# From validating a local Birmingham client to completing a transactional booking.

import os
import sys
# 1. Get the directory of test_database.py, then go up one level to the root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Add that root directory to Python's search path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
from db import database
from app import engine

# Reset database for clean simulation deployment
if os.path.exists("marketplace.db"):
    os.remove("marketplace.db")

# Initialize Database Architecture
database.init_db()

# Launch the Engine
app = engine.CentralBirminghamMarketplace()

print("\n--- 🏗️ STEP 1: REGISTERING CENTRAL BIRMINGHAM CLIENTS ---")
# Success: B1 is inside the city centre
app.register_client("C01", "James Cook", "james.b1@mail.co.uk", "07712345678", "B1 1AY") 
# Rejection: B74 (Sutton Coldfield) is outside the MVP zone
app.register_client("C02", "Sarah Smith", "sarah@mail.com", "07788899911", "B74 2ET") 

print("\n--- 🏗️ STEP 2: REGISTERING CLEANERS & SETTING AVAILABILITY ---")
# Cleaner covers modern central blocks (B1, B2, B3)
app.register_worker("W01", "Amara Adebayo", "amara@bhmclean.co.uk", "07700900123", hourly_rate=18.50, covered_zones=["B1", "B2", "B3"])
# Set up calendar windows
app.add_worker_availability("W01", "2026-08-15", ["09:00-11:00", "11:00-13:00"])

print("\n--- 🏗️ STEP 3: SEARCHING AVAILABILITY IN REAL-TIME ---")
print("🔍 Searching for cleaners in B1 for morning slot on 2026-08-15...")
matches = app.search_available_cleaners("B1 1AY", "2026-08-15", "09:00-11:00")
for cleaner in matches:
    print(f"👉 Available: {cleaner['name']} | Rate: £{cleaner['hourly_rate']}/hr | Phone: {cleaner['phone']}")

print("\n--- 🏗️ STEP 4: PROCESSING TRANSACTIONAL BOOKING ---")
# Execute automated checkout
booking_id = app.book_cleaning("C01", "W01", "2026-08-15", "09:00-11:00")

print("\n--- 🏗️ STEP 5: VERIFYING INVENTORY PROTECTION ---")
print("🔍 Searching for the exact same slot again to verify it is locked out...")
post_matches = app.search_available_cleaners("B1 1AY", "2026-08-15", "09:00-11:00")
print(f"👉 Matching cleaners found: {len(post_matches)}")
