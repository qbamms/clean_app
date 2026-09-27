# This script contains the core business operations. 
# It strictly validates that clients are based in central Birmingham and programmatically ensures workers are matched 
# by both their postcode zone, active availability, and applies a 20% platform commission fee split at checkout.

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

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
    def __init__(self, db_path: str = "cleaning_engine.db"):
        # Maintained for initialization compatibility, though we route queries via the db Session
        self.db_path = db_path

    def register_client(self, db: Session, client_id: str, name: str, email: str, phone: str, postcode: str) -> bool:
        zone = BirminghamMVPConfig.clean_postcode(postcode)
        if zone not in VALID_BIRMINGHAM_ZONES:
            print(f"❌ Registration rejected: {zone} is outside our Birmingham City Centre MVP zone.")
            return False

        try:
            # 1. Neon Postgres requires text() wrapper and named variables (:var) instead of (?)
            query = text("""
                INSERT INTO clients (client_id, name, email, phone, postcode)
                VALUES (:client_id, :name, :email, :phone, :postcode)
            """)
            db.execute(query, {
                "client_id": client_id,
                "name": name,
                "email": email,
                "phone": phone,
                "postcode": zone
            })
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Registration rejected: {e}")
            return False

    def register_worker(self, db: Session, worker_id: str, name: str, email: str, phone: str, hourly_rate: float, covered_zones: List[str]) -> bool:
        cleaned_zones = [BirminghamMVPConfig.clean_postcode(z) for z in covered_zones if BirminghamMVPConfig.clean_postcode(z) in VALID_BIRMINGHAM_ZONES]
        
        if not cleaned_zones:
            print("❌ Registration rejected: Worker must service at least one core zone (B1-B5).")
            return False

        try:
            # Insert main worker profile
            worker_query = text("""
                INSERT INTO workers (worker_id, name, email, phone, hourly_rate)
                VALUES (:worker_id, :name, :email, :phone, :hourly_rate)
            """)
            db.execute(worker_query, {
                "worker_id": worker_id,
                "name": name,
                "email": email,
                "phone": phone,
                "hourly_rate": hourly_rate
            })
            
            # 2. Postgres uses ON CONFLICT DO NOTHING instead of INSERT OR IGNORE
            zone_query = text("""
                INSERT INTO worker_zones (worker_id, postcode)
                VALUES (:worker_id, :postcode)
                ON CONFLICT DO NOTHING
            """)
            for zone in cleaned_zones:
                db.execute(zone_query, {"worker_id": worker_id, "postcode": zone})
                
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"❌ Registration rejected: {e}")
            return False

    def add_worker_availability(self, db: Session, worker_id: str, date_str: str, time_slots: List[str]):
        """Time slots formatted uniformly as 2-hour windows: '09:00-11:00' or '14:00-16:00'"""
        try:
            query = text("""
                INSERT INTO worker_availability (worker_id, date_str, time_slot)
                VALUES (:worker_id, :date_str, :time_slot)
                ON CONFLICT DO NOTHING
            """)
            for slot in time_slots:
                db.execute(query, {"worker_id": worker_id, "date_str": date_str, "time_slot": slot})
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"❌ Failed to add worker availability: {e}")
            raise e

    def search_available_cleaners(self, db: Session, client_postcode: str, date_str: str, time_slot: str) -> List[Dict[str, Any]]:
        """Matches workers who service the specific postcode sector and are free at that exact time."""
        zone = BirminghamMVPConfig.clean_postcode(client_postcode)

        query = text("""
            SELECT w.worker_id, w.name, w.hourly_rate, w.phone 
            FROM workers w
            JOIN worker_zones wz ON w.worker_id = wz.worker_id
            JOIN worker_availability wa ON w.worker_id = wa.worker_id
            WHERE wz.postcode = :postcode 
              AND wa.date_str = :date_str 
              AND wa.time_slot = :time_slot
        """)

        try:
            # 3. Use mappings().all() to convert Postgres result rows into clean dictionaries
            result = db.execute(query, {"postcode": zone, "date_str": date_str, "time_slot": time_slot})
            return [dict(row) for row in result.mappings().all()]
        except Exception as e:
            print(f"❌ Cleaner search query failed: {e}")
            return []

    def book_cleaning(self, db: Session, client_id: str, worker_id: str, date_str: str, time_slot: str) -> Optional[Dict[str, Any]]:
        """Atomically processes pricing based on standard 2-hour service increments and locks the slot."""
        try:
            # 1. Double-check worker availability still holds true
            availability_query = text("""
                SELECT 1 FROM worker_availability 
                WHERE worker_id = :worker_id AND date_str = :date_str AND time_slot = :time_slot
            """)
            avail_check = db.execute(availability_query, {"worker_id": worker_id, "date_str": date_str, "time_slot": time_slot}).fetchone()
            
            if not avail_check:
                print("❌ Booking Error: Slot is no longer available.")
                return None

            # 2. Grab worker hourly rate using mappings().first() to fetch dict columns securely
            rate_query = text("SELECT hourly_rate FROM workers WHERE worker_id = :worker_id")
            worker_data = db.execute(rate_query, {"worker_id": worker_id}).mappings().first()
            if not worker_data:
                return None

            # Fixed 2-hour cleaning blocks for the MVP
            gross_amount = worker_data['hourly_rate'] * 2.0
            booking_id = f"BHM-{int(datetime.now().timestamp())}"

            # Simulated 20% platform commission fee split
            platform_fee = round(gross_amount * 0.20, 2)
            worker_payout = round(gross_amount - platform_fee, 2)

            # 3. Insert Booking record into the ledger
            insert_booking = text("""
                INSERT INTO bookings (booking_id, client_id, worker_id, date_str, time_slot, gross_amount, platform_fee, worker_payout)
                VALUES (:booking_id, :client_id, :worker_id, :date_str, :time_slot, :gross_amount, :platform_fee, :worker_payout)
            """)
            db.execute(insert_booking, {
                "booking_id": booking_id,
                "client_id": client_id,
                "worker_id": worker_id,
                "date_str": date_str,
                "time_slot": time_slot,
                "gross_amount": gross_amount,
                "platform_fee": platform_fee,
                "worker_payout": worker_payout
            })
            
            # 4. Remove time slot from available pool to avoid double-bookings
            delete_availability = text("""
                DELETE FROM worker_availability 
                WHERE worker_id = :worker_id AND date_str = :date_str AND time_slot = :time_slot
            """)
            db.execute(delete_availability, {"worker_id": worker_id, "date_str": date_str, "time_slot": time_slot})
            
            db.commit()
            print(f"✅ Success: {booking_id} confirmed for Residential Clean in {date_str} ({time_slot}). Total: £{gross_amount:.2f}")
            return {
                "booking_id": booking_id,
                "gross_amount": gross_amount,
                "platform_fee": platform_fee,
                "worker_payout": worker_payout
            }
        except Exception as e:
            print(f"❌ Transaction failure: {e}")
            db.rollback()
            return None

    def export_ledger_csv(self, db: Session, filename: str = "generated/birmingham_mvp_ledger.csv"):
        """Exports the transaction history to a CSV spreadsheet."""
        try:
            # Run query through connection bind to safely feed pandas read_sql
            df = pd.read_sql_query("SELECT * FROM bookings", db.bind)
            df.to_csv(filename, index=False)
            return filename
        except Exception as e:
            print(f"❌ Ledger export failed: {e}")
            return None
