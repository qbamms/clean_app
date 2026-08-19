# This file would run an end-to-end test of the MVP platform in action.
# From validating a local Birmingham city centre client to completing a transactional booking.
# (onboarding clients, managing shifts, filtering by postcode, checking out, and verifying that the booked slot is locked out.)

import os
import sys
# Get the directory of test_database.py, then go up one level to the root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add that root directory to Python's search path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from db import database
from app import engine

# Get the directory of test_database.py, then go up one level to the root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add that root directory to Python's search path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Define the folder path
output_folder = "generated"

# Check if the folder exists; if not, create it automatically
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

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

print("\n--- 🏗️ STEP 3: CLIENT PLACES SEARCH VIA APP ---")
print("🔍 Searching for cleaners in B1 for morning slot on 2026-08-15 at 09:00-11:00...")
matches = app.search_available_cleaners("B1 1AY", "2026-08-15", "09:00-11:00")
for cleaner in matches:
    print(f"👉 Available: {cleaner['name']} | Rate: £{cleaner['hourly_rate']}/hr | Phone: {cleaner['phone']}")

print("\n--- 🏗️ STEP 4: PROCESSING TRANSACTIONAL BOOKING AND SPLIT PAYOUT ---")
# Execute automated checkout
transaction = app.book_cleaning("C01", "W01", "2026-08-15", "09:00-11:00")
if transaction:
    print(f"Booking Confirmed: {transaction['booking_id']}")
    print(f"  💸 Total Paid by Client:  £{transaction['gross_amount']:.2f}")
    print(f"  🏢 App Net Platform Fee: £{transaction['platform_fee']:.2f} (20% Cut)")
    print(f"  🧹 Sent to Cleaner Bank:  £{transaction['worker_payout']:.2f}")

print("\n--- 🏗️ STEP 5: VERIFYING DOUBLE-BOOKING PROTECTION ---")
print("🔍 Searching for the exact same slot again to verify it is locked out...")
post_matches = app.search_available_cleaners("B1 1AY", "2026-08-15", "09:00-11:00")
print(f"Cleaners found for the same slot after booking: {len(post_matches)}")

# Export data to tracking ledger
ledger = app.export_ledger_csv()