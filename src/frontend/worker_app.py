# To convert the central Birmingham cleaning engine into an interactive web prototype, 
# Streamlit library would be use.
# This code would run a Worker Booking App Dashboard.
# Worker Dashboard (frontend/worker_app.py): Run this app using: streamlit run frontend/worker_app.py --server.port 8502

import streamlit as st
import os
import requests
from datetime import date
import sys

# Get the directory of test_database.py, then go up one level to the root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add that root directory to Python's search path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from db import database

# Point this directly to your running FastAPI server
API_URL = "http://127.0.0.1:8000"

# Ensure database file exists on boot
if not os.path.exists("cleaning_engine.db"):
    database.init_db()

# Page layout configurations
st.set_page_config(
    page_title="BrumClean MVP Portal", 
    page_icon="🧹", 
    layout="wide"
)

st.title("🧹 BrumClean Marketplace Prototype")
st.caption("📍 Serving Postcodes: B1, B2, B3, B4, B5 (Birmingham City Centre Only)")
st.set_page_config(page_title="Cleaner Onboarding & Schedule Engine", layout="wide")
st.header("Cleaner Registration & Onboarding Engine")
worker_column1, worker_column2 = st.columns([1, 2], gap="large")

with worker_column1:
    st.subheader("📋 Step 1: Join Platform Network")
    with st.form("worker_reg_form", clear_on_submit=True):
        worker_id = st.text_input("Worker Reference ID (e.g., W201)")
        worker_name = st.text_input("Full Professional Name")
        worker_email = st.text_input("Direct Email")
        worker_phone = st.text_input("Mobile Number")
        worker_rate = st.number_input("Your Custom Base Hourly Rate (£)", min_value=12.00, value=17.50, step=0.50)

        st.markdown("**Select Service Sectors You Cover:**")
        zone_b1 = st.checkbox("B1 (Broad St / Bullring / Jewel Quarter)")
        zone_b2 = st.checkbox("B2 (New Street Centre)")
        zone_b3 = st.checkbox("B3 (Colmore Row / Financial District)")
        zone_b4 = st.checkbox("B4 (Corporation St / Aston Univ)")
        zone_b5 = st.checkbox("B5 (Digbeth / Chinese Quarter)")

        submit_worker = st.form_submit_button("Submit Application")
        if submit_worker:
            zones = []
            if zone_b1: zones.append("B1")
            if zone_b2: zones.append("B2")
            if zone_b3: zones.append("B3")
            if zone_b4: zones.append("B4")
            if zone_b5: zones.append("B5")
        
            if not (worker_id and worker_name and worker_email and zones):
                st.error("Please fill out your identity fields and select at least one central delivery postcode.")
            else:
                # Decoupled Action: Network registration payload
                worker_payload = {
                    "worker_id": worker_id, "name": worker_name, "email": worker_email,
                    "phone": worker_phone, "hourly_rate": worker_rate, "zones": zones
                }
                try:
                    response = requests.post(f"{API_URL}/workers/register", json=worker_payload)
                    if response.status_code == 200:
                        st.success(f"Welcome to the team, {worker_name}! Profile successfully deployed to database.")
                    else:
                        st.error("Registration failed. Ensure your Worker ID or email is unique.")
                except requests.exceptions.ConnectionError:
                    st.error("Network connection refused by API server core.")

    with worker_column2:
        st.subheader("📅 Step 2: Open Shift Inventory Hours")
        with st.form("shift_form", clear_on_submit=True):
            active_worker_id = st.text_input("Enter Your Worker Reference ID to Add Hours")
            shift_date = st.date_input("Available Working Date", min_value=date.today(), key="shift_date")
            
            st.markdown("**Check the 2-Hour Blocks You Want to Open to Public Market:**")
            slot_1 = st.checkbox("Morning Slot (09:00 - 11:00)")
            slot_2 = st.checkbox("Midday Slot (11:00 - 13:00)")
            slot_3 = st.checkbox("Afternoon Slot (14:00 - 16:00)")
            
            submit_slots = st.form_submit_button("Publish Calendar Inventory")
            if submit_slots:
                slots_to_add = []
                if slot_1: slots_to_add.append("09:00-11:00")
                if slot_2: slots_to_add.append("11:00-13:00")
                if slot_3: slots_to_add.append("14:00-16:00")
                
                if not active_worker_id or not slots_to_add:
                    st.error("Please provide your Worker ID and select at least one time slot block.")
                else:
                    shift_date_str = shift_date.strftime("%Y-%m-%d")
                    # Decoupled Action: POST request to map inventory slots to worker calendars
                    shift_payload = {"worker_id": active_worker_id, "date": shift_date_str, "slots": slots_to_add}
                    try:
                        response = requests.post(f"{API_URL}/workers/availability", json=shift_payload)
                        if response.status_code == 200:
                            st.success(f"Calendar inventory pushed successfully for {shift_date_str}!")
                        else:
                            st.error(f"Failed to post shifts: {response.json().get('detail')}")
                    except requests.exceptions.ConnectionError:
                        st.error("Backend validation server is unreachable.")