import customtkinter as ctk
import tkinter.messagebox as messagebox
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, create_styled_entry, COLORS, FONTS
# Import data handling functions
from data_handler import load_data, save_data, get_next_id # Import necessary data functions
from datetime import datetime
from ui_elements import show_error, show_success

class ExpensesBillsManager:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback

        # Initialize data lists
        self.expenses = []
        self.bills = []
        self.active_alerts = [] # This is not used in ExpensesBillsManager, will remove

        # Initialize sorting attributes
        self.sort_column = 'date' # Default sorting column
        self.sort_order = 'desc' # Default sorting order (latest first for date)

        # Load data
        self.load_data()

        self.frame = None # Main frame for this section
        self.list_scroll_frame = None # Scrollable frame for the list

    def load_data(self):
        """Load expenses and bills data"""
        print("[DEBUG] Loading expenses and bills data...")
        self.expenses = load_data('expenses') or []
        self.bills = load_data('bills') or []
        print(f"[DEBUG] Loaded {len(self.expenses)} expenses and {len(self.bills)} bills")

    def save_data(self):
        """Save expenses and bills data"""
        print("[DEBUG] Saving expenses and bills data...")
        save_data('expenses', self.expenses)
        save_data('bills', self.bills)
        print("[DEBUG] Expenses and bills data saved")

    def create_expenses_bills_interface(self):
        """Create the expenses and bills interface"""
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
            text=self.LANGUAGES[self.current_language].get("expenses_bills", "Expenses and Bills"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Search and Filter section
        search_filter_frame = create_styled_frame(self.frame, style='card')
        search_filter_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.search_entry = create_styled_entry(
            search_filter_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search_expenses_bills", "Search expenses and bills...")
        )
        self.search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_entries)

        # Filter by option menu
        filter_options = [
            self.LANGUAGES[self.current_language].get("all_fields", "All Fields"),
            self.LANGUAGES[self.current_language].get("date", "Date"),
            self.LANGUAGES[self.current_language].get("description", "Description"),
            self.LANGUAGES[self.current_language].get("amount", "Amount"),
            self.LANGUAGES[self.current_language].get("category", "Category"),
            self.LANGUAGES[self.current_language].get("type", "Type"),
        ]
        self.filter_option_menu = ctk.CTkOptionMenu(
            search_filter_frame,
            values=filter_options,
            command=self.filter_entries # Trigger filter when option changes
        )
        self.filter_option_menu.set(filter_options[0]) # Set default to All Fields
        self.filter_option_menu.pack(side='left', padx=(0, 20), pady=20)

        # Area for expenses and bills list
        # Replace fixed frame with scrollable frame
        self.list_scroll_frame = ctk.CTkScrollableFrame(self.frame, orientation='vertical')
        self.list_scroll_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Display entries after loading
        self.display_entries() # Call display method

        # Placeholder for Add Expense/Bill buttons
        buttons_frame = create_styled_frame(self.frame, style='card') # Moved to be below scroll frame
        buttons_frame.pack(fill='x', padx=20, pady=(0, 20))

        add_expense_button = create_styled_button(
            buttons_frame,
            text=self.LANGUAGES[self.current_language].get("add_expense", "Add Expense"),
            style='primary',
            command=lambda: self.add_expense()
        )
        add_expense_button.pack(side='left', padx=10)

        add_bill_button = create_styled_button(
            buttons_frame,
            text=self.LANGUAGES[self.current_language].get("add_bill", "Add Bill"),
            style='primary',
            command=lambda: self.add_bill()
        )
        add_bill_button.pack(side='left', padx=10)

    def display_entries(self, entries_to_display=None):
        """Display the list of expenses and bills"""
        # Use the provided list if available, otherwise use the combined list
        all_entries = entries_to_display if entries_to_display is not None else self.expenses + self.bills

        # Sort the list
        if self.sort_column:
            try:
                # Handle numerical sorting for amount
                if self.sort_column == 'amount':
                    all_entries = sorted(all_entries, key=lambda x: float(x.get(self.sort_column, 0)), reverse=(self.sort_order == 'desc'))
                # Handle date sorting
                elif self.sort_column == 'date':
                    all_entries = sorted(all_entries, key=lambda x: datetime.strptime(x.get(self.sort_column, '1900-01-01'), '%Y-%m-%d') if x.get('date') else datetime.min, reverse=(self.sort_order == 'desc'))
                else:
                    # Default string sorting for other columns
                    all_entries = sorted(all_entries, key=lambda x: str(x.get(self.sort_column, '')).lower(), reverse=(self.sort_order == 'desc'))
            except Exception as e:
                print(f"[ERROR] Error during sorting: {e}")
                # Fallback to unsorted if sorting fails
                pass

        # Clear existing list
        for widget in self.list_scroll_frame.winfo_children():
            widget.destroy()

        if not all_entries:
            no_entries_label = create_styled_label(
                self.list_scroll_frame,
                text=self.LANGUAGES[self.current_language].get("no_expenses_bills", "No expenses or bills found."),
                style='body'
            )
            no_entries_label.pack(pady=20)
            return

        # Table headers
        headers = [
            ("date", "Date"),
            ("description", "Description"),
            ("amount", "Amount"),
            ("category", "Category"),
            ("supplier_name", "Supplier / المورد"),
            ("payment_method", "Payment Method / طريقة الدفع"),
            ("paid_amount", "Paid / المدفوع"),
            ("remaining", "Remaining / المتبقي"),
            ("type", "Type"), # Expense or Bill
            ("actions", "Actions") # Placeholder for Edit/Delete
        ]

        # Add headers to the grid and bind click events
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                self.list_scroll_frame,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
            # Bind click event for sorting, but exclude the 'actions' column
            if key != "actions":
                header.bind('<Button-1>', lambda e, col_key=key: self.sort_by_column(col_key))
                header.configure(cursor="hand2") # Change cursor to indicate it's clickable

            self.list_scroll_frame.grid_columnconfigure(i, weight=1)

        # Display entries
        for i, entry in enumerate(all_entries, 1):
            # Entry details
            date_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('date', ''),
                style='body'
            )
            date_label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

            description_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('description', ''),
                style='body'
            )
            description_label.grid(row=i, column=1, padx=10, pady=5, sticky='w')

            amount_label = create_styled_label(
                self.list_scroll_frame,
                text=f"${float(entry.get('amount', 0)):.2f}" if entry.get('amount') is not None else '$0.00',
                style='body'
            )
            amount_label.grid(row=i, column=2, padx=10, pady=5, sticky='w')

            category_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('category', ''),
                style='body'
            )
            category_label.grid(row=i, column=3, padx=10, pady=5, sticky='w')

            supplier_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('supplier_name', ''),
                style='body'
            )
            supplier_label.grid(row=i, column=4, padx=10, pady=5, sticky='w')

            payment_method_label = create_styled_label(
                self.list_scroll_frame,
                text=self._get_bilingual_payment_method(entry.get('payment_method', '')),
                style='body'
            )
            payment_method_label.grid(row=i, column=5, padx=10, pady=5, sticky='w')

            paid_amount_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('paid_amount', ''),
                style='body'
            )
            paid_amount_label.grid(row=i, column=6, padx=10, pady=5, sticky='w')

            remaining_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('remaining', ''),
                style='body'
            )
            remaining_label.grid(row=i, column=7, padx=10, pady=5, sticky='w')

            type_label = create_styled_label(
                self.list_scroll_frame,
                text=entry.get('type', ''),
                style='body'
            )
            type_label.grid(row=i, column=8, padx=10, pady=5, sticky='w')

            # Action buttons (placeholder)
            actions_frame = create_styled_frame(self.list_scroll_frame, style='card')
            actions_frame.grid(row=i, column=9, padx=10, pady=5, sticky='w')

            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=60,
                command=lambda e=entry: self.edit_entry(e) # Connect to edit method
            )
            edit_button.pack(side='left', padx=5)

            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='outline',
                width=60,
                command=lambda e=entry: self.delete_entry(e) # Connect to delete method
            )
            delete_button.pack(side='left', padx=5)

    def add_expense(self):
        """Open dialog to add a new expense"""
        self._add_entry_dialog('expense')

    def add_bill(self):
        """Open dialog to add a new bill"""
        self._add_entry_dialog('bill')

    def _add_entry_dialog(self, entry_type):
        """Create and show a dialog for adding a new expense or bill"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get(f"add_{entry_type}", f"Add New {entry_type.capitalize()}"))
        dialog.geometry("400x400") # Adjust size as needed
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
            text=self.LANGUAGES[self.current_language].get(f"add_{entry_type}", f"Add New {entry_type.capitalize()}"),
            style='heading'
        )
        title_label.pack(pady=10)

        # Input fields
        fields = [
            ("date", "Date (YYYY-MM-DD)"),
            ("description", "Description"),
            ("amount", "Amount"),
            ("category", "Category"),
        ]

        self.add_entry_entries = {}
        for key, text in fields:
            label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get(key, text), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            entry = create_styled_entry(form_frame)
            entry.pack(fill='x', padx=20, pady=(0, 10))
            self.add_entry_entries[key] = entry

        # Payment method (Dropdown)
        payment_methods = [
            self.LANGUAGES[self.current_language].get("cash", "Cash / نقدي"),
            self.LANGUAGES[self.current_language].get("credit", "Credit / آجل"),
            self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي")
        ]
        payment_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("payment_method", "Payment Method / طريقة الدفع"), style='subheading')
        payment_label.pack(pady=(0, 5), padx=20, anchor='w')
        self.payment_method_menu = ctk.CTkOptionMenu(form_frame, values=payment_methods)
        self.payment_method_menu.set(payment_methods[0])
        self.payment_method_menu.pack(fill='x', padx=20, pady=(0, 10))
        self.payment_method_menu.bind("<<ComboboxSelected>>", lambda e=None: self._toggle_paid_amount_field())

        # Paid amount (only for partial)
        self.paid_amount_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("paid_amount", "Paid Amount / المبلغ المدفوع"), style='subheading')
        self.paid_amount_entry = create_styled_entry(form_frame)
        self.paid_amount_label.pack_forget()
        self.paid_amount_entry.pack_forget()

        # Remaining amount (calculated)
        self.remaining_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("remaining_amount", "Remaining / المتبقي"), style='subheading')
        self.remaining_value = create_styled_label(form_frame, text="0", style='body')
        self.remaining_label.pack_forget()
        self.remaining_value.pack_forget()

        def on_paid_amount_change(event=None):
            try:
                total = float(self.add_entry_entries["amount"].get())
                paid = float(self.paid_amount_entry.get()) if self.paid_amount_entry.get() else 0
                remaining = max(0, total - paid)
                self.remaining_value.configure(text=f"{remaining:.2f}")
            except Exception:
                self.remaining_value.configure(text="0")
        self.paid_amount_entry.bind('<KeyRelease>', on_paid_amount_change)
        self.add_entry_entries["amount"].bind('<KeyRelease>', on_paid_amount_change)

        # --- Supplier Dropdown (for bills only) ---
        supplier_id = None
        supplier_name = None
        self.supplier_menu = None
        if entry_type == 'bill':
            suppliers = load_data('suppliers') or []
            supplier_names = [f"{s.get('name', '')} ({s.get('phone', '')})" for s in suppliers]
            supplier_ids = [s.get('id', '') for s in suppliers]
            supplier_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("supplier", "Supplier / المورد"), style='subheading')
            supplier_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.supplier_menu = ctk.CTkOptionMenu(form_frame, values=supplier_names)
            if supplier_names:
                self.supplier_menu.set(supplier_names[0])
            self.supplier_menu.pack(fill='x', padx=20, pady=(0, 10))

        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self._save_new_entry(dialog, entry_type)
        )
        save_button.pack(pady=20)

    def _toggle_paid_amount_field(self):
        method = self.payment_method_menu.get()
        partial = self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي")
        if method == partial:
            self.paid_amount_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.paid_amount_entry.pack(fill='x', padx=20, pady=(0, 10))
            self.remaining_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.remaining_value.pack(fill='x', padx=20, pady=(0, 10))
        else:
            self.paid_amount_label.pack_forget()
            self.paid_amount_entry.pack_forget()
            self.remaining_label.pack_forget()
            self.remaining_value.pack_forget()

    def _save_new_entry(self, dialog, entry_type):
        """Save the new expense or bill data"""
        new_entry_data = {'type': entry_type.capitalize()}
        for key, entry in self.add_entry_entries.items():
            new_entry_data[key] = entry.get().strip()
        # Payment method
        new_entry_data['payment_method'] = self.payment_method_menu.get()
        if new_entry_data['payment_method'] == self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي"):
            new_entry_data['paid_amount'] = self.paid_amount_entry.get().strip()
            try:
                total = float(new_entry_data['amount'])
                paid = float(new_entry_data['paid_amount']) if new_entry_data['paid_amount'] else 0
                new_entry_data['remaining'] = max(0, total - paid)
            except Exception:
                new_entry_data['remaining'] = new_entry_data['amount']
        elif new_entry_data['payment_method'] == self.LANGUAGES[self.current_language].get("credit", "Credit / آجل"):
            new_entry_data['paid_amount'] = "0"
            new_entry_data['remaining'] = new_entry_data['amount']
        else:
            new_entry_data['paid_amount'] = new_entry_data['amount']
            new_entry_data['remaining'] = "0"

        # Supplier info for bills
        if entry_type == 'bill' and self.supplier_menu:
            suppliers = load_data('suppliers') or []
            supplier_names = [f"{s.get('name', '')} ({s.get('phone', '')})" for s in suppliers]
            idx = supplier_names.index(self.supplier_menu.get()) if self.supplier_menu.get() in supplier_names else -1
            if idx >= 0:
                new_entry_data['supplier_id'] = suppliers[idx].get('id', '')
                new_entry_data['supplier_name'] = suppliers[idx].get('name', '')
            else:
                new_entry_data['supplier_id'] = ''
                new_entry_data['supplier_name'] = ''

        # Basic validation (e.g., date format, amount is numeric)
        if not new_entry_data.get('date') or not new_entry_data.get('description') or not new_entry_data.get('amount'):
            # Use existing show_error function
            show_error(self.LANGUAGES[self.current_language].get("fill_all_fields", "Please fill all required fields."), self.current_language)
            return

        try:
            # Validate date format
            datetime.strptime(new_entry_data.get('date'), '%Y-%m-%d')
        except ValueError:
            show_error(self.LANGUAGES[self.current_language].get("invalid_date_format", "Invalid date format. Please use YYYY-MM-DD."), self.current_language)
            return

        try:
            # Validate amount is numeric
            float(new_entry_data.get('amount'))
        except ValueError:
            show_error(self.LANGUAGES[self.current_language].get("invalid_amount", "Invalid amount. Please enter a number."), self.current_language)
            return

        # Generate next ID (assuming unique IDs for expenses and bills separately or combined)
        # For simplicity, let's use a combined ID system for now or separate if needed.
        # Let's use a combined system with a prefix to distinguish.
        entry_prefix = 'EXP' if entry_type == 'expense' else 'BILL'
        next_id = get_next_id(f'{entry_type}s') # Use data_type specific ID counter
        new_entry_data['id'] = f'{entry_prefix}-{next_id}'

        # Add to the respective list
        if entry_type == 'expense':
            self.expenses.append(new_entry_data)
            self.save_data()
        elif entry_type == 'bill':
            self.bills.append(new_entry_data)
            self.save_data()

        # Update display and close dialog
        self.display_entries()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get(f"{entry_type}_added", f"{entry_type.capitalize()} added successfully."), self.current_language)

    def edit_entry(self, entry):
        """Open dialog to edit an existing expense or bill"""
        dialog = ctk.CTkToplevel(self.root)
        entry_type = entry.get('type', '').lower()
        dialog.title(self.LANGUAGES[self.current_language].get(f"edit_{entry_type}", f"Edit {entry.get('type', '')}"))
        dialog.geometry("400x400") # Adjust size as needed
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
            text=self.LANGUAGES[self.current_language].get(f"edit_{entry_type}", f"Edit {entry.get('type', '')}"),
            style='heading'
        )
        title_label.pack(pady=10)

        # Input fields
        fields = [
            ("date", "Date (YYYY-MM-DD)"),
            ("description", "Description"),
            ("amount", "Amount"),
            ("category", "Category"),
        ]

        self.edit_entry_entries = {}
        for key, text in fields:
            label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get(key, text), style='subheading')
            label.pack(pady=(0, 5), padx=20, anchor='w')
            entry_widget = create_styled_entry(form_frame)
            entry_widget.insert(0, str(entry.get(key, '')))
            entry_widget.pack(fill='x', padx=20, pady=(0, 10))
            self.edit_entry_entries[key] = entry_widget

        # Payment method (Dropdown)
        payment_methods = [
            self.LANGUAGES[self.current_language].get("cash", "Cash / نقدي"),
            self.LANGUAGES[self.current_language].get("credit", "Credit / آجل"),
            self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي")
        ]
        payment_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("payment_method", "Payment Method / طريقة الدفع"), style='subheading')
        payment_label.pack(pady=(0, 5), padx=20, anchor='w')
        self.edit_payment_method_menu = ctk.CTkOptionMenu(form_frame, values=payment_methods)
        self.edit_payment_method_menu.set(entry.get('payment_method', payment_methods[0]))
        self.edit_payment_method_menu.pack(fill='x', padx=20, pady=(0, 10))
        self.edit_payment_method_menu.bind("<<ComboboxSelected>>", lambda e=None: self._toggle_edit_paid_amount_field())

        # Paid amount (only for partial)
        self.edit_paid_amount_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("paid_amount", "Paid Amount / المبلغ المدفوع"), style='subheading')
        self.edit_paid_amount_entry = create_styled_entry(form_frame)
        self.edit_paid_amount_entry.insert(0, str(entry.get('paid_amount', '')))
        self.edit_paid_amount_label.pack_forget()
        self.edit_paid_amount_entry.pack_forget()

        # Remaining amount (calculated)
        self.edit_remaining_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("remaining_amount", "Remaining / المتبقي"), style='subheading')
        self.edit_remaining_value = create_styled_label(form_frame, text=str(entry.get('remaining', '0')), style='body')
        self.edit_remaining_label.pack_forget()
        self.edit_remaining_value.pack_forget()

        def on_edit_paid_amount_change(event=None):
            try:
                total = float(self.edit_entry_entries["amount"].get())
                paid = float(self.edit_paid_amount_entry.get()) if self.edit_paid_amount_entry.get() else 0
                remaining = max(0, total - paid)
                self.edit_remaining_value.configure(text=f"{remaining:.2f}")
            except Exception:
                self.edit_remaining_value.configure(text="0")
        self.edit_paid_amount_entry.bind('<KeyRelease>', on_edit_paid_amount_change)
        self.edit_entry_entries["amount"].bind('<KeyRelease>', on_edit_paid_amount_change)

        # --- Supplier Dropdown (for bills only) ---
        self.edit_supplier_menu = None
        if entry_type == 'bill':
            suppliers = load_data('suppliers') or []
            supplier_names = [f"{s.get('name', '')} ({s.get('phone', '')})" for s in suppliers]
            supplier_ids = [s.get('id', '') for s in suppliers]
            supplier_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("supplier", "Supplier / المورد"), style='subheading')
            supplier_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.edit_supplier_menu = ctk.CTkOptionMenu(form_frame, values=supplier_names)
            # Set current value if exists
            current_supplier = None
            for s in suppliers:
                if s.get('id', '') == entry.get('supplier_id', ''):
                    current_supplier = f"{s.get('name', '')} ({s.get('phone', '')})"
            if current_supplier and current_supplier in supplier_names:
                self.edit_supplier_menu.set(current_supplier)
            elif supplier_names:
                self.edit_supplier_menu.set(supplier_names[0])
            self.edit_supplier_menu.pack(fill='x', padx=20, pady=(0, 10))

        # Update button
        update_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("update", "Update"),
            style='primary',
            command=lambda: self.update_entry(dialog, entry)
        )
        update_button.pack(pady=20)

        # Cancel button
        cancel_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("cancel", "Cancel"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(pady=10)

    def _toggle_edit_paid_amount_field(self):
        method = self.edit_payment_method_menu.get()
        partial = self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي")
        if method == partial:
            self.edit_paid_amount_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.edit_paid_amount_entry.pack(fill='x', padx=20, pady=(0, 10))
            self.edit_remaining_label.pack(pady=(0, 5), padx=20, anchor='w')
            self.edit_remaining_value.pack(fill='x', padx=20, pady=(0, 10))
        else:
            self.edit_paid_amount_label.pack_forget()
            self.edit_paid_amount_entry.pack_forget()
            self.edit_remaining_label.pack_forget()
            self.edit_remaining_value.pack_forget()

    def update_entry(self, dialog, original_entry):
        for key, entry_widget in self.edit_entry_entries.items():
            original_entry[key] = entry_widget.get().strip()
        # Payment method
        original_entry['payment_method'] = self.edit_payment_method_menu.get()
        if original_entry['payment_method'] == self.LANGUAGES[self.current_language].get("partial", "Partial / جزئي"):
            original_entry['paid_amount'] = self.edit_paid_amount_entry.get().strip()
            try:
                total = float(original_entry['amount'])
                paid = float(original_entry['paid_amount']) if original_entry['paid_amount'] else 0
                original_entry['remaining'] = max(0, total - paid)
            except Exception:
                original_entry['remaining'] = original_entry['amount']
        elif original_entry['payment_method'] == self.LANGUAGES[self.current_language].get("credit", "Credit / آجل"):
            original_entry['paid_amount'] = "0"
            original_entry['remaining'] = original_entry['amount']
        else:
            original_entry['paid_amount'] = original_entry['amount']
            original_entry['remaining'] = "0"
        # Supplier info for bills
        if original_entry.get('type', '').lower() == 'bill' and self.edit_supplier_menu:
            suppliers = load_data('suppliers') or []
            supplier_names = [f"{s.get('name', '')} ({s.get('phone', '')})" for s in suppliers]
            idx = supplier_names.index(self.edit_supplier_menu.get()) if self.edit_supplier_menu.get() in supplier_names else -1
            if idx >= 0:
                original_entry['supplier_id'] = suppliers[idx].get('id', '')
                original_entry['supplier_name'] = suppliers[idx].get('name', '')
            else:
                original_entry['supplier_id'] = ''
                original_entry['supplier_name'] = ''
        self.save_data()
        self.display_entries()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get("entry_updated", "Entry updated successfully."), self.current_language)

    def delete_entry(self, entry):
        """Delete an expense or bill entry"""
        entry_type = entry.get('type', '').lower()
        confirm_message_key = f"confirm_delete_{entry_type}"
        success_message_key = f"{entry_type}_deleted"

        confirm_delete = messagebox.askyesno(
            self.LANGUAGES[self.current_language].get("confirm_delete", "Confirm Delete"),
            self.LANGUAGES[self.current_language].get(confirm_message_key, f"Are you sure you want to delete this {entry.get('type', '')} entry?")
        )

        if confirm_delete:
            if entry_type == 'expense':
                try:
                    self.expenses.remove(entry)
                    self.save_data()
                    self.display_entries()
                    show_success(self.LANGUAGES[self.current_language].get(success_message_key, f"{entry.get('type', '')} deleted successfully."), self.current_language)
                except ValueError:
                    show_error(self.LANGUAGES[self.current_language].get("entry_not_found", "Entry not found for deletion."), self.current_language)
            elif entry_type == 'bill':
                try:
                    self.bills.remove(entry)
                    self.save_data()
                    self.display_entries()
                    show_success(self.LANGUAGES[self.current_language].get(success_message_key, f"{entry.get('type', '')} deleted successfully."), self.current_language)
                except ValueError:
                    show_error(self.LANGUAGES[self.current_language].get("entry_not_found", "Entry not found for deletion."), self.current_language)
            else:
                show_error("Unknown entry type.", self.current_language)

    def filter_entries(self, event=None):
        """Filter expenses and bills based on the search entry and selected filter option"""
        search_text = self.search_entry.get().lower()
        selected_option = self.filter_option_menu.get()

        all_entries = self.expenses + self.bills
        filtered_entries = []

        # Map language option back to data key
        field_key_map = {
            self.LANGUAGES[self.current_language].get("date", "Date"): 'date',
            self.LANGUAGES[self.current_language].get("description", "Description"): 'description',
            self.LANGUAGES[self.current_language].get("amount", "Amount"): 'amount',
            self.LANGUAGES[self.current_language].get("category", "Category"): 'category',
            self.LANGUAGES[self.current_language].get("type", "Type"): 'type',
            self.LANGUAGES[self.current_language].get("all_fields", "All Fields"): 'all_fields', # Special key for all fields
        }
        filter_key = field_key_map.get(selected_option, 'all_fields') # Default to all_fields

        if filter_key == 'all_fields':
            # Filter across all relevant fields
            filtered_entries = [entry for entry in all_entries if
                                  (str(entry.get('date', '')).lower().find(search_text) != -1 or
                                   str(entry.get('description', '')).lower().find(search_text) != -1 or
                                   str(entry.get('amount', '')).lower().find(search_text) != -1 or
                                   str(entry.get('category', '')).lower().find(search_text) != -1 or
                                   str(entry.get('type', '')).lower().find(search_text) != -1)]
        else:
            # Filter by selected field
            filtered_entries = [entry for entry in all_entries if
                                  str(entry.get(filter_key, '')).lower().find(search_text) != -1]

        # Display the filtered list (sorting will be applied in display_entries)
        self.display_entries(filtered_entries)

    def sort_by_column(self, column_key):
        """Sort the expenses and bills list by the specified column"""
        if self.sort_column == column_key:
            # If already sorting by this column, reverse the order
            self.sort_order = 'desc' if self.sort_order == 'asc' else 'asc'
        else:
            # If sorting by a new column, set it to ascending order
            self.sort_column = column_key
            self.sort_order = 'asc'

        # Re-display the currently filtered list with the new sorting
        # Get the currently filtered list by calling filter_entries without an event
        self.filter_entries() # filter_entries will call display_entries with the correct data 

    def _get_bilingual_payment_method(self, value):
        if not value:
            return ""
        # Return always bilingual
        if "جزئي" in value or "Partial" in value:
            return "Partial / جزئي"
        if "آجل" in value or "Credit" in value:
            return "Credit / آجل"
        if "نقدي" in value or "Cash" in value:
            return "Cash / نقدي"
        return value 