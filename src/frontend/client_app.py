# To convert the central Birmingham cleaning engine into an interactive web prototype, 
# Streamlit library would be use.
# This code would run a Client Booking App and a Cleaner Schedule Dashboard.
# Client Dashboard (frontend/client_app.py): Run this app using: streamlit run frontend/client_app.py --server.port 8501
# Hosted on Streamlit.app: https://cleanapp-client-mvp.streamlit.app/

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
st.set_page_config(page_title="Client Experience Portal", layout="wide")
st.header("Find a Reliable Local Cleaner")

column_reg, column_search = st.columns([1, 2], gap="large")

with column_reg:
    st.subheader("👤 Step 1: Create Client Profile")
    with st.form("client_reg_form", clear_on_submit=True):
        client_id = st.text_input("Client ID Key (e.g., C101)")
        client_name = st.text_input("Full Name")
        client_email = st.text_input("Email Address")
        client_phone = st.text_input("Phone Number")
        client_postcode = st.text_input("Birmingham Postcode (e.g., B1 1AY)")

        submit_client = st.form_submit_button("Register Account")
        if submit_client:
            if not (client_id and client_name and client_email and client_postcode):
                st.error("Please fill out all primary identity fields.")
            else:
                # Decoupled Action: Network POST request replaces direct memory reference
                payload = {
                    "client_id": client_id, "name": client_name,
                    "email": client_email, "phone": client_phone, "postcode": client_postcode
                }
                try:
                    response = requests.post(f"{API_URL}/clients/register", json=payload)
                    if response.status_code == 200:
                        st.success(f"Welcome {client_name}! Account active in database.")
                    else:
                        st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the central backend server.")
                
    with column_search:
        st.subheader("🔍 Step 2: Browse and Checkout Available Openings")
        
        search_column1, search_column2, search_column3 = st.columns(3)
        with search_column1:
            target_postcode = st.text_input("Enter Delivery Postcode", value="B1 1AY")
        with search_column2:
            target_date = st.date_input("Target Date", min_value=date.today())
        with search_column3:
            target_slot = st.selectbox("Preferred Time Block", ["09:00-11:00", "11:00-13:00", "14:00-16:00"])
            
        date_str = target_date.strftime("%Y-%m-%d")

        # Decoupled Action: GET network query with URL params fetches cleaner availability matrix
        available_cleaners = []
        try:
            search_params = {"postcode": target_postcode, "date": date_str, "slot": target_slot}
            response = requests.get(f"{API_URL}/cleaners/search", params=search_params)
            if response.status_code == 200:
                available_cleaners = response.json()
        except requests.exceptions.ConnectionError:
            st.error("Search module offline. Connect backend API server.")
        
        if not available_cleaners:
            st.info(f"ℹ️ No cleaners are currently listing availability for {target_postcode} on {date_str} at {target_slot}.")
        else:
            st.success(f"🎉 Found {len(available_cleaners)} professional(s) matching your request:")

            for cleaner in available_cleaners:
                with st.container(border=True):
                    row1, row2 = st.columns([3, 1])
                    with row1:
                        st.markdown(f"### 🧼 {cleaner['name']}")
                        st.markdown(f"**Rate:** £{cleaner['hourly_rate']:.2f}/hr | **Estimated Total Cost (2-hr block):** £{cleaner['hourly_rate']*2:.2f}")
                    with row2:
                        # Dedicated text field to simulate secure customer identification
                        checkout_client_id = st.text_input("Confirm Client ID to Book", key=f"id_{cleaner['worker_id']}")
                        
                        if st.button(f"Book {cleaner['name']}", key=f"btn_{cleaner['worker_id']}"):
                            if not checkout_client_id:
                                st.warning("Please type your Client ID to authorize checkout.")
                            else:
                                # Decoupled Action: POST request to submit a secure booking
                                booking_payload = {
                                    "client_id": checkout_client_id, "worker_id": cleaner['worker_id'],
                                    "date": date_str, "slot": target_slot
                                }
                                booking_resp = requests.post(f"{API_URL}/bookings/create", json=booking_payload)
                                if booking_resp.status_code == 200:
                                    result = booking_resp.json()
                                    st.toast("Card Payment Authorised via Simulated Stripe Split!", icon="💳")
                                    st.success(f"**Booking Confirmed!** ID: {result['booking_id']}")
                                    st.rerun()
                                else:
                                    st.error("Transaction declined. Check that your client ID is registered and valid.")