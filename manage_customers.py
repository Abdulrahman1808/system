import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, create_styled_entry, COLORS, FONTS
# Import data handling functions
from data_handler import load_data, save_data, get_next_id
from ui_elements import show_error, show_success

class CustomerManager:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.customers = [] # We will load data here later

        # This will be the main frame for the customer management section
        self.frame = None
        self.scrollable_customer_list = None # Initialize scrollable frame

        self.sort_column = 'name' # Default sorting column
        self.sort_order = 'asc' # Default sorting order

    def manage_customers(self):
        """Create the customer management interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create the main frame for this section using styled frame
        self.frame = create_styled_frame(self.root, style='section')
        self.frame.pack(fill='both', expand=True)

        # Header frame
        header_frame = create_styled_frame(self.frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)

        # Back button
        back_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("back", "Back"),
            style='outline',
            command=self.back_callback
        )
        back_button.pack(side='left', padx=20, pady=20)

        # Title Label
        title_label = create_styled_label(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("manage_customers", "Manage Customers"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Add Customer Button
        add_customer_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("add_customer", "Add Customer"),
            style='primary',
            command=self.add_customer
        )
        add_customer_button.pack(side='right', padx=20, pady=20)

        # Search and Filter section
        search_frame = create_styled_frame(self.frame, style='card')
        search_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search_customers", "Search customers...")
        )
        self.search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_customers)

        # Filter by option menu
        filter_options = [
            self.LANGUAGES[self.current_language].get("all_fields", "All Fields"),
            self.LANGUAGES[self.current_language].get("name", "Name"),
            self.LANGUAGES[self.current_language].get("contact", "Contact Person"),
            self.LANGUAGES[self.current_language].get("email", "Email"),
            self.LANGUAGES[self.current_language].get("phone", "Phone Number"),
            self.LANGUAGES[self.current_language].get("address", "Address"),
            self.LANGUAGES[self.current_language].get("notes", "Notes")
        ]
        self.filter_option_menu = ctk.CTkOptionMenu(
            search_frame,
            values=filter_options,
            command=self.filter_customers # Trigger filter when option changes
        )
        self.filter_option_menu.set(filter_options[0]) # Set default to All Fields
        self.filter_option_menu.pack(side='left', padx=(0, 20), pady=20)

        filter_button = create_styled_button(
            search_frame,
            text=self.LANGUAGES[self.current_language].get("filter", "Filter"),
            style='outline',
            command=self.filter_customers
        )
        filter_button.pack(side='right', padx=20, pady=20)

        # Customer list/table area
        customer_list_frame = create_styled_frame(self.frame, style='card')
        customer_list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Create scrollable frame for the customer list
        self.scrollable_customer_list = ctk.CTkScrollableFrame(customer_list_frame, orientation='vertical')
        self.scrollable_customer_list.pack(fill='both', expand=True)

        # Load customer data when the section is displayed
        self.load_customers()
        # Display customers after loading
        self.display_customers()


    def load_customers(self):
        """Load customer data from the database"""
        print("[DEBUG] Loading customer data...")
        self.customers = load_data('customers') or []
        print(f"[DEBUG] Loaded {len(self.customers)} customers")


    def save_customers(self):
        """Save customer data to the database"""
        print("[DEBUG] Saving customer data...")
        save_data('customers', self.customers)
        print("[DEBUG] Customer data saved")

    def display_customers(self, customers_to_display=None):
        """Display the list of customers in the scrollable frame"""
        # Use the provided list if available, otherwise use the full list
        customer_list = customers_to_display if customers_to_display is not None else self.customers

        # Sort the customer list
        if self.sort_column:
            customer_list = sorted(customer_list, key=lambda x: x.get(self.sort_column, ''), reverse=(self.sort_order == 'desc'))

        # Clear existing list
        for widget in self.scrollable_customer_list.winfo_children():
            widget.destroy()

        if not customer_list:
            no_customers_label = create_styled_label(
                self.scrollable_customer_list,
                text=self.LANGUAGES[self.current_language].get("no_customers", "No customers found."),
                style='body'
            )
            no_customers_label.pack(pady=20)
            return

        # Table headers
        headers = [
            ("name", "Name"),
            ("contact", "Contact"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("address", "Address"),
            ("notes", "Notes"),
            ("actions", "Actions")
        ]

        # Add headers to the grid and bind click events
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                self.scrollable_customer_list,
                text=self.get_bilingual(key, default_text, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
            # Bind click event for sorting, but exclude the 'actions' column
            if key != "actions":
                header.bind('<Button-1>', lambda e, col_key=key: self.sort_by_column(col_key))
                header.configure(cursor="hand2") # Change cursor to indicate it's clickable

        # Customer list
        for i, customer in enumerate(customer_list, 1):
            # Customer details
            name_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')

            contact_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('contact', ''),
                style='body'
            )
            contact_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')

            email_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('email', ''),
                style='body'
            )
            email_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')

            phone_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('phone', ''),
                style='body'
            )
            phone_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')

            # Address
            address_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('address', ''),
                style='body'
            )
            address_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')

            # Notes
            notes_label = create_styled_label(
                self.scrollable_customer_list,
                text=customer.get('notes', ''),
                style='body'
            )
            notes_label.grid(row=i, column=5, padx=10, pady=10, sticky='w')

            # Action buttons (placeholder)
            actions_frame = create_styled_frame(self.scrollable_customer_list, style='card')
            actions_frame.grid(row=i, column=6, padx=10, pady=10, sticky='w')

            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda c=customer: self.edit_customer(c) # Placeholder
            )
            edit_button.pack(side='left', padx=5)

            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='outline',
                width=80,
                command=lambda c=customer: self.delete_customer(c) # Placeholder
            )
            delete_button.pack(side='left', padx=5)

        # Configure column weights so columns expand evenly
        for i in range(len(headers)):
            self.scrollable_customer_list.grid_columnconfigure(i, weight=1)


    def add_customer(self):
        """Open dialog to add a new customer"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("add_customer", "Add Customer"))
        dialog.geometry("400x600") # Set dialog size
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set() # Make dialog modal

        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Form frame
        form_frame = create_styled_frame(scrollable_form_frame, style='card') # Use styled frame inside scrollable
        form_frame.pack(fill='both', expand=True) # Removed padx, pady as they are on the scrollable frame

        # Title inside dialog
        title_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("add_customer", "Add New Customer"),
            style='heading'
        )
        title_label.pack(pady=20)

        # Input fields
        fields = [
            ("name", "Name"),
            ("contact", "Contact Person"),
            ("email", "Email"),
            ("phone", "Phone Number"),
            ("address", "Address"),
            ("notes", "Notes")
        ]

        self.add_customer_entries = {} # Store entry widgets

        for key, text in fields:
            label = create_styled_label(form_frame, text=self.get_bilingual(key, text, text), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            entry = create_styled_entry(form_frame)
            entry.pack(fill='x', padx=20, pady=(0, 15))
            self.add_customer_entries[key] = entry

        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_new_customer(dialog)
        )
        save_button.pack(pady=20)


    def save_new_customer(self, dialog):
        """Save the new customer data"""
        new_customer_data = {}
        for key, entry in self.add_customer_entries.items():
            new_customer_data[key] = entry.get().strip()

        # Basic validation
        if not new_customer_data.get('name'):
            show_error(self.LANGUAGES[self.current_language].get("name_required", "Customer Name is required."), self.current_language)
            return

        # Generate next ID
        new_customer_data['id'] = get_next_id('customers')

        # Add to the list
        self.customers.append(new_customer_data)

        # Save data
        self.save_customers()

        # Update display and close dialog
        self.display_customers()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get("customer_added", "Customer added successfully."), self.current_language)


    def edit_customer(self, customer):
        """Open dialog to edit an existing customer"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("edit_customer", "Edit Customer"))
        dialog.geometry("400x450") # Adjusted size for address field
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set() # Make dialog modal

        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form frame
        form_frame = create_styled_frame(scrollable_form_frame, style='card') # Use styled frame inside scrollable
        form_frame.pack(fill='both', expand=True) # Removed padx, pady as they are on the scrollable frame

        # Title inside dialog
        title_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("edit_customer", "Edit Customer"),
            style='heading'
        )
        title_label.pack(pady=20)

        # Input fields
        fields = [
            ("name", "Name"),
            ("contact", "Contact Person"),
            ("email", "Email"),
            ("phone", "Phone Number"),
            ("address", "Address"),
            ("notes", "Notes")
        ]

        self.edit_customer_entries = {} # Store entry widgets

        for key, text in fields:
            label = create_styled_label(form_frame, text=self.get_bilingual(key, text, text), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            entry = create_styled_entry(form_frame)
            entry.insert(0, customer.get(key, '')) # Pre-fill with existing data
            entry.pack(fill='x', padx=20, pady=(0, 15))
            self.edit_customer_entries[key] = entry

        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.update_customer(dialog, customer)
        )
        save_button.pack(pady=20)

        # Cancel button
        cancel_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("cancel", "Cancel"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(pady=10)

    def update_customer(self, dialog, original_customer):
        """Update an existing customer's data"""
        updated_data = {}
        for key, entry in self.edit_customer_entries.items():
            updated_data[key] = entry.get().strip()

        # Basic validation
        if not updated_data.get('name'):
            show_error(self.LANGUAGES[self.current_language].get("name_required", "Customer Name is required."), self.current_language)
            return

        # Find the customer in the list and update
        for i, customer in enumerate(self.customers):
            if customer.get('id') == original_customer.get('id'): # Assuming 'id' is the unique identifier
                self.customers[i].update(updated_data)
                break
        else:
            # Should not happen if edit_customer is called correctly
            show_error(self.LANGUAGES[self.current_language].get("customer_not_found", "Customer not found for update."), self.current_language)
            return

        # Save data
        self.save_customers()

        # Update display and close dialog
        self.display_customers()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get("customer_updated", "Customer updated successfully."), self.current_language)

    def delete_customer(self, customer):
        """Delete a customer"""
        try:
            # Remove the customer from the list
            self.customers.remove(customer)

            # Save the updated list
            self.save_customers()

            # Refresh the display
            self.display_customers()

            # Show success message
            show_success(self.LANGUAGES[self.current_language].get("customer_deleted", "Customer deleted successfully."), self.current_language)

        except ValueError:
            # Should not happen if called from display, but good to handle
            show_error(self.LANGUAGES[self.current_language].get("customer_not_found", "Customer not found for deletion."), self.current_language)
        except Exception as e:
            show_error(f"Error deleting customer: {str(e)}", self.current_language)

    def filter_customers(self, event=None):
        """Filter customers based on the search entry and selected filter option"""
        search_text = self.search_entry.get().lower()
        selected_option = self.filter_option_menu.get()

        filtered_customers = []
        if selected_option == self.LANGUAGES[self.current_language].get("all_fields", "All Fields"):
            # Filter across all fields
            filtered_customers = [customer for customer in self.customers if
                                  (customer.get('name', '').lower().find(search_text) != -1 or
                                   customer.get('contact', '').lower().find(search_text) != -1 or
                                   customer.get('email', '').lower().find(search_text) != -1 or
                                   customer.get('phone', '').lower().find(search_text) != -1 or
                                   customer.get('address', '').lower().find(search_text) != -1 or
                                   customer.get('notes', '').lower().find(search_text) != -1)]
        else:
            # Filter by selected field
            # Map language option back to data key
            field_key_map = {
                self.LANGUAGES[self.current_language].get("name", "Name"): 'name',
                self.LANGUAGES[self.current_language].get("contact", "Contact Person"): 'contact',
                self.LANGUAGES[self.current_language].get("email", "Email"): 'email',
                self.LANGUAGES[self.current_language].get("phone", "Phone Number"): 'phone',
                self.LANGUAGES[self.current_language].get("address", "Address"): 'address',
                self.LANGUAGES[self.current_language].get("notes", "Notes"): 'notes'
            }
            filter_key = field_key_map.get(selected_option)
            if filter_key:
                filtered_customers = [customer for customer in self.customers if
                                      customer.get(filter_key, '').lower().find(search_text) != -1]
            else:
                # Should not happen if options and map are correct
                filtered_customers = self.customers # Return all if filter key not found

        # Sort the filtered list before displaying
        self.display_customers(filtered_customers)

    def sort_by_column(self, column_key):
        """Sort the customer list by the specified column"""
        if self.sort_column == column_key:
            # If already sorting by this column, reverse the order
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            # If sorting by a new column, set it to ascending order
            self.sort_column = column_key
            self.sort_order = 'asc'

        # Re-display the customers with the new sorting
        self.display_customers(self.customers) # Pass the full list to be sorted and displayed

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}" 