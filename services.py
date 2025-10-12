"""
Business logic layer for the Water Bill Tracking System
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple
import logging

from models import (
    Tenant, WaterReading, Bill, SystemSetting,
    TenantRepository, WaterReadingRepository, BillRepository, SystemSettingRepository
)

logger = logging.getLogger(__name__)

class WaterBillService:
    """Main service class for water bill operations."""
    
    def __init__(self):
        self.tenant_repo = TenantRepository()
        self.reading_repo = WaterReadingRepository()
        self.bill_repo = BillRepository()
        self.setting_repo = SystemSettingRepository()
        self.db_manager = self.tenant_repo.db_manager
    
    def add_tenant(self, tenant_id: str, name: str, apartment_number: str,
                  phone: str = None, email: str = None) -> Tenant:
        """Add a new tenant."""
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            apartment_number=apartment_number,
            phone=phone,
            email=email
        )
        return self.tenant_repo.create(tenant)
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant and all their associated data (readings and bills).
        
        Args:
            tenant_id: The ID of the tenant to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            ValueError: If tenant not found
        """
        # Check if tenant exists
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
            
        try:
            # Start a transaction
            with self.db_manager.get_cursor() as cursor:
                # Delete bills first (due to foreign key constraints)
                cursor.execute("""
                    DELETE FROM bills 
                    WHERE tenant_id = ?
                """, (tenant_id,))
                
                # Delete water readings
                cursor.execute("""
                    DELETE FROM water_readings 
                    WHERE tenant_id = ?
                """, (tenant_id,))
                
                # Finally delete the tenant
                cursor.execute("""
                    DELETE FROM tenants 
                    WHERE tenant_id = ?
                """, (tenant_id,))
                
            return True
            
        except Exception as e:
            raise Exception(f"Failed to delete tenant: {str(e)}")
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenant_repo.get_by_id(tenant_id)
    
    def get_all_tenants(self) -> List[Tenant]:
        """Get all tenants."""
        return self.tenant_repo.get_all()
    
    def add_water_reading(self, tenant_id: str, reading_units: float,
                         reading_date: str, notes: str = None) -> WaterReading:
        """Add a new water reading."""
        # Validate tenant exists
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Convert date string to datetime if needed
        if isinstance(reading_date, str):
            reading_date = datetime.strptime(reading_date, '%Y-%m-%d')
        
        reading = WaterReading(
            tenant_id=tenant_id,
            reading_units=reading_units,
            reading_date=reading_date.strftime('%Y-%m-%d'),
            recorded_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            notes=notes
        )
        
        return self.reading_repo.create(reading)
    
    def get_tenant_readings(self, tenant_id: str) -> List[WaterReading]:
        """Get all readings for a tenant."""
        return self.reading_repo.get_by_tenant(tenant_id)
    
    def generate_bill(self, tenant_id: str, start_reading_id: int, end_reading_id: int,
                     rate_per_unit: float = None) -> Bill:
        """Generate a new bill from two readings."""
        # Get readings
        start_reading = self.reading_repo.get_by_id(start_reading_id)
        end_reading = self.reading_repo.get_by_id(end_reading_id)
        
        if not start_reading or not end_reading:
            raise ValueError("Invalid reading IDs")
        
        if start_reading.tenant_id != tenant_id or end_reading.tenant_id != tenant_id:
            raise ValueError("Readings do not belong to the specified tenant")
        
        # Calculate consumption
        units_consumed = end_reading.reading_units - start_reading.reading_units
        if units_consumed <= 0:
            raise ValueError("End reading must be greater than start reading")
        
        # Get rate
        if rate_per_unit is None:
            rate_per_unit = self._get_default_rate()
        
        # Calculate total
        total_amount = units_consumed * rate_per_unit
        
        # Create bill
        bill = Bill(
            tenant_id=tenant_id,
            bill_period_start=start_reading.reading_date,
            bill_period_end=end_reading.reading_date,
            start_reading_id=start_reading_id,
            end_reading_id=end_reading_id,
            units_consumed=units_consumed,
            rate_per_unit=rate_per_unit,
            total_amount=total_amount,
            bill_status='generated'
        )
        
        return self.bill_repo.create(bill)
    
    def get_tenant_bills(self, tenant_id: str) -> List[Bill]:
        """Get all bills for a tenant."""
        return self.bill_repo.get_by_tenant(tenant_id)
    
    def get_outstanding_bills(self, tenant_id: str) -> List[Bill]:
        """Get unpaid bills for a tenant."""
        return [b for b in self.get_tenant_bills(tenant_id) if b.bill_status != 'paid']
    
    def mark_bill_paid(self, bill_id: int) -> Bill:
        """Mark a bill as paid."""
        bill = self.bill_repo.get_by_id(bill_id)
        if not bill:
            raise ValueError(f"Bill {bill_id} not found")
        
        bill.bill_status = 'paid'
        bill.payment_date = datetime.now().strftime('%Y-%m-%d')
        return self.bill_repo.update(bill)
    
    def get_tenant_summary(self, tenant_id: str) -> Dict:
        """Get a summary of tenant activity."""
        tenant = self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        readings = self.get_tenant_readings(tenant_id)
        bills = self.get_tenant_bills(tenant_id)
        outstanding = self.get_outstanding_bills(tenant_id)
        
        total_paid = sum(b.total_amount for b in bills if b.bill_status == 'paid')
        outstanding_amount = sum(b.total_amount for b in outstanding)
        
        return {
            'tenant_id': tenant.tenant_id,
            'name': tenant.name,
            'apartment_number': tenant.apartment_number,
            'total_readings': len(readings),
            'total_bills': len(bills),
            'last_reading_date': readings[-1].reading_date if readings else None,
            'total_paid': total_paid,
            'outstanding_amount': outstanding_amount,
            'bills_paid': len(bills) - len(outstanding),
            'bills_outstanding': len(outstanding)
        }
    
    def update_setting(self, key: str, value: str) -> SystemSetting:
        """Update a system setting."""
        setting = self.setting_repo.get_by_key(key)
        if not setting:
            raise ValueError(f"Setting {key} not found")
        
        setting.setting_value = value
        return self.setting_repo.update(setting)
    
    def _get_default_rate(self) -> float:
        """Get the default rate per unit from settings."""
        setting = self.setting_repo.get_by_key('water_rate_per_unit')
        return float(setting.setting_value) if setting else 2.50  # Default to $2.50