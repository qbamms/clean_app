# To convert the central Birmingham cleaning engine into an interactive web prototype, 
# Streamlit library would be use.
# This code would run a multi-tab application where you can toggle between a Client Booking App and a Cleaner Schedule Dashboard.

import streamlit as st
import os
from datetime import date
from db import database
from app import engine

# Ensure database file exists on boot
if not os.path.exists("marketplace.db"):
    database.init_db()

# Initialize the marketplace backend engine
app = engine.CentralBirminghamMarketplace()

# Page layout configurations
st.set_page_config(
    page_title="BrumClean MVP Portal", 
    page_icon="🧹", 
    layout="wide"
)

st.title("🧹 BrumClean Marketplace Prototype")
st.caption("📍 Serving Postcodes: B1, B2, B3, B4, B5 (Birmingham City Centre Only)")

# Create separate operational views using tabs
tab_client, tab_worker, tab_admin = st.tabs([
    "📱 Client Marketplace (Book a Clean)", 
    "🏃 Cleaner Portal (Manage Shifts)", 
    "📊 Admin Ledger & Analytics"
])

# ==============================================================================
# TAB 1: CLIENT WEB EXPERIENCE
# ==============================================================================
with tab_client:
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
                    success = app.register_client(client_id, client_name, client_email, client_phone, client_postcode)
                    if success:
                        st.success(f"Welcome aboard, {client_name}! Account active in database.")
                    else:
                        st.error("Registration failed. Ensure postcode is central (B1-B5) and email is unique.")

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

        # Trigger real-time matching query against backend
        available_cleaners = app.search_available_cleaners(target_postcode, date_str, target_slot)
        
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
                                result = app.book_cleaning(checkout_client_id, cleaner['worker_id'], date_str, target_slot)
                                if result:
                                    st.toast("Card Payment Authorised via Simulated Stripe Split!", icon="💳")
                                    st.success(f"**Booking Confirmed!** ID: {result['booking_id']}")
                                    st.rerun()
                                else:
                                    st.error("Transaction declined. Check that your client ID is registered and valid.")

# ==============================================================================
# TAB 2: CLEANER MANAGEMENT EXPERIENCE 
# ==============================================================================
with tab_worker:
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
                    worker_success = app.register_worker(worker_id, worker_name, worker_email, worker_phone, worker_rate, zones)
                    if worker_success:
                        st.success(f"Welcome to the team, {worker_name}! Profile successfully deployed to database.")
                    else:
                        st.error("Registration failed. Ensure your Worker ID or email is unique.")

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
                    app.add_worker_availability(active_worker_id, shift_date_str, slots_to_add)
                    st.success(f"Calendar inventory pushed successfully for {shift_date_str}!")

# ==============================================================================
# TAB 3: BACK-OFFICE REPORTING & ANALYTICS
# ==============================================================================
with tab_admin:
    st.header("Back-Office Financial & Operational Analytics")
    
    # Standard SQLite connection specifically formatted for generating diagnostic frames
    import sqlite3
    import pandas as pd
    
    conn = sqlite3.connect("marketplace.db")
    df_bookings = pd.read_sql_query("SELECT * FROM bookings", conn)
    conn.close()
    
    if df_bookings.empty:
        st.info("📊 No financial checkout operations have been run yet inside this deployment.")
    else:
        # High-level aggregate operational metrics
        total_gross = df_bookings["gross_amount"].sum()
        total_fees = df_bookings["platform_fee"].sum()
        cleaner_share = df_bookings["worker_payout"].sum()

        manager_column1, manager_column2, manager_column3, manager_column4 = st.columns(4)
        manager_column1.metric("📦 Total Bookings", len(df_bookings))
        manager_column2.metric("💳 Gross Volume Processed", f"£{total_gross:.2f}")
        manager_column3.metric("🏢 Platform Revenue (20% Split)", f"£{total_fees:.2f}", delta="Net Revenue")
        manager_column4.metric("🤝 Total Cleaner Payouts", f"£{cleaner_share:.2f}")

        st.subheader("🗃️ Real-Time Transaction Ledger History")
        st.dataframe(df_bookings, width='stretch')
        
        # Interactive file export engine call
        os.makedirs("generated", exist_ok=True)                               

filepath = app.export_ledger_csv("generated/birmingham_mvp_ledger.csv")
with open(filepath, "r") as file:st.download_button \
(label="📥 Export Ledger History to CSV",data=file.read(),file_name="birmingham_mvp_ledger.csv",mime="text/csv")
