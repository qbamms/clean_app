# This script contains the core business operations. 
# It strictly validates that clients are based in central Birmingham and programmatically ensures workers are matched 
# by both their postcode zone, active availability, and applies a 20% platform commission fee split at checkout.

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

# Central Birmingham MVP Service Boundaries
VALID_BIRMINGHAM_ZONES = {"B1", "B2", "B3", "B4", "B5"}

class BirminghamMVPConfig:
    """Expecting a string data type and @staticmethod decorator behaves exactly like an isolated, normal function,
    but lives inside a class namespace for logical organization."""
    @staticmethod
    def clean_postcode(pc: str) -> str:
        """Extracts the outward sector (e.g., 'B1' from 'B1 1AY')."""
        return pc.strip().upper().split()[0]

class CentralBirminghamMarketplace:
    def __init__(self, db_path: str = "marketplace.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables access to database fields by column name
        return conn

    def register_client(self, client_id: str, name: str, email: str, phone: str, postcode: str) -> bool:
        zone = BirminghamMVPConfig.clean_postcode(postcode)
        if zone not in VALID_BIRMINGHAM_ZONES:
            print(f"❌ Registration rejected: {zone} is outside our Birmingham City Centre MVP zone.")
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clients VALUES (?, ?, ?, ?, ?)", 
                    (client_id, name, email, phone, zone)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("❌ Registration rejected: Email already exists.")
            return False

    def register_worker(self, worker_id: str, name: str, email: str, phone: str, hourly_rate: float, covered_zones: List[str]) -> bool:
        cleaned_zones = [BirminghamMVPConfig.clean_postcode(z) for z in covered_zones if BirminghamMVPConfig.clean_postcode(z) in VALID_BIRMINGHAM_ZONES]
        
        if not cleaned_zones:
            print("❌ Registration rejected: Worker must service at least one core zone (B1-B5).")
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO workers VALUES (?, ?, ?, ?, ?)", (worker_id, name, email, phone, hourly_rate))
                for zone in cleaned_zones:
                    cursor.execute("INSERT OR IGNORE INTO worker_zones VALUES (?, ?)", (worker_id, zone))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            print("❌ Registration rejected: Cleaner email already exists.")
            return False

    def add_worker_availability(self, worker_id: str, date_str: str, time_slots: List[str]):
        """Time slots formatted uniformly as 2-hour windows: '09:00-11:00' or '14:00-16:00'"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for slot in time_slots:
                cursor.execute("INSERT OR IGNORE INTO worker_availability VALUES (?, ?, ?)", (worker_id, date_str, slot))
            conn.commit()

    def search_available_cleaners(self, client_postcode: str, date_str: str, time_slot: str) -> List[Dict[str, Any]]:
        """Matches workers who service the specific postcode sector and are free at that exact time."""
        zone = BirminghamMVPConfig.clean_postcode(client_postcode)

        query = """
            SELECT w.worker_id, w.name, w.hourly_rate, w.phone 
            FROM workers w
            JOIN worker_zones wz ON w.worker_id = wz.worker_id
            JOIN worker_availability wa ON w.worker_id = wa.worker_id
            WHERE wz.postcode = ? 
              AND wa.date_str = ? 
              AND wa.time_slot = ?
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (zone, date_str, time_slot))
            return [dict(row) for row in cursor.fetchall()]

    def book_cleaning(self, client_id: str, worker_id: str, date_str: str, time_slot: str) -> Optional[str]:
        """Atomically processes pricing based on standard 2-hour service increments and locks the slot."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Double-check worker availability still holds true
            cursor.execute(
                "SELECT 1 FROM worker_availability WHERE worker_id = ? AND date_str = ? AND time_slot = ?", 
                (worker_id, date_str, time_slot)
            )
            if not cursor.fetchone():
                print("❌ Booking Error: Slot is no longer available.")
                return None

            # 2. Grab worker hourly rate to calculate fixed cost (MVP assumes 2-hour slots)
            cursor.execute("SELECT hourly_rate FROM workers WHERE worker_id = ?", (worker_id,))
            worker_data = cursor.fetchone()
            if not worker_data:
                return None

            # Fixed 2-hour cleaning blocks for the MVP
            gross_amount = worker_data['hourly_rate'] * 2.0
            booking_id = f"BHM-{int(datetime.now().timestamp())}"

            # Simulated 20% platform commission fee split
            platform_fee = round(gross_amount * 0.20, 2)
            worker_payout = round(gross_amount - platform_fee, 2)
            booking_id = f"BHM-{int(datetime.now().timestamp())}"

            try:
                # 3. Insert Booking
                cursor.execute(
                    "INSERT INTO bookings (booking_id, client_id, worker_id, date_str, time_slot, gross_amount,platform_fee, worker_payout)\
                          VALUES (?, ?, ?, ?, ?, ?,?,?)",
                    (booking_id, client_id, worker_id, date_str, time_slot, gross_amount, platform_fee, worker_payout)
                )
                # 4. Remove time slot from available pool to avoid double-bookings
                cursor.execute(
                    "DELETE FROM worker_availability WHERE worker_id = ? AND date_str = ? AND time_slot = ?", 
                    (worker_id, date_str, time_slot)
                )
                conn.commit()
                print(f"✅ Success: {booking_id} confirmed for Residential Clean in {date_str} ({time_slot}). Total: £{gross_amount:.2f}")
                return {
                    "booking_id": booking_id,
                    "gross_amount": gross_amount,
                    "platform_fee": platform_fee,
                    "worker_payout": worker_payout
                }
            except sqlite3.Error as e:
                print(f"❌ Transaction failure: {e}")
                conn.rollback()
                return None

    def export_ledger_csv(self, filename: str = "generated/birmingham_mvp_ledger.csv"):
        """Exports the transaction history to a CSV spreadsheet."""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM bookings", conn)
            df.to_csv(filename, index=False)
            return filename
