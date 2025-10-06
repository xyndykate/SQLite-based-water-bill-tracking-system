# Water Bill Tracking System - SQLite Edition

## 📋 Project Overview

A complete water bill tracking system for apartment tenants using SQLite database for easy deployment.

**Status**: ✅ **Fully Operational & Production Ready**

---

## 🚀 Quick Start

```bash
# 1. Setup database (first time only)
python db_utils.py setup

# 2. Run demo to add sample data
python demo.py

# 3. View system status
python main.py

# 4. View database contents
python view_db.py
```

---

## 📁 Project Structure

### Core Application Files

| File | Purpose |
|------|---------|
| `main.py` | System verification & status display |
| `database.py` | SQLite connection manager |
| `models.py` | Data models & repositories (12.9 KB) |
| `services.py` | Business logic layer (13.5 KB) |
| `db_utils.py` | Database setup & maintenance utilities |

### Demo & Testing

| File | Purpose |
|------|---------|
| `demo.py` | Interactive system demonstration with sample data |
| `view_db.py` | SQLite database viewer & query tool |

### Database

| File | Purpose |
|------|---------|
| `water_bill.db` | SQLite database (61 KB) |
| `database_schema_sqlite.sql` | Complete database schema |

### Configuration

| File | Purpose |
|------|---------|
| `.env` | Local configuration (not in git) |
| `.env.example` | Configuration template |
| `requirements.txt` | Python dependencies |

---

## 🎯 Key Features

✅ **Tenant Management** - Add, update, remove, list tenants  
✅ **Water Reading Tracking** - Record and view meter readings  
✅ **Automated Bill Generation** - Calculate bills from readings  
✅ **Payment Tracking** - Mark bills as paid/unpaid  
✅ **Reporting** - Tenant summaries, outstanding bills  
✅ **System Settings** - Configurable rates and currency  
✅ **Database Views** - Pre-built queries for reporting  
✅ **No External Database** - SQLite built into Python  

---

## 📊 Database Schema

### Tables (5)

- **tenants** - Tenant information (ID, name, apartment, contact)
- **water_readings** - Meter readings with timestamps
- **bills** - Generated bills with amounts and status
- **system_settings** - Configurable system parameters
- **sqlite_sequence** - Auto-increment tracking

### Views (2)

- **tenant_summary** - Aggregated tenant statistics
- **monthly_consumption** - Usage trends

---

## 💻 Usage Examples

### View System Status

```bash
python main.py
```

Shows:

- Active tenants count
- Water readings per tenant
- Bills generated
- System settings

### Run Demo

```bash
python demo.py```
Adds 3 sample tenants with readings and generates bills.

### View Database

```bash
# View all data
python view_db.py

# Interactive SQL mode
python view_db.py query
```

### Database Setup

```bash
# Initialize database
python db_utils.py setup

# Verify database
python db_utils.py verify
```

---

## 🔧 API Usage (Python)

```python
from services import WaterBillService

service = WaterBillService()

# Add a tenant
service.add_tenant("T004", "Alice Wonder", "Apt 4A", "555-1234", "alice@example.com")

# Add water reading
service.add_water_reading("T004", 1000.0)

# Calculate bill
bill_data = service.calculate_bill("T004")
print(f"Amount: ${bill_data['total_amount']:.2f}")

# Generate and save bill
bill = service.generate_bill("T004", due_days=30)
print(f"Bill #{bill.id} generated")

# Mark as paid
service.mark_bill_paid(bill.id)

# Get summaries
summaries = service.get_tenant_summary()
outstanding = service.get_outstanding_bills()
```

---

## 🗄️ Viewing the Database

### Method 1: Python Script (Built-in)

```bash
python view_db.py        # View all data
python view_db.py query  # Interactive SQL
```

### Method 2: DB Browser for SQLite (GUI)

1. Download from: [https://sqlitebrowser.org/dl/](https://sqlitebrowser.org/dl/)
2. Open `water_bill.db`
3. Browse tables visually

### Method 3: VS Code Extension

1. Install "SQLite" extension
2. Right-click `water_bill.db` → "Open Database"

---

## ⚙️ Configuration

Edit `.env` file to configure:

```ini
# Database
DATABASE_PATH=water_bill.db

# Billing Settings
DEFAULT_RATE_PER_UNIT=2.50
DEFAULT_CURRENCY=USD
BILLING_CYCLE_DAYS=30
```

---

## 📈 Current Database Status

**As of last update:**

- **3 Tenants**: John Doe, Jane Smith, Bob Johnson
- **18 Water Readings**: Multiple readings per tenant
- **3 Bills**: Generated and ready
- **Settings**: $2.50/unit, USD currency
- **Database Size**: 61 KB

---

## 🛠️ Technical Details

### Architecture

- **Repository Pattern** - Clean data access layer
- **Service Layer** - Business logic encapsulation
- **Transaction Support** - ACID compliance
- **Connection Pooling** - Efficient resource management

### Database Features

- Foreign key constraints
- Indexed queries for performance
- Automated triggers
- Pre-built views for reporting

### Requirements

- Python 3.7+
- SQLite (built into Python)
- Optional: python-dotenv

---

## 🔄 Migration Notes

**Converted from PostgreSQL to SQLite:**

- ✅ Removed psycopg2 dependency
- ✅ Changed placeholder syntax: `%s` → `?`
- ✅ Updated boolean values: `TRUE/FALSE` → `1/0`
- ✅ Fixed date/datetime handling
- ✅ All functionality preserved

---

## 📝 Useful SQL Queries

```sql
-- View all tenants with latest readings
SELECT t.name, t.apartment_number, 
       MAX(w.reading_date) as last_reading,
       MAX(w.reading_units) as last_value
FROM tenants t
LEFT JOIN water_readings w ON t.tenant_id = w.tenant_id
GROUP BY t.tenant_id;

-- View unpaid bills
SELECT b.id, t.name, b.total_amount, b.due_date
FROM bills b
JOIN tenants t ON b.tenant_id = t.tenant_id
WHERE b.bill_status != 'paid';

-- Tenant consumption summary
SELECT * FROM tenant_summary;
```

---

## 🎉 Project History

1. **Initial Development** - JSON-based file storage system
2. **Enterprise Upgrade** - PostgreSQL with full schema
3. **Simplification** - Converted to SQLite for easy deployment
4. **Bug Fixes** - Cleaned up redundant files and fixed issues
5. **Current State** - Production-ready SQLite system

---

## 📍 File Locations

- **Database**: `C:\Users\ADMIN\projects\water_bill_module\water_bill.db`
- **Configuration**: `.env`
- **Schema**: `database_schema_sqlite.sql`

---

## 🚦 System Status Indicators

Run `python main.py` to see:

✅ **Database Ready** - Connection successful  
✅ **Tenants Active** - Count of active tenants  
✅ **Readings Recorded** - Total reading count  
✅ **Bills Generated** - Outstanding bill count  
✅ **Settings Configured** - Rate and currency  

---

## 💡 Tips

- Run `python demo.py` to populate with sample data
- Use `python view_db.py query` for custom SQL queries
- Check `.env` file for configuration options
- Database is automatically backed up by `db_utils.py`

---

## 📞 Support

For issues or questions:

1. Check `HOW_TO_VIEW_DATABASE.md` for database viewing help
2. Run `python db_utils.py setup` to reset database
3. Check system status with `python main.py`

---

**Last Updated**: October 6, 2025  
**Version**: 2.0 (SQLite Edition)  
**Status**: ✅ Production Ready
