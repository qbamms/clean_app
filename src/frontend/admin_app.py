# To convert the central Birmingham cleaning engine into an interactive web prototype, 
# Streamlit library would be use.
# This code would run a Admin Booking App Dashboard.
# Admin Dashboard (frontend/admin_app.py): Run this app using: streamlit run frontend/admin_app.py --server.port 8503
# Hosted on Streamlit.app: https://cleanapp-mvp.streamlit.app/

import streamlit as st
import streamlit as pd
import pandas as pd
import requests
import os
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
st.set_page_config(page_title="Operational Control Hub", layout="wide")
st.header("Back-Office Financial & Operational Analytics")
st.title("🧹 BrumClean Marketplace Prototype")
st.caption("📍 Serving Postcodes: B1, B2, B3, B4, B5 (Birmingham City Centre Only)")

# Decoupled Action: Admin aggregates platform wide operational tables over HTTP GET requests
if st.button("🔄 Sync Summary & Detail Tables", type="primary"):
    try:
        response = requests.get(f"{API_URL}/admin/metrics")
        if response.status_code == 200:
            payload = response.json()
            
            # Extract out separate data structures cleanly
            summary = payload.get("summary", {})
            details = payload.get("details", {})
            
            # ==================================================================
            # LAYER 1: THE EXECUTIVE SUMMARY CONTROL PANE (Glanceable Counts)
            # ==================================================================
            st.subheader("📊 Key Performance Indicators (KPIs)")
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            metric_col1.metric(
                label="Registered Clients", 
                value=summary.get("total_clients", 0)
            )
            metric_col2.metric(
                label="Active Service Providers", 
                value=summary.get("total_workers", 0)
            )
            metric_col3.metric(
                label="Total System Bookings", 
                value=summary.get("total_bookings", 0)
            )
            metric_col4.metric(
                label="Platform Fees Earned (20% Split)", 
                value=f"£{summary.get('platform_commission_collected', 0.00):.2f}",
                delta=f"Gross GMV: £{summary.get('gross_revenue_collected', 0.00):.2f}"
            )
            
            st.markdown("---")
            
            # ==================================================================
            # LAYER 2: THE OPERATIONAL DETAIL DATA GRID (Granular Table Views)
            # ==================================================================
            st.subheader("🔍 Deep-Dive Operational Registries")
            
            tab_bookings, tab_clients, tab_workers = st.tabs([
                "💳 Transactional Ledger", 
                "👥 Client Records", 
                "🧼 Worker Profiles"
            ])
            
            with tab_bookings:
                bookings_data = details.get("bookings", [])
                if bookings_data:
                    df_bookings = pd.DataFrame(bookings_data)
                    st.dataframe(df_bookings, use_container_width=True)
                else:
                    st.info("No bookings have been logged by the system engine yet.")
                    
            with tab_clients:
                clients_data = details.get("clients", [])
                if clients_data:
                    df_clients = pd.DataFrame(clients_data)
                    df_clients.columns = ["Client ID Key", "Full Legal Name", "Email Address", "Phone Line", "Postcode Sector"]
                    st.dataframe(df_clients, use_container_width=True)
                else:
                    st.info("No customer client entries found within this database node.")
                    
            with tab_workers:
                workers_data = details.get("workers", [])
                if workers_data:
                    df_workers = pd.DataFrame(workers_data)
                    df_workers.columns = ["Worker Ref ID", "Professional Name", "Direct Email", "Mobile Number", "Hourly Base Rate (£)"]
                    st.dataframe(df_workers, use_container_width=True)
                else:
                    st.info("No cleaning service providers are currently onboarded.")
                    
    except requests.exceptions.ConnectionError:
        st.error("System Connection Error: Unable to trace your FastAPI backend on port 8000.")
