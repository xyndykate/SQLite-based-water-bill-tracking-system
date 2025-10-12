"""
A simple GUI for the Water Bill Tracking System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from services import WaterBillService
from datetime import datetime
import re

class WaterBillGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Water Bill Management System")
        self.service = WaterBillService()
        
        # Set window size and make it non-resizable
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.tenant_tab = ttk.Frame(self.notebook)
        self.readings_tab = ttk.Frame(self.notebook)
        self.bills_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tenant_tab, text='Manage Tenants')
        self.notebook.add(self.readings_tab, text='Water Readings')
        self.notebook.add(self.bills_tab, text='View Bills')
        
        # Initialize tabs
        self.setup_tenant_tab()
        self.setup_readings_tab()
        self.setup_bills_tab()
        
        # Refresh data
        self.refresh_all_data()
    
    def setup_tenant_tab(self):
        # Left Frame - Add Tenant Form
        left_frame = ttk.LabelFrame(self.tenant_tab, text="Add New Tenant")
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Tenant Form
        labels = ['Tenant ID:', 'Name:', 'Apartment:', 'Phone:', 'Email:']
        self.tenant_entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = ttk.Entry(left_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.tenant_entries[label] = entry
        
        ttk.Button(left_frame, text="Add Tenant", command=self.add_tenant).grid(
            row=len(labels), column=0, columnspan=2, pady=10
        )
        
        # Right Frame - Tenant List
        right_frame = ttk.LabelFrame(self.tenant_tab, text="Existing Tenants")
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Tenant Treeview
        self.tenant_tree = ttk.Treeview(right_frame, columns=('ID', 'Name', 'Apartment', 'Phone', 'Email'), 
                                      show='headings', height=15)
        
        # Set column headings
        for col in self.tenant_tree['columns']:
            self.tenant_tree.heading(col, text=col)
            self.tenant_tree.column(col, width=100)
        
        self.tenant_tree.pack(padx=5, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_tenants).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_tenant, style='Danger.TButton').pack(side='left', padx=5)
    
    def setup_readings_tab(self):
        # Left Frame - Add Reading Form
        left_frame = ttk.LabelFrame(self.readings_tab, text="Add Water Reading")
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Tenant Selection
        ttk.Label(left_frame, text="Select Tenant:").grid(row=0, column=0, padx=5, pady=5)
        self.tenant_combo = ttk.Combobox(left_frame, width=27)
        self.tenant_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Reading Details
        ttk.Label(left_frame, text="Reading (Units):").grid(row=1, column=0, padx=5, pady=5)
        self.reading_entry = ttk.Entry(left_frame, width=30)
        self.reading_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(left_frame, width=30)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Notes:").grid(row=3, column=0, padx=5, pady=5)
        self.notes_entry = ttk.Entry(left_frame, width=30)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(left_frame, text="Add Reading", command=self.add_reading).grid(
            row=4, column=0, columnspan=2, pady=10
        )
        
        # Right Frame - Readings List
        right_frame = ttk.LabelFrame(self.readings_tab, text="Recent Readings")
        right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        
        # Readings Treeview
        self.readings_tree = ttk.Treeview(right_frame, 
            columns=('Date', 'Tenant', 'Apartment', 'Reading', 'Notes'),
            show='headings', height=15
        )
        
        # Set column headings
        for col in self.readings_tree['columns']:
            self.readings_tree.heading(col, text=col)
            self.readings_tree.column(col, width=100)
        
        self.readings_tree.pack(padx=5, pady=5)
        
        # Refresh button
        ttk.Button(right_frame, text="Refresh", command=self.refresh_readings).pack(pady=5)
    
    def setup_bills_tab(self):
        # Top Frame - Generate Bill
        top_frame = ttk.LabelFrame(self.bills_tab, text="Generate New Bill")
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Tenant Selection
        ttk.Label(top_frame, text="Select Tenant:").grid(row=0, column=0, padx=5, pady=5)
        self.bill_tenant_combo = ttk.Combobox(top_frame, width=27)
        self.bill_tenant_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(top_frame, text="Generate Bill", command=self.generate_bill).grid(
            row=0, column=2, padx=20, pady=5
        )
        
        # Bottom Frame - Bills List
        bottom_frame = ttk.LabelFrame(self.bills_tab, text="Recent Bills")
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Bills Treeview
        self.bills_tree = ttk.Treeview(bottom_frame, 
            columns=('Bill ID', 'Tenant', 'Period', 'Units', 'Amount', 'Status'),
            show='headings', height=15
        )
        
        # Set column headings
        for col in self.bills_tree['columns']:
            self.bills_tree.heading(col, text=col)
            self.bills_tree.column(col, width=100)
        
        self.bills_tree.pack(padx=5, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_bills).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Mark as Paid", command=self.mark_bill_paid).pack(side='left', padx=5)
    
    def add_tenant(self):
        try:
            # Get values from entries
            tenant_data = {
                'tenant_id': self.tenant_entries['Tenant ID:'].get().strip(),
                'name': self.tenant_entries['Name:'].get().strip(),
                'apartment_number': self.tenant_entries['Apartment:'].get().strip(),
                'phone': self.tenant_entries['Phone:'].get().strip(),
                'email': self.tenant_entries['Email:'].get().strip()
            }
            
            # Validate required fields
            if not all([tenant_data['tenant_id'], tenant_data['name'], tenant_data['apartment_number']]):
                raise ValueError("Tenant ID, Name, and Apartment are required!")
            
            # Validate email format if provided
            if tenant_data['email'] and not re.match(r"[^@]+@[^@]+\.[^@]+", tenant_data['email']):
                raise ValueError("Invalid email format!")
            
            # Add tenant using service
            tenant = self.service.add_tenant(**tenant_data)
            
            # Clear form
            for entry in self.tenant_entries.values():
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Tenant {tenant.name} added successfully!")
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def add_reading(self):
        try:
            # Get selected tenant
            tenant_id = self.tenant_combo.get().split(' - ')[0]
            
            # Validate reading
            try:
                reading_units = float(self.reading_entry.get())
                if reading_units < 0:
                    raise ValueError
            except ValueError:
                raise ValueError("Reading must be a positive number!")
            
            # Validate date
            date_str = self.date_entry.get()
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format! Use YYYY-MM-DD")
            
            # Add reading
            reading = self.service.add_water_reading(
                tenant_id=tenant_id,
                reading_units=reading_units,
                reading_date=date_str,
                notes=self.notes_entry.get()
            )
            
            # Clear form
            self.reading_entry.delete(0, tk.END)
            self.notes_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Reading added successfully!")
            self.refresh_readings()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_bill(self):
        try:
            # Get selected tenant
            tenant_id = self.bill_tenant_combo.get().split(' - ')[0]
            
            # Get last two readings
            readings = self.service.get_tenant_readings(tenant_id)
            if len(readings) < 2:
                raise ValueError("Need at least two readings to generate a bill!")
            
            # Generate bill from last two readings
            bill = self.service.generate_bill(
                tenant_id=tenant_id,
                start_reading_id=readings[-2].id,
                end_reading_id=readings[-1].id
            )
            
            messagebox.showinfo("Success", 
                f"Bill generated successfully!\n"
                f"Amount: ${bill.total_amount:.2f}\n"
                f"Period: {bill.bill_period_start} to {bill.bill_period_end}"
            )
            
            self.refresh_bills()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def mark_bill_paid(self):
        try:
            selected_item = self.bills_tree.selection()[0]
            bill_id = int(self.bills_tree.item(selected_item)['values'][0])
            
            self.service.mark_bill_paid(bill_id)
            messagebox.showinfo("Success", "Bill marked as paid!")
            self.refresh_bills()
            
        except IndexError:
            messagebox.showerror("Error", "Please select a bill first!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def refresh_tenants(self):
        # Clear existing items
        for item in self.tenant_tree.get_children():
            self.tenant_tree.delete(item)
        
        # Fetch and display tenants
        tenants = self.service.get_all_tenants()
        for tenant in tenants:
            self.tenant_tree.insert('', 'end', values=(
                tenant.tenant_id,
                tenant.name,
                tenant.apartment_number,
                tenant.phone or '',
                tenant.email or ''
            ))
    
    def refresh_readings(self):
        # Clear existing items
        for item in self.readings_tree.get_children():
            self.readings_tree.delete(item)
        
        # Fetch and display readings
        for tenant in self.service.get_all_tenants():
            readings = self.service.get_tenant_readings(tenant.tenant_id)
            for reading in readings:
                self.readings_tree.insert('', 'end', values=(
                    reading.reading_date,
                    tenant.name,
                    tenant.apartment_number,
                    f"{reading.reading_units:.1f}",
                    reading.notes or ''
                ))
    
    def refresh_bills(self):
        # Clear existing items
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        
        # Fetch and display bills
        for tenant in self.service.get_all_tenants():
            bills = self.service.get_tenant_bills(tenant.tenant_id)
            for bill in bills:
                self.bills_tree.insert('', 'end', values=(
                    bill.id,
                    tenant.name,
                    f"{bill.bill_period_start} to {bill.bill_period_end}",
                    f"{bill.units_consumed:.1f}",
                    f"${bill.total_amount:.2f}",
                    bill.bill_status.upper()
                ))
    
    def refresh_tenant_combos(self):
        # Get all tenants for comboboxes
        tenants = self.service.get_all_tenants()
        tenant_list = [f"{t.tenant_id} - {t.name} ({t.apartment_number})" for t in tenants]
        
        # Update comboboxes
        self.tenant_combo['values'] = tenant_list
        self.bill_tenant_combo['values'] = tenant_list
        
        if tenant_list:
            self.tenant_combo.set(tenant_list[0])
            self.bill_tenant_combo.set(tenant_list[0])
    
    def delete_tenant(self):
        try:
            # Get selected tenant
            selected_item = self.tenant_tree.selection()[0]
            tenant_id = self.tenant_tree.item(selected_item)['values'][0]
            tenant_name = self.tenant_tree.item(selected_item)['values'][1]
            
            # Confirm deletion
            if not messagebox.askyesno("Confirm Delete", 
                f"Are you sure you want to delete tenant {tenant_name}?\n\n"
                "WARNING: This will also delete all associated readings and bills!\n"
                "This action cannot be undone."):
                return
            
            # Check for existing bills and readings
            readings = self.service.get_tenant_readings(tenant_id)
            bills = self.service.get_tenant_bills(tenant_id)
            
            if readings or bills:
                if not messagebox.askyesno("Warning", 
                    f"This tenant has:\n"
                    f"- {len(readings)} water readings\n"
                    f"- {len(bills)} bills\n\n"
                    "All related data will be permanently deleted.\n"
                    "Do you want to continue?"):
                    return
            
            # Delete tenant using service layer
            self.service.delete_tenant(tenant_id)
            
            messagebox.showinfo("Success", f"Tenant {tenant_name} and all related data deleted successfully!")
            
            # Refresh all data
            self.refresh_all_data()
            
        except IndexError:
            messagebox.showerror("Error", "Please select a tenant to delete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete tenant: {str(e)}")
    
    def refresh_all_data(self):
        self.refresh_tenants()
        self.refresh_readings()
        self.refresh_bills()
        self.refresh_tenant_combos()

def main():
    root = tk.Tk()
    
    # Configure style for danger button
    style = ttk.Style()
    style.configure('Danger.TButton', foreground='red')
    app = WaterBillGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()