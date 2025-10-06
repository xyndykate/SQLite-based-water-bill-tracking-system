#!/usr/bin/env python3
"""
Demo script for SQLite-based Water Bill Tracking System
"""

import os
from datetime import datetime, timedelta

def demo_sqlite():
    """Demonstrate the SQLite-based water bill tracking system."""
    
    print("🌊 SQLite Water Bill Tracking System Demo")
    print("="*60)
    
    try:
        from services import WaterBillService
        from database import db_manager
        
        # Check database connection
        if not db_manager.test_connection():
            print("❌ Database connection failed! Run: python db_utils.py setup")
            return
        
        print("✅ Database connected successfully!")
        
        # Initialize service
        service = WaterBillService()
        
        # Demo 1: Add tenants
        print("\n1️⃣ Adding sample tenants...")
        tenants_data = [
            ("T001", "John Doe", "A101", "555-1234", "john.doe@email.com"),
            ("T002", "Jane Smith", "B205", "555-5678", "jane.smith@email.com"),
            ("T003", "Bob Johnson", "C303", "555-9012", "bob.johnson@email.com"),
        ]
        
        for tenant_id, name, apt, phone, email in tenants_data:
            if service.add_tenant(tenant_id, name, apt, phone, email):
                print(f"  ✅ Added: {name} ({tenant_id})")
            else:
                print(f"  ⚠️  Tenant {tenant_id} already exists or failed to add")
        
        # Demo 2: Add water readings
        print("\n2️⃣ Adding water readings...")
        previous_month = datetime.now() - timedelta(days=30)
        current_date = datetime.now()
        
        # Initial readings
        readings_data = [
            ("T001", 1000.0, previous_month),
            ("T002", 2000.0, previous_month),
            ("T003", 1500.0, previous_month),
        ]
        
        for tenant_id, reading, date in readings_data:
            if service.add_water_reading(tenant_id, reading, date, "Initial reading"):
                print(f"  ✅ Added initial reading for {tenant_id}: {reading}")
        
        # Current readings
        current_readings = [
            ("T001", 1150.0),
            ("T002", 2080.0),
            ("T003", 1650.0),
        ]
        
        for tenant_id, reading in current_readings:
            if service.add_water_reading(tenant_id, reading, current_date, "Monthly reading"):
                print(f"  ✅ Added current reading for {tenant_id}: {reading}")
        
        # Demo 3: Calculate and display bills
        print("\n3️⃣ Calculating bills...")
        for tenant_id, name, apt, _, _ in tenants_data:
            bill_data = service.calculate_bill(tenant_id)
            if bill_data:
                print(f"\n📄 Bill for {name} ({tenant_id}):")
                print(f"   Period: {bill_data['period_start']} to {bill_data['period_end']}")
                print(f"   Consumption: {bill_data['units_consumed']} units")
                print(f"   Amount: ${bill_data['total_amount']:.2f}")
        
        # Demo 4: Generate actual bills
        print("\n4️⃣ Generating bills...")
        for tenant_id, name, _, _, _ in tenants_data:
            bill = service.generate_bill(tenant_id)
            if bill:
                print(f"  ✅ Bill #{bill.id} generated for {name}")
        
        print("\n🎉 Demo completed successfully!")
        print(f"\nDatabase location: {os.path.abspath(db_manager.config.get_database_path())}")
        print("\nTo run the full application: python main.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to run 'python db_utils.py setup' first")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_sqlite()