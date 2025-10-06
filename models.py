"""
Data models for the Water Bill Tracking System using SQLite
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

from database import db_manager

logger = logging.getLogger(__name__)

@dataclass
class Tenant:
    """Tenant data model."""
    tenant_id: str
    name: str
    apartment_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    is_active: bool = 1
    id: Optional[int] = None

@dataclass
class WaterReading:
    """Water reading data model."""
    tenant_id: str
    reading_units: float
    reading_date: datetime
    recorded_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    id: Optional[int] = None

@dataclass
class Bill:
    """Bill data model."""
    tenant_id: str
    bill_period_start: date
    bill_period_end: date
    units_consumed: float
    rate_per_unit: float
    total_amount: float
    start_reading_id: Optional[int] = None
    end_reading_id: Optional[int] = None
    currency: str = 'USD'
    bill_status: str = 'generated'
    generated_date: Optional[datetime] = None
    due_date: Optional[date] = None
    paid_date: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class SystemSetting:
    """System setting data model."""
    setting_key: str
    setting_value: str
    description: Optional[str] = None
    updated_date: Optional[datetime] = None
    id: Optional[int] = None

class TenantRepository:
    """Repository for tenant data operations."""
    
    @staticmethod
    def create(tenant: Tenant) -> Optional[Tenant]:
        """Create a new tenant."""
        query = """
            INSERT INTO tenants (tenant_id, name, apartment_number, phone, email, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            RETURNING id, created_date, updated_date
        """
        try:
            result = db_manager.execute_query(
                query, 
                (tenant.tenant_id, tenant.name, tenant.apartment_number, 
                 tenant.phone, tenant.email, tenant.is_active),
                fetch=1
            )
            if result:
                row = result[0]
                tenant.id = row['id']
                tenant.created_date = row['created_date']
                tenant.updated_date = row['updated_date']
                logger.info(f"Created tenant: {tenant.tenant_id}")
                return tenant
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
        return None
    
    @staticmethod
    def get_by_id(tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        query = "SELECT * FROM tenants WHERE tenant_id = ? AND is_active = 1"
        try:
            result = db_manager.execute_query(query, (tenant_id,), fetch=1)
            if result:
                row = result[0]
                return Tenant(**dict(row))
        except Exception as e:
            logger.error(f"Failed to get tenant {tenant_id}: {e}")
        return None
    
    @staticmethod
    def get_all(active_only: bool = 1) -> List[Tenant]:
        """Get all tenants."""
        query = "SELECT * FROM tenants"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY apartment_number"
        
        try:
            result = db_manager.execute_query(query, fetch=1)
            return [Tenant(**dict(row)) for row in result]
        except Exception as e:
            logger.error(f"Failed to get tenants: {e}")
            return []
    
    @staticmethod
    def update(tenant: Tenant) -> bool:
        """Update tenant information."""
        query = """
            UPDATE tenants 
            SET name = ?, apartment_number = ?, phone = ?, email = ?, is_active = ?
            WHERE tenant_id = ?
        """
        try:
            rows_affected = db_manager.execute_query(
                query,
                (tenant.name, tenant.apartment_number, tenant.phone, 
                 tenant.email, tenant.is_active, tenant.tenant_id)
            )
            if rows_affected > 0:
                logger.info(f"Updated tenant: {tenant.tenant_id}")
                return 1
        except Exception as e:
            logger.error(f"Failed to update tenant {tenant.tenant_id}: {e}")
        return 0
    
    @staticmethod
    def delete(tenant_id: str, soft_delete: bool = 1) -> bool:
        """Delete or deactivate tenant."""
        if soft_delete:
            query = "UPDATE tenants SET is_active = 0 WHERE tenant_id = ?"
        else:
            query = "DELETE FROM tenants WHERE tenant_id = ?"
        
        try:
            rows_affected = db_manager.execute_query(query, (tenant_id,))
            if rows_affected > 0:
                action = "deactivated" if soft_delete else "deleted"
                logger.info(f"Tenant {tenant_id} {action}")
                return 1
        except Exception as e:
            logger.error(f"Failed to delete tenant {tenant_id}: {e}")
        return 0
    
    @staticmethod
    def exists(tenant_id: str) -> bool:
        """Check if tenant exists."""
        query = "SELECT 1 FROM tenants WHERE tenant_id = ?"
        try:
            result = db_manager.execute_query(query, (tenant_id,), fetch=1)
            return len(result) > 0
        except Exception as e:
            logger.error(f"Failed to check tenant existence {tenant_id}: {e}")
            return 0

class WaterReadingRepository:
    """Repository for water reading data operations."""
    
    @staticmethod
    def create(reading: WaterReading) -> Optional[WaterReading]:
        """Create a new water reading."""
        query = """
            INSERT INTO water_readings (tenant_id, reading_units, reading_date, notes, created_by)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, recorded_date
        """
        try:
            result = db_manager.execute_query(
                query,
                (reading.tenant_id, reading.reading_units, reading.reading_date,
                 reading.notes, reading.created_by),
                fetch=1
            )
            if result:
                row = result[0]
                reading.id = row['id']
                reading.recorded_date = row['recorded_date']
                logger.info(f"Created water reading for tenant: {reading.tenant_id}")
                return reading
        except Exception as e:
            logger.error(f"Failed to create water reading: {e}")
        return None
    
    @staticmethod
    def get_by_tenant(tenant_id: str, limit: Optional[int] = None) -> List[WaterReading]:
        """Get water readings for a tenant."""
        query = """
            SELECT * FROM water_readings 
            WHERE tenant_id = ? 
            ORDER BY reading_date DESC
        """
        params = [tenant_id]
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        try:
            result = db_manager.execute_query(query, tuple(params), fetch=1)
            return [WaterReading(**dict(row)) for row in result]
        except Exception as e:
            logger.error(f"Failed to get readings for tenant {tenant_id}: {e}")
            return []
    
    @staticmethod
    def get_latest_reading(tenant_id: str) -> Optional[WaterReading]:
        """Get the latest water reading for a tenant."""
        readings = WaterReadingRepository.get_by_tenant(tenant_id, limit=1)
        return readings[0] if readings else None
    
    @staticmethod
    def get_reading_range(tenant_id: str, start_date: datetime, end_date: datetime) -> List[WaterReading]:
        """Get water readings within a date range."""
        query = """
            SELECT * FROM water_readings 
            WHERE tenant_id = ? AND reading_date BETWEEN ? AND ?
            ORDER BY reading_date ASC
        """
        try:
            result = db_manager.execute_query(query, (tenant_id, start_date, end_date), fetch=1)
            return [WaterReading(**dict(row)) for row in result]
        except Exception as e:
            logger.error(f"Failed to get readings for range: {e}")
            return []

class BillRepository:
    """Repository for bill data operations."""
    
    @staticmethod
    def create(bill: Bill) -> Optional[Bill]:
        """Create a new bill."""
        query = """
            INSERT INTO bills (tenant_id, bill_period_start, bill_period_end, 
                             start_reading_id, end_reading_id, units_consumed, 
                             rate_per_unit, total_amount, currency, bill_status, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id, generated_date
        """
        try:
            result = db_manager.execute_query(
                query,
                (bill.tenant_id, bill.bill_period_start, bill.bill_period_end,
                 bill.start_reading_id, bill.end_reading_id, bill.units_consumed,
                 bill.rate_per_unit, bill.total_amount, bill.currency,
                 bill.bill_status, bill.due_date),
                fetch=1
            )
            if result:
                row = result[0]
                bill.id = row['id']
                bill.generated_date = row['generated_date']
                logger.info(f"Created bill for tenant: {bill.tenant_id}")
                return bill
        except Exception as e:
            logger.error(f"Failed to create bill: {e}")
        return None
    
    @staticmethod
    def get_by_tenant(tenant_id: str) -> List[Bill]:
        """Get all bills for a tenant."""
        query = """
            SELECT * FROM bills 
            WHERE tenant_id = ? 
            ORDER BY generated_date DESC
        """
        try:
            result = db_manager.execute_query(query, (tenant_id,), fetch=1)
            return [Bill(**dict(row)) for row in result]
        except Exception as e:
            logger.error(f"Failed to get bills for tenant {tenant_id}: {e}")
            return []
    
    @staticmethod
    def mark_as_paid(bill_id: int, payment_date: datetime = None) -> bool:
        """Mark a bill as paid."""
        if payment_date is None:
            payment_date = datetime.now()
        
        query = """
            UPDATE bills 
            SET bill_status = 'paid', paid_date = ? 
            WHERE id = ?
        """
        try:
            rows_affected = db_manager.execute_query(query, (payment_date, bill_id))
            if rows_affected > 0:
                logger.info(f"Bill {bill_id} marked as paid")
                return 1
        except Exception as e:
            logger.error(f"Failed to mark bill {bill_id} as paid: {e}")
        return 0

class SystemSettingRepository:
    """Repository for system settings operations."""
    
    @staticmethod
    def get_setting(key: str) -> Optional[str]:
        """Get a system setting value."""
        query = "SELECT setting_value FROM system_settings WHERE setting_key = ?"
        try:
            result = db_manager.execute_query(query, (key,), fetch=1)
            return result[0]['setting_value'] if result else None
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            return None
    
    @staticmethod
    def set_setting(key: str, value: str, description: str = None) -> bool:
        """Set a system setting value."""
        query = """
            INSERT INTO system_settings (setting_key, setting_value, description)
            VALUES (?, ?, ?)
            ON CONFLICT (setting_key) 
            DO UPDATE SET setting_value = ?, description = COALESCE(?, system_settings.description)
        """
        try:
            db_manager.execute_query(query, (key, value, description, value, description))
            logger.info(f"Updated setting {key} = {value}")
            return 1
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return 0
    
    @staticmethod
    def get_all_settings() -> Dict[str, str]:
        """Get all system settings."""
        query = "SELECT setting_key, setting_value FROM system_settings"
        try:
            result = db_manager.execute_query(query, fetch=1)
            return {row['setting_key']: row['setting_value'] for row in result}
        except Exception as e:
            logger.error(f"Failed to get all settings: {e}")
            return {}
