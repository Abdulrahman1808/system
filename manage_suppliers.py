import customtkinter as ctk
from tkinter import messagebox
from ui_elements import show_error, show_success
from data_handler import (
    insert_document, update_document, delete_document,
    load_data, save_data, get_next_id
)
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label, create_styled_option_menu
)

class ManageSuppliers:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.suppliers = []

    def manage_suppliers(self):
        """Create a modern suppliers management interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Create header
        header_frame = create_styled_frame(main_frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        # Title and back button
        title_frame = ctk.CTkFrame(header_frame, fg_color='transparent')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        back_btn = create_styled_button(
            title_frame,
            text="← Back",
            style='outline',
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.back_callback
        )
        back_btn.pack(side='left')
        
        title_label = create_styled_label(
            title_frame,
            text=self.LANGUAGES[self.current_language].get("supplier_management", "Supplier Management"),
            style='heading'
        )
        title_label.pack(side='left', padx=20)
        
        # Load suppliers
        self.suppliers = load_data("suppliers")

        # Summary cards
        summary_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_suppliers = len(self.suppliers)
        active_suppliers = len([s for s in self.suppliers if s.get('status') == 'Active'])
        inactive_suppliers = len([s for s in self.suppliers if s.get('status') == 'Inactive'])
        
        # Create summary cards
        summary_cards = [
            ("total_suppliers", "Total Suppliers", total_suppliers),
            ("active_suppliers", "Active Suppliers", active_suppliers),
            ("inactive_suppliers", "Inactive Suppliers", inactive_suppliers)
        ]
        
        for i, (key, default_text, value) in enumerate(summary_cards):
            card = create_styled_frame(summary_frame, style='card')
            card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
            
            label = create_styled_label(
                card,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            label.pack(pady=(20, 5))
            
            value_label = create_styled_label(
                card,
                text=str(value),
                style='heading'
            )
            value_label.pack(pady=(0, 20))
        
        # Search and filter section
        filter_frame = create_styled_frame(main_frame, style='card')
        filter_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        search_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        search_frame.pack(fill='x', padx=20, pady=20)
        
        search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search", "Search suppliers..."),
            height=40
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        filter_btn = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("filter", "Filter"),
            style='outline',
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        filter_btn.pack(side='right')
        
        # Add new supplier button
        add_btn = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("add_supplier", "Add Supplier"),
            style='primary',
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.add_new_supplier
        )
        add_btn.pack(side='right', padx=10)
        
        # Suppliers table
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create scrollable frame for the table
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        
        # Table headers
        headers = [
            ("supplier_name", "Supplier Name"),
            ("contact", "Contact"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("status", "Status"),
            ("actions", "Actions")
        ]
        
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Suppliers list
        for i, supplier in enumerate(self.suppliers, 1):
            # Supplier details
            name_label = create_styled_label(
                scrollable_table,
                text=supplier.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            contact_label = create_styled_label(
                scrollable_table,
                text=supplier.get('contact', ''),
                style='body'
            )
            contact_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            email_label = create_styled_label(
                scrollable_table,
                text=supplier.get('email', ''),
                style='body'
            )
            email_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            phone_label = create_styled_label(
                scrollable_table,
                text=supplier.get('phone', ''),
                style='body'
            )
            phone_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            status_label = create_styled_label(
                scrollable_table,
                text=supplier.get('status', 'Active'),
                style='body'
            )
            status_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            
            edit_btn = create_styled_button(
                actions_frame,
                text="Edit",
                style='outline',
                width=80,
                command=lambda s=supplier: self.edit_supplier(s['name'])
            )
            edit_btn.pack(side='left', padx=5)
            
            delete_btn = create_styled_button(
                actions_frame,
                text="Delete",
                style='outline',
                width=80,
                command=lambda s=supplier: self.delete_supplier(s['name'])
            )
            delete_btn.pack(side='left', padx=5)

    def add_new_supplier(self):
        """Add a new supplier"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Supplier")
        dialog.geometry("400x500")
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set()
        
        # Create form
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("add_supplier", "Add Supplier"),
            style='heading'
        )
        title_label.pack(pady=20)
        
        # Supplier name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("supplier_name", "Supplier Name"),
            style='subheading'
        )
        name_label.pack(pady=(0, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Contact person
        contact_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("contact", "Contact Person"),
            style='subheading'
        )
        contact_label.pack(pady=(0, 5))
        
        contact_entry = create_styled_entry(form_frame)
        contact_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Email
        email_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("email", "Email"),
            style='subheading'
        )
        email_label.pack(pady=(0, 5))
        
        email_entry = create_styled_entry(form_frame)
        email_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Phone
        phone_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("phone", "Phone"),
            style='subheading'
        )
        phone_label.pack(pady=(0, 5))
        
        phone_entry = create_styled_entry(form_frame)
        phone_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_menu = create_styled_option_menu(
            form_frame,
            values=["Active", "Inactive"]
        )
        status_menu.pack(fill='x', padx=20, pady=(0, 20))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_supplier(
                dialog,
                name_entry.get(),
                contact_entry.get(),
                email_entry.get(),
                phone_entry.get(),
                status_menu.get()
            )
        )
        save_button.pack(fill='x', padx=20, pady=(0, 20))

    def save_supplier(self, dialog, name, contact, email, phone, status):
        """Save a new supplier"""
        if not all([name, contact, email, phone]):
            show_error("Please fill all fields", self.current_language)
            return
            
        # Create new supplier
        supplier = {
            'id': str(len(self.suppliers) + 1),
            'name': name,
            'contact': contact,
            'email': email,
            'phone': phone,
            'status': status
        }
        
        # Add to suppliers list
        self.suppliers.append(supplier)
        
        # Save to MongoDB
        save_data("suppliers", self.suppliers)
        
        # Close dialog and refresh
        dialog.destroy()
        self.manage_suppliers()
        show_success(self.LANGUAGES[self.current_language].get("supplier_added", "Supplier added successfully"), self.current_language)

    def edit_supplier(self, supplier_name):
        """Handle editing a supplier"""
        # Implement edit functionality
        pass
        
    def delete_supplier(self, supplier_name):
        """Delete a supplier"""
        if not supplier_name:
            return
            
        # Find and remove supplier
        self.suppliers = [s for s in self.suppliers if s['name'] != supplier_name]
        
        # Save to MongoDB
        save_data("suppliers", self.suppliers)
        
        # Refresh the view
        self.manage_suppliers()
        show_success(self.LANGUAGES[self.current_language].get("supplier_deleted", "Supplier deleted successfully"), self.current_language)

    def refresh_suppliers_list(self):
        """Refresh the suppliers treeview"""
        self.suppliers = load_data("suppliers")
        self.filtered_suppliers = self.suppliers  # Initialize filtered suppliers
        self.update_suppliers_tree()

    def update_suppliers_tree(self):
        """Update the suppliers treeview with filtered suppliers"""
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        for supplier in self.filtered_suppliers:
            self.suppliers_tree.insert("", "end", values=(
                supplier.get("Name", ""),
                supplier.get("Contact", ""),
                supplier.get("Email", "")
            ))

    def add_supplier_dialog(self):
        """Show dialog to add a new supplier"""
        self.add_supplier_window = ctk.CTkToplevel(self.root)
        self.add_supplier_window.title(self.LANGUAGES[self.current_language]["add_supplier"])
        self.add_supplier_window.geometry("500x400")
        self.add_supplier_window.configure(fg_color="#1f1f1f")

        title_label = ctk.CTkLabel(
            self.add_supplier_window, 
            text=self.LANGUAGES[self.current_language]["add_supplier"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=20)

        fields = [
            ("Name:", "entry"),
            ("Contact:", "entry"),
            ("Email:", "entry"),
            ("Phone:", "entry"),
            ("Status:", "option")
        ]

        self.supplier_entries = []
        for label, field_type in fields:
            frame = ctk.CTkFrame(self.add_supplier_window, fg_color="#1f1f1f")
            frame.pack(fill='x', padx=30, pady=10)

            label_widget = ctk.CTkLabel(
                frame, 
                text=label, 
                text_color="white", 
                font=ctk.CTkFont(size=14)
            )
            label_widget.pack(side='left', padx=10)

            if field_type == "entry":
                entry = ctk.CTkEntry(frame, height=35)
                entry.pack(side='right', expand=True, fill='x', padx=10)
                self.supplier_entries.append(entry)
            elif field_type == "option":
                status_menu = ctk.CTkOptionMenu(
                    frame,
                    values=["Active", "Inactive"],
                    height=35
                )
                status_menu.pack(side='right', expand=True, fill='x', padx=10)
                self.supplier_entries.append(status_menu)

        save_button = ctk.CTkButton(
            self.add_supplier_window,
            text=self.LANGUAGES[self.current_language]["save"],
            height=40,
            font=ctk.CTkFont(size=14),
            command=lambda: self.save_supplier(
                self.add_supplier_window,
                self.supplier_entries[0].get(),
                self.supplier_entries[1].get(),
                self.supplier_entries[2].get(),
                self.supplier_entries[3].get(),
                self.supplier_entries[4].get()
            )
        )
        save_button.pack(pady=30, padx=30, fill='x')

    def edit_supplier(self):
        """Edit an existing supplier"""
        selected = self.suppliers_tree.selection()
        if not selected:
            show_error(self.LANGUAGES[self.current_language]["please_fill"], self.current_language)
            return

        item = self.suppliers_tree.item(selected[0])
        supplier_name = item['values'][0]

        supplier = None
        for s in self.suppliers:
            if s.get("Name") == supplier_name:
                supplier = s
                break

        if not supplier:
            show_error(self.LANGUAGES[self.current_language]["supplier_not_found"], self.current_language)
            return

        self.edit_supplier_window = ctk.CTkToplevel(self.root)
        self.edit_supplier_window.title(self.LANGUAGES[self.current_language]["edit_supplier"])
        self.edit_supplier_window.geometry("400x300")
        self.edit_supplier_window.configure(fg_color="#1f1f1f")

        title_label = ctk.CTkLabel(self.edit_supplier_window, text=self.LANGUAGES[self.current_language]["edit_supplier"],
                                   font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        title_label.pack(pady=10)

        fields = [
            ("Name:", "entry", supplier.get("Name", "")),
            ("Contact:", "entry", supplier.get("Contact", "")),
            ("Email:", "entry", supplier.get("Email", ""))
        ]

        self.edit_entries = []
        for label, field_type, value in fields:
            frame = ctk.CTkFrame(self.edit_supplier_window, fg_color="#1f1f1f")
            frame.pack(fill='x', padx=20, pady=5)

            label_widget = ctk.CTkLabel(frame, text=label, text_color="white", font=ctk.CTkFont(size=12))
            label_widget.pack(side='left', padx=5)

            if field_type == "entry":
                entry = ctk.CTkEntry(frame)
                entry.insert(0, value)
                entry.pack(side='right', expand=True, fill='x', padx=5)
                self.edit_entries.append(entry)

        edit_btn = ctk.CTkButton(self.edit_supplier_window, text=self.LANGUAGES[self.current_language]["edit_supplier"],
                                 command=lambda: self.update_supplier(supplier))
        edit_btn.pack(pady=20)

    def update_supplier(self, original_supplier):
        """Update an existing supplier"""
        values = [entry.get().strip() for entry in self.edit_entries]

        if not all(values):
            show_error(self.LANGUAGES[self.current_language]["please_fill"], self.current_language)
            return

        update_data = {
            "Name": values[0],
            "Contact": values[1],
            "Email": values[2]
        }

        success = update_document("suppliers", original_supplier["_id"], update_data)
        if success:
            self.refresh_suppliers_list()
            self.edit_supplier_window.destroy()
            show_success(self.LANGUAGES[self.current_language]["supplier_updated"], self.current_language)
        else:
            show_error(self.LANGUAGES[self.current_language]["error"], self.current_language)

    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def filter_suppliers(self, *args):
        """Filter suppliers based on search query"""
        query = self.search_var.get().lower()
        if not query:
            self.filtered_suppliers = self.suppliers
        else:
            self.filtered_suppliers = [s for s in self.suppliers if query in s.get("Name", "").lower() or
                                       query in s.get("Contact", "").lower() or
                                       query in s.get("Email", "").lower()]
        self.update_suppliers_tree()
