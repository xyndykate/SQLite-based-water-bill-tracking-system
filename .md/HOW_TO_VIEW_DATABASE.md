# How to View SQLite Database

## ✅ Quick Method (Just Created!)

```bash
# View all tables and data
python view_db.py

# Interactive SQL query mode
python view_db.py query
```

## 🔧 Other Methods

### 1. **DB Browser for SQLite** (Best GUI Option)
**Free desktop application with visual interface**

**Download**: https://sqlitebrowser.org/dl/

**Features**:
- ✅ View/edit tables visually
- ✅ Run SQL queries
- ✅ Export data (CSV, SQL)
- ✅ Visualize database structure
- ✅ No coding required

**Usage**:
1. Download and install DB Browser for SQLite
2. Open the program
3. Click "Open Database"
4. Navigate to: `C:\Users\ADMIN\projects\water_bill_module\water_bill.db`

---

### 2. **VS Code Extension** (If you use VS Code)

**Extension**: SQLite Viewer or SQLite

**Installation**:
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search "SQLite" or "SQLite Viewer"
4. Install "SQLite" by alexcvzz

**Usage**:
- Right-click `water_bill.db` → "Open Database"
- Click on tables to view data
- Run queries in SQL editor

---

### 3. **PowerShell/Command Line** (Built-in)

```powershell
# Open SQLite command-line (if installed)
sqlite3 water_bill.db

# Once inside:
.tables                    # List all tables
.schema tenants           # Show table structure
SELECT * FROM tenants;    # Query data
.quit                     # Exit
```

**Note**: Requires SQLite command-line tool installed

---

### 4. **Python REPL** (Quick Checks)

```python
python
>>> import sqlite3
>>> conn = sqlite3.connect('water_bill.db')
>>> cursor = conn.cursor()
>>> 
>>> # List tables
>>> cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
>>> print(cursor.fetchall())
>>> 
>>> # View tenants
>>> cursor.execute("SELECT * FROM tenants")
>>> for row in cursor.fetchall():
...     print(row)
>>> 
>>> conn.close()
>>> exit()
```

---

### 5. **Using Our Custom Viewer** (Interactive Mode)

```bash
python view_db.py query
```

Then run queries like:
```sql
SQL> SELECT * FROM tenants;
SQL> SELECT name, apartment_number FROM tenants WHERE is_active = 1;
SQL> SELECT * FROM bills WHERE bill_status = 'generated';
SQL> SELECT t.name, COUNT(w.id) as readings 
     FROM tenants t 
     LEFT JOIN water_readings w ON t.tenant_id = w.tenant_id 
     GROUP BY t.name;
SQL> exit
```

---

## 📊 Current Database Content

Your `water_bill.db` contains:

**Tables (5)**:
- `tenants` - 3 tenants (John Doe, Jane Smith, Bob Johnson)
- `water_readings` - 18 readings
- `bills` - 3 generated bills
- `system_settings` - 5 configuration settings
- `sqlite_sequence` - Auto-increment tracking

**Views (2)**:
- `tenant_summary` - Aggregated tenant data
- `monthly_consumption` - Monthly usage statistics

**Database Size**: 61 KB

---

## 🎯 Recommended Options

**For Quick Viewing**: Use `python view_db.py` ✅ (Just created!)

**For Visual Editing**: Download DB Browser for SQLite 🖥️

**For VS Code Users**: Install SQLite extension 📝

**For SQL Practice**: Use `python view_db.py query` 💻

---

## 💡 Useful SQL Queries

```sql
-- View all tenants with their latest readings
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

-- View tenant consumption summary
SELECT * FROM tenant_summary;

-- View system settings
SELECT setting_key, setting_value, description 
FROM system_settings;
```

---

## 📍 Database Location

```
C:\Users\ADMIN\projects\water_bill_module\water_bill.db
```

You can open this file with any of the tools mentioned above!
