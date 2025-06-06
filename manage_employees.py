import customtkinter as ctk
from tkinter import ttk, messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id, import_from_excel
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label
)

class ManageEmployees:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.employees = load_data("employees") or []

    def refresh_employees(self):
        """Refresh the employees list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            if import_from_excel('employees'):
                print("[DEBUG] Successfully imported data from Excel")
            else:
                print("[DEBUG] No Excel data to import or import failed")

            # Load employees from database
            self.employees = load_data("employees") or []
            print(f"[DEBUG] Loaded employees count: {len(self.employees)}")
            print(f"[DEBUG] Loaded employees: {self.employees}")
            
            # Refresh the display
            self.manage_employees()
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            show_error(f"Error refreshing employees: {str(e)}", self.current_language)

    def manage_employees(self):
        """Create a modern employee management interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = create_styled_frame(main_frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        back_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("back", "Back"),
            style='outline',
            command=self.back_callback
        )
        back_button.pack(side='left', padx=20, pady=20)
        
        title_label = create_styled_label(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("manage_employees", "Manage Employees"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_employees
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_employees = len(self.employees)
        active_employees = len([e for e in self.employees if e.get('status') == 'active'])
        on_leave = len([e for e in self.employees if e.get('status') == 'on_leave'])
        
        # Create summary cards
        summary_cards = [
            ("total_employees", "Total Employees", total_employees),
            ("active_employees", "Active Employees", active_employees),
            ("on_leave", "On Leave", on_leave)
        ]
        
        for i, (key, default_text, value) in enumerate(summary_cards):
            card = create_styled_frame(summary_frame, style='card')
            card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
            
            label = create_styled_label(
                card,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            label.pack(pady=(10, 5))
            
            value_label = create_styled_label(
                card,
                text=str(value),
                style='heading'
            )
            value_label.pack(pady=(0, 10))
        
        # Search and filter section
        search_frame = create_styled_frame(main_frame, style='card')
        search_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search_employees", "Search employees...")
        )
        search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        
        filter_button = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("filter", "Filter"),
            style='outline'
        )
        filter_button.pack(side='right', padx=20, pady=20)
        
        add_button = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("add_employee", "Add Employee"),
            style='primary',
            command=self.add_employee
        )
        add_button.pack(side='right', padx=20, pady=20)
        
        # Employees table
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Table headers
        headers = [
            ("employee_name", "Name"),
            ("position", "Position"),
            ("contact", "Contact"),
            ("status", "Status"),
            ("actions", "Actions")
        ]
        
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                table_frame,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Employees list
        for i, employee in enumerate(self.employees, 1):
            # Employee details
            name_label = create_styled_label(
                table_frame,
                text=employee.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            position_label = create_styled_label(
                table_frame,
                text=employee.get('position', ''),
                style='body'
            )
            position_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            contact_label = create_styled_label(
                table_frame,
                text=employee.get('contact', ''),
                style='body'
            )
            contact_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            status_label = create_styled_label(
                table_frame,
                text=employee.get('status', 'active'),
                style='body'
            )
            status_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(table_frame, style='card')
            actions_frame.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda e=employee: self.edit_employee(e)
            )
            edit_button.pack(side='left', padx=5)
            
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='outline',
                width=80,
                command=lambda e=employee: self.delete_employee(e)
            )
            delete_button.pack(side='left', padx=5)

    def add_employee(self):
        """Add a new employee"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("add_employee", "Add Employee"))
        dialog.geometry("400x500")
        
        # Employee form
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("employee_name", "Name"),
            style='subheading'
        )
        name_label.pack(pady=(20, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Position
        position_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("position", "Position"),
            style='subheading'
        )
        position_label.pack(pady=(0, 5))
        
        position_entry = create_styled_entry(form_frame)
        position_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Contact
        contact_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("contact", "Contact"),
            style='subheading'
        )
        contact_label.pack(pady=(0, 5))
        
        contact_entry = create_styled_entry(form_frame)
        contact_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_entry = create_styled_entry(form_frame)
        status_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_employee(
                dialog,
                name_entry.get(),
                position_entry.get(),
                contact_entry.get(),
                status_entry.get()
            )
        )
        save_button.pack(pady=20)

    def edit_employee(self, employee):
        """Edit an existing employee"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("edit_employee", "Edit Employee"))
        dialog.geometry("400x500")
        
        # Employee form
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("employee_name", "Name"),
            style='subheading'
        )
        name_label.pack(pady=(20, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, employee.get('name', ''))
        name_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Position
        position_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("position", "Position"),
            style='subheading'
        )
        position_label.pack(pady=(0, 5))
        
        position_entry = create_styled_entry(form_frame)
        position_entry.insert(0, employee.get('position', ''))
        position_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Contact
        contact_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("contact", "Contact"),
            style='subheading'
        )
        contact_label.pack(pady=(0, 5))
        
        contact_entry = create_styled_entry(form_frame)
        contact_entry.insert(0, employee.get('contact', ''))
        contact_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_entry = create_styled_entry(form_frame)
        status_entry.insert(0, employee.get('status', ''))
        status_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.update_employee(
                dialog,
                employee,
                name_entry.get(),
                position_entry.get(),
                contact_entry.get(),
                status_entry.get()
            )
        )
        save_button.pack(pady=20)

    def save_employee(self, dialog, name, position, contact, status):
        """Save a new employee"""
        if not all([name, position, contact, status]):
            show_error(self.LANGUAGES[self.current_language].get("invalid_employee", "Please fill all fields"), self.current_language)
            return

        new_employee = {
            'id': get_next_id('employees'),
            'name': name,
            'position': position,
            'contact': contact,
            'status': status
        }
        
        self.employees.append(new_employee)
        save_data("employees", self.employees)
        dialog.destroy()
        self.manage_employees()
        show_success(self.LANGUAGES[self.current_language].get("employee_added", "Employee added successfully"), self.current_language)

    def update_employee(self, dialog, employee, name, position, contact, status):
        """Update an existing employee"""
        if not all([name, position, contact, status]):
            show_error(self.LANGUAGES[self.current_language].get("invalid_employee", "Please fill all fields"), self.current_language)
            return

        employee.update({
            'name': name,
            'position': position,
            'contact': contact,
            'status': status
        })
        
        save_data("employees", self.employees)
        dialog.destroy()
        self.manage_employees()
        show_success(self.LANGUAGES[self.current_language].get("employee_updated", "Employee updated successfully"), self.current_language)

    def delete_employee(self, employee):
        """Delete an employee"""
        self.employees.remove(employee)
        save_data("employees", self.employees)
        self.manage_employees()
        show_success(self.LANGUAGES[self.current_language].get("employee_deleted", "Employee deleted successfully"), self.current_language) 