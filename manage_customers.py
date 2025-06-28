import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, create_styled_entry, COLORS, FONTS
# Import data handling functions
from data_handler import load_data, save_data, get_next_id, import_from_excel
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

        self.PAGE_SIZE = 50
        self.current_page = 0

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

        # زر حذف كل العملاء (إداري فقط)
        delete_all_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("delete_all_customers", "Delete All Customers"),
            style='outline',
            command=self.delete_all_customers
        )
        delete_all_button.pack(side='right', padx=20, pady=20)

        # Refresh Button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_customers
        )
        refresh_button.pack(side='right', padx=20, pady=20)

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
        customer_list = customers_to_display if customers_to_display is not None else self.customers
        # Pagination
        total_customers = len(customer_list)
        total_pages = max(1, (total_customers + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        start = self.current_page * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_customers = customer_list[start:end]

        # Sort the customer list
        if self.sort_column:
            page_customers = sorted(page_customers, key=lambda x: x.get(self.sort_column, ''), reverse=(self.sort_order == 'desc'))

        # Clear existing list
        for widget in self.scrollable_customer_list.winfo_children():
            widget.destroy()

        if not page_customers:
            no_customers_label = create_styled_label(
                self.scrollable_customer_list,
                text=self.LANGUAGES[self.current_language].get("no_customers", "No customers found."),
                style='body'
            )
            no_customers_label.pack(pady=20)
            return

        # Table headers
        headers = [
            ("id", "Customer ID", "رقم العميل"),
            ("name", "Name", "اسم العميل"),
            ("category", "Category", "فئة العميل"),
            ("address", "Address", "العنوان"),
            ("phone1", "Phone 1", "تليفون 1"),
            ("phone2", "Phone 2", "تليفون 2"),
            ("local_code", "Local System Code", "الرمز الداخلي - المحلي"),
            ("old_code", "Old System Code", "الرمز الداخلي - القديم"),
            ("currency", "Currency", "عملة الحساب"),
            ("city", "City", "المدينة"),
            ("governorate", "Governorate", "المحافظة"),
            ("country", "Country", "الدولة"),
            ("representative", "Representative", "المندوب"),
            ("notes", "Notes", "ملاحظات"),
            ("actions", "Actions", "إجراءات")
        ]

        # Add headers to the grid and bind click events
        for i, (key, en, ar) in enumerate(headers):
            header = create_styled_label(
                self.scrollable_customer_list,
                text=self.get_bilingual(key, en, ar),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
            # Bind click event for sorting, but exclude the 'actions' column
            if key != "actions":
                header.bind('<Button-1>', lambda e, col_key=key: self.sort_by_column(col_key))
                header.configure(cursor="hand2") # Change cursor to indicate it's clickable

        # Customer list
        for i, customer in enumerate(page_customers, 1):
            for j, (key, en, ar) in enumerate(headers):
                if key == "actions":
                    actions_frame = create_styled_frame(self.scrollable_customer_list, style='card')
                    actions_frame.grid(row=i, column=j, padx=10, pady=10, sticky='w')
                    edit_button = create_styled_button(
                        actions_frame,
                        text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                        style='outline',
                        width=80,
                        command=lambda c=customer: self.edit_customer(c)
                    )
                    edit_button.pack(side='left', padx=5)
                    delete_button = create_styled_button(
                        actions_frame,
                        text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                        style='outline',
                        width=80,
                        command=lambda c=customer: self.delete_customer(c)
                    )
                    delete_button.pack(side='left', padx=5)
                else:
                    value = customer.get(key, "")
                    label = create_styled_label(
                        self.scrollable_customer_list,
                        text=value,
                        style='body'
                    )
                    label.grid(row=i, column=j, padx=10, pady=10, sticky='w')
        # Configure column weights so columns expand evenly
        for i in range(len(headers)):
            self.scrollable_customer_list.grid_columnconfigure(i, weight=1)

        # Pagination controls
        pagination_frame = create_styled_frame(self.scrollable_customer_list, style='card')
        pagination_frame.grid(row=len(page_customers)+2, column=0, columnspan=len(headers), pady=10)
        prev_button = create_styled_button(
            pagination_frame,
            text=self.LANGUAGES[self.current_language].get("previous", "Previous"),
            style='outline',
            command=self.go_to_previous_page
        )
        prev_button.pack(side='left', padx=10)
        page_label = create_styled_label(
            pagination_frame,
            text=f"{self.current_page+1} / {total_pages}",
            style='body'
        )
        page_label.pack(side='left', padx=10)
        next_button = create_styled_button(
            pagination_frame,
            text=self.LANGUAGES[self.current_language].get("next", "Next"),
            style='outline',
            command=self.go_to_next_page
        )
        next_button.pack(side='left', padx=10)

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

        # Input fields (add_customer)
        fields = [
            ("id", "Customer ID", "رقم العميل"),
            ("name", "Name", "اسم العميل"),
            ("category", "Category", "فئة العميل"),
            ("address", "Address", "العنوان"),
            ("phone1", "Phone 1", "تليفون 1"),
            ("phone2", "Phone 2", "تليفون 2"),
            ("local_code", "Local System Code", "الرمز الداخلي - المحلي"),
            ("old_code", "Old System Code", "الرمز الداخلي - القديم"),
            ("currency", "Currency", "عملة الحساب"),
            ("city", "City", "المدينة"),
            ("governorate", "Governorate", "المحافظة"),
            ("country", "Country", "الدولة"),
            ("representative", "Representative", "المندوب"),
            ("notes", "Notes", "ملاحظات")
        ]

        self.add_customer_entries = {} # Store entry widgets

        # Dropdown values
        category_options = [
            self.get_bilingual("category_cash", "Cash Customer", "عميل نقدي"),
            self.get_bilingual("category_credit", "Credit Customer", "عميل بالأجل")
        ]
        governorate_options = [
            self.get_bilingual(None, en, ar) for ar, en in [
                ("القاهرة", "Cairo"), ("الجيزة", "Giza"), ("الإسكندرية", "Alexandria"), ("الدقهلية", "Dakahlia"),
                ("البحر الأحمر", "Red Sea"), ("البحيرة", "Beheira"), ("الفيوم", "Fayoum"), ("الغربية", "Gharbia"),
                ("الإسماعيلية", "Ismailia"), ("المنوفية", "Monufia"), ("المنيا", "Minya"), ("القليوبية", "Qalyubia"),
                ("الوادي الجديد", "New Valley"), ("السويس", "Suez"), ("اسوان", "Aswan"), ("اسيوط", "Assiut"),
                ("بني سويف", "Beni Suef"), ("بورسعيد", "Port Said"), ("دمياط", "Damietta"), ("الشرقية", "Sharqia"),
                ("جنوب سيناء", "South Sinai"), ("كفر الشيخ", "Kafr El Sheikh"), ("مطروح", "Matrouh"), ("الأقصر", "Luxor"),
                ("قنا", "Qena"), ("شمال سيناء", "North Sinai"), ("سوهاج", "Sohag")
            ]
        ]

        for key, en, ar in fields:
            label = create_styled_label(form_frame, text=self.get_bilingual(key, en, ar), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            if key == "category":
                entry = ctk.CTkOptionMenu(form_frame, values=category_options)
                entry.set(category_options[0])
            elif key == "governorate":
                entry = ctk.CTkOptionMenu(form_frame, values=governorate_options)
                entry.set(governorate_options[0])
            else:
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

        # Input fields (edit_customer)
        fields = [
            ("id", "Customer ID", "رقم العميل"),
            ("name", "Name", "اسم العميل"),
            ("category", "Category", "فئة العميل"),
            ("address", "Address", "العنوان"),
            ("phone1", "Phone 1", "تليفون 1"),
            ("phone2", "Phone 2", "تليفون 2"),
            ("local_code", "Local System Code", "الرمز الداخلي - المحلي"),
            ("old_code", "Old System Code", "الرمز الداخلي - القديم"),
            ("currency", "Currency", "عملة الحساب"),
            ("city", "City", "المدينة"),
            ("governorate", "Governorate", "المحافظة"),
            ("country", "Country", "الدولة"),
            ("representative", "Representative", "المندوب"),
            ("notes", "Notes", "ملاحظات")
        ]

        self.edit_customer_entries = {} # Store entry widgets

        # Dropdown values
        category_options = [
            self.get_bilingual("category_cash", "Cash Customer", "عميل نقدي"),
            self.get_bilingual("category_credit", "Credit Customer", "عميل بالأجل")
        ]
        governorate_options = [
            self.get_bilingual(None, en, ar) for ar, en in [
                ("القاهرة", "Cairo"), ("الجيزة", "Giza"), ("الإسكندرية", "Alexandria"), ("الدقهلية", "Dakahlia"),
                ("البحر الأحمر", "Red Sea"), ("البحيرة", "Beheira"), ("الفيوم", "Fayoum"), ("الغربية", "Gharbia"),
                ("الإسماعيلية", "Ismailia"), ("المنوفية", "Monufia"), ("المنيا", "Minya"), ("القليوبية", "Qalyubia"),
                ("الوادي الجديد", "New Valley"), ("السويس", "Suez"), ("اسوان", "Aswan"), ("اسيوط", "Assiut"),
                ("بني سويف", "Beni Suef"), ("بورسعيد", "Port Said"), ("دمياط", "Damietta"), ("الشرقية", "Sharqia"),
                ("جنوب سيناء", "South Sinai"), ("كفر الشيخ", "Kafr El Sheikh"), ("مطروح", "Matrouh"), ("الأقصر", "Luxor"),
                ("قنا", "Qena"), ("شمال سيناء", "North Sinai"), ("سوهاج", "Sohag")
            ]
        ]

        for key, en, ar in fields:
            label = create_styled_label(form_frame, text=self.get_bilingual(key, en, ar), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            if key == "category":
                entry = ctk.CTkOptionMenu(form_frame, values=category_options)
                entry.set(customer.get(key, category_options[0]))
            elif key == "governorate":
                entry = ctk.CTkOptionMenu(form_frame, values=governorate_options)
                entry.set(customer.get(key, governorate_options[0]))
            else:
                entry = create_styled_entry(form_frame)
                entry.insert(0, customer.get(key, ''))
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

    def refresh_customers(self):
        """Refresh the customers list from Excel and update display"""
        try:
            # Import data from Excel before loading from DB
            if import_from_excel('customers'):
                print("[DEBUG] Successfully imported customers from Excel")
            else:
                print("[DEBUG] No Excel data to import or import failed")
            # Load customers from database
            self.customers = load_data("customers") or []
            print(f"[DEBUG] Loaded customers count: {len(self.customers)}")
            # Refresh the display
            self.display_customers()
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            from ui_elements import show_error
            show_error(f"Error refreshing customers: {str(e)}", self.current_language)

    def go_to_next_page(self):
        total_customers = len(self.customers)
        total_pages = max(1, (total_customers + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_customers()

    def go_to_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_customers()

    def delete_all_customers(self):
        from data_handler import save_data
        from ui_elements import show_success
        # حذف كل العملاء من القاعدة والملفات
        save_data('customers', [])
        self.customers = []
        self.display_customers()
        show_success(self.LANGUAGES[self.current_language].get("all_customers_deleted", "All customers deleted successfully."), self.current_language) 