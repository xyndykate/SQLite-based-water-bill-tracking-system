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
        self.settings_repo = SystemSettingRepository()
    
    # Tenant operations
    def add_tenant(self, tenant_id: str, name: str, apartment_number: str, 
                   phone: str = None, email: str = None) -> bool:
        """Add a new tenant."""
        try:
            # Check if tenant already exists
            if self.tenant_repo.exists(tenant_id):
                logger.warning(f"Tenant {tenant_id} already exists")
                return False
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                apartment_number=apartment_number,
                phone=phone,
                email=email
            )
            
            created_tenant = self.tenant_repo.create(tenant)
            return created_tenant is not None
            
        except Exception as e:
            logger.error(f"Failed to add tenant: {e}")
            return False
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenant_repo.get_by_id(tenant_id)
    
    def get_all_tenants(self, active_only: bool = True) -> List[Tenant]:
        """Get all tenants."""
        return self.tenant_repo.get_all(active_only)
    
    def update_tenant(self, tenant_id: str, name: str = None, apartment_number: str = None,
                     phone: str = None, email: str = None) -> bool:
        """Update tenant information."""
        try:
            tenant = self.tenant_repo.get_by_id(tenant_id)
            if not tenant:
                logger.warning(f"Tenant {tenant_id} not found")
                return False
            
            # Update only provided fields
            if name is not None:
                tenant.name = name
            if apartment_number is not None:
                tenant.apartment_number = apartment_number
            if phone is not None:
                tenant.phone = phone
            if email is not None:
                tenant.email = email
            
            return self.tenant_repo.update(tenant)
            
        except Exception as e:
            logger.error(f"Failed to update tenant: {e}")
            return False
    
    def remove_tenant(self, tenant_id: str, hard_delete: bool = False) -> bool:
        """Remove a tenant (soft delete by default)."""
        return self.tenant_repo.delete(tenant_id, soft_delete=not hard_delete)
    
    # Water reading operations
    def add_water_reading(self, tenant_id: str, reading_units: float, 
                         reading_date: datetime = None, notes: str = None,
                         created_by: str = None, validate: bool = True) -> bool:
        """Add a water reading for a tenant."""
        try:
            # Verify tenant exists
            if not self.tenant_repo.exists(tenant_id):
                logger.warning(f"Tenant {tenant_id} not found")
                return False
            
            if reading_date is None:
                reading_date = datetime.now()
            
            # Validate reading progression if requested
            if validate:
                last_reading = self.reading_repo.get_latest_reading(tenant_id)
                if last_reading and reading_units < float(last_reading.reading_units):
                    logger.warning(f"New reading ({reading_units}) is lower than last reading ({last_reading.reading_units})")
                    # In a real application, you might want to prompt the user or require confirmation
            
            reading = WaterReading(
                tenant_id=tenant_id,
                reading_units=float(reading_units),
                reading_date=reading_date,
                notes=notes,
                created_by=created_by
            )
            
            created_reading = self.reading_repo.create(reading)
            return created_reading is not None
            
        except Exception as e:
            logger.error(f"Failed to add water reading: {e}")
            return False
    
    def get_tenant_readings(self, tenant_id: str, limit: int = None) -> List[WaterReading]:
        """Get water readings for a tenant."""
        return self.reading_repo.get_by_tenant(tenant_id, limit)
    
    def get_latest_reading(self, tenant_id: str) -> Optional[WaterReading]:
        """Get the latest reading for a tenant."""
        return self.reading_repo.get_latest_reading(tenant_id)
    
    # Bill operations
    def calculate_bill(self, tenant_id: str, period_start: date = None, 
                      period_end: date = None) -> Optional[Dict]:
        """Calculate a water bill for a tenant."""
        try:
            # Verify tenant exists
            tenant = self.tenant_repo.get_by_id(tenant_id)
            if not tenant:
                logger.warning(f"Tenant {tenant_id} not found")
                return None
            
            # Get readings for the period
            if period_start and period_end:
                readings = self.reading_repo.get_reading_range(
                    tenant_id, 
                    datetime.combine(period_start, datetime.min.time()),
                    datetime.combine(period_end, datetime.max.time())
                )
            else:
                # Use last two readings
                readings = self.reading_repo.get_by_tenant(tenant_id, limit=2)
                readings.reverse()  # Chronological order
            
            if len(readings) < 2:
                logger.warning(f"Insufficient readings for tenant {tenant_id}")
                return None
            
            start_reading = readings[0]
            end_reading = readings[-1]
            
            # Calculate consumption
            units_consumed = end_reading.reading_units - start_reading.reading_units
            
            # Get rate from settings
            rate_str = self.settings_repo.get_setting('default_rate_per_unit')
            rate_per_unit = float(rate_str) if rate_str else 2.50
            
            total_amount = units_consumed * rate_per_unit
            
            # Get currency from settings
            currency = self.settings_repo.get_setting('default_currency') or 'USD'
            
            # Convert reading_date to date object (handles both string and datetime)
            if isinstance(start_reading.reading_date, str):
                period_start = datetime.fromisoformat(start_reading.reading_date.replace('Z', '+00:00')).date()
            else:
                period_start = start_reading.reading_date.date() if hasattr(start_reading.reading_date, 'date') else start_reading.reading_date
            
            if isinstance(end_reading.reading_date, str):
                period_end = datetime.fromisoformat(end_reading.reading_date.replace('Z', '+00:00')).date()
            else:
                period_end = end_reading.reading_date.date() if hasattr(end_reading.reading_date, 'date') else end_reading.reading_date
            
            bill_data = {
                'tenant_id': tenant_id,
                'tenant_name': tenant.name,
                'apartment_number': tenant.apartment_number,
                'period_start': period_start,
                'period_end': period_end,
                'start_reading': start_reading.reading_units,
                'end_reading': end_reading.reading_units,
                'units_consumed': units_consumed,
                'rate_per_unit': rate_per_unit,
                'total_amount': total_amount,
                'currency': currency,
                'start_reading_id': start_reading.id,
                'end_reading_id': end_reading.id
            }
            
            return bill_data
            
        except Exception as e:
            logger.error(f"Failed to calculate bill: {e}")
            return None
    
    def generate_bill(self, tenant_id: str, period_start: date = None, 
                     period_end: date = None, due_days: int = 30) -> Optional[Bill]:
        """Generate and save a bill for a tenant."""
        try:
            bill_data = self.calculate_bill(tenant_id, period_start, period_end)
            if not bill_data:
                return None
            
            # Calculate due date
            due_date = date.today() + timedelta(days=due_days)
            
            bill = Bill(
                tenant_id=tenant_id,
                bill_period_start=bill_data['period_start'],
                bill_period_end=bill_data['period_end'],
                start_reading_id=bill_data['start_reading_id'],
                end_reading_id=bill_data['end_reading_id'],
                units_consumed=bill_data['units_consumed'],
                rate_per_unit=bill_data['rate_per_unit'],
                total_amount=bill_data['total_amount'],
                currency=bill_data['currency'],
                due_date=due_date
            )
            
            return self.bill_repo.create(bill)
            
        except Exception as e:
            logger.error(f"Failed to generate bill: {e}")
            return None
    
    def get_tenant_bills(self, tenant_id: str) -> List[Bill]:
        """Get all bills for a tenant."""
        return self.bill_repo.get_by_tenant(tenant_id)
    
    def mark_bill_paid(self, bill_id: int, payment_date: datetime = None) -> bool:
        """Mark a bill as paid."""
        return self.bill_repo.mark_as_paid(bill_id, payment_date)
    
    # Settings operations
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a system setting."""
        value = self.settings_repo.get_setting(key)
        return value if value is not None else default
    
    def update_setting(self, key: str, value: str, description: str = None) -> bool:
        """Update a system setting."""
        return self.settings_repo.set_setting(key, value, description)
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all system settings."""
        return self.settings_repo.get_all_settings()
    
    # Reporting and analytics
    def get_tenant_summary(self, tenant_id: str = None) -> List[Dict]:
        """Get tenant summary with consumption and billing info."""
        # This would use the tenant_summary view from the database
        from database import db_manager
        
        try:
            if tenant_id:
                query = "SELECT * FROM tenant_summary WHERE tenant_id = %s"
                params = (tenant_id,)
            else:
                query = "SELECT * FROM tenant_summary ORDER BY apartment_number"
                params = ()
            
            result = db_manager.execute_query(query, params, fetch=True)
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get tenant summary: {e}")
            return []
    
    def get_monthly_consumption_report(self, year: int = None, month: int = None) -> List[Dict]:
        """Get monthly consumption report."""
        from database import db_manager
        
        try:
            query = "SELECT * FROM monthly_consumption"
            params = []
            
            if year and month:
                query += " WHERE EXTRACT(YEAR FROM month) = %s AND EXTRACT(MONTH FROM month) = %s"
                params = [year, month]
            elif year:
                query += " WHERE EXTRACT(YEAR FROM month) = %s"
                params = [year]
            
            query += " ORDER BY month DESC, apartment_number"
            
            result = db_manager.execute_query(query, tuple(params), fetch=True)
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get monthly consumption report: {e}")
            return []
    
    def get_outstanding_bills(self) -> List[Dict]:
        """Get all outstanding (unpaid) bills."""
        from database import db_manager
        
        try:
            query = """
                SELECT b.*, t.name, t.apartment_number
                FROM bills b
                JOIN tenants t ON b.tenant_id = t.tenant_id
                WHERE b.bill_status != 'paid'
                ORDER BY b.due_date ASC
            """
            
            result = db_manager.execute_query(query, fetch=True)
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Failed to get outstanding bills: {e}")
            return []
