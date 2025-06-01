import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from ui_elements import show_error, show_success
from data_handler import (
    insert_document, update_document, delete_document,
    load_data, save_data, get_next_id, import_from_excel
)
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label, create_styled_option_menu
)

class ProductManager:
    def __init__(self, root, current_language, languages, back_callback, hookah_types=None, hookah_flavors=None):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.hookah_types = hookah_types or []
        self.hookah_flavors = hookah_flavors or []
        self.products = load_data("products") or []

    def refresh_products(self):
        """Refresh the products list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            import_from_excel()

            # Load products from database
            self.products = load_data("products") or []
            print(f"[DEBUG] Loaded products count: {len(self.products)}")
            print(f"[DEBUG] Loaded products: {self.products}")
            
            # Refresh the display
            self.manage_products()
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            show_error(f"Error refreshing products: {str(e)}", self.current_language)

    def manage_products(self):
        """Create a modern product management interface"""
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
            text=self.LANGUAGES[self.current_language].get("manage_products", "Manage Products"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_products
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_products = len(self.products)
        active_products = len([p for p in self.products if p.get('status') == 'active'])
        discontinued_products = len([p for p in self.products if p.get('status') == 'discontinued'])
        
        # Create summary cards
        summary_cards = [
            ("total_products", "Total Products", total_products),
            ("active_products", "Active Products", active_products),
            ("discontinued_products", "Discontinued Products", discontinued_products)
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
            placeholder_text=self.LANGUAGES[self.current_language].get("search_products", "Search products...")
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
            text=self.LANGUAGES[self.current_language].get("add_product", "Add Product"),
            style='primary',
            command=self.add_product
        )
        add_button.pack(side='right', padx=20, pady=20)
        
        # Products table
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create scrollable frame for the table
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        
        # Table headers
        headers = [
            ("product_name", "Product Name"),
            ("product_type", "Type"),
            ("product_flavor", "Flavor"),
            ("product_price", "Price"),
            ("product_status", "Status"),
            ("actions", "Actions")
        ]
        
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=self.LANGUAGES[self.current_language].get(key, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Products list
        for i, product in enumerate(self.products, 1):
            # Product details
            name_label = create_styled_label(
                scrollable_table,
                text=product.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            type_label = create_styled_label(
                scrollable_table,
                text=product.get('type', ''),
                style='body'
            )
            type_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            flavor_label = create_styled_label(
                scrollable_table,
                text=product.get('flavor', ''),
                style='body'
            )
            flavor_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            price_label = create_styled_label(
                scrollable_table,
                text=f"${product.get('price', 0):.2f}",
                style='body'
            )
            price_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            status_label = create_styled_label(
                scrollable_table,
                text=product.get('status', 'active'),
                style='body'
            )
            status_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda p=product: self.edit_product(p['name'])
            )
            edit_button.pack(side='left', padx=5)
            
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='outline',
                width=80,
                command=lambda p=product: self.delete_product(p)
            )
            delete_button.pack(side='left', padx=5)

    def add_product(self):
        """Add a new product"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Product")
        dialog.geometry("400x500")
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set()
        
        # Create form
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("add_product", "Add Product"),
            style='heading'
        )
        title_label.pack(pady=20)
        
        # Product name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_name", "Product Name"),
            style='subheading'
        )
        name_label.pack(pady=(0, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Product type
        type_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_type", "Product Type"),
            style='subheading'
        )
        type_label.pack(pady=(0, 5))
        
        type_entry = create_styled_entry(form_frame)
        type_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Product flavor
        flavor_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_flavor", "Product Flavor"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        
        flavor_entry = create_styled_entry(form_frame)
        flavor_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Price
        price_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("price", "Price"),
            style='subheading'
        )
        price_label.pack(pady=(0, 5))
        
        price_entry = create_styled_entry(form_frame)
        price_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_menu = create_styled_option_menu(
            form_frame,
            values=["Available", "Out of Stock", "Discontinued"]
        )
        status_menu.pack(fill='x', padx=20, pady=(0, 20))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_product(
                dialog,
                name_entry.get(),
                type_entry.get(),
                flavor_entry.get(),
                price_entry.get(),
                status_menu.get()
            )
        )
        save_button.pack(fill='x', padx=20, pady=(0, 20))

    def edit_product(self, product_name=None):
        """Edit an existing product"""
        if product_name is None:
            return
            
        # Find the product
        product = None
        for p in self.products:
            if p['name'] == product_name:
                product = p
                break
        
        if not product:
            show_error("Product not found", self.current_language)
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("400x500")
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set()
        
        # Create form
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("edit_product", "Edit Product"),
            style='heading'
        )
        title_label.pack(pady=20)
        
        # Product name
        name_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_name", "Product Name"),
            style='subheading'
        )
        name_label.pack(pady=(0, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, product['name'])
        name_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Product type
        type_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_type", "Product Type"),
            style='subheading'
        )
        type_label.pack(pady=(0, 5))
        
        type_entry = create_styled_entry(form_frame)
        type_entry.insert(0, product['type'])
        type_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Product flavor
        flavor_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_flavor", "Product Flavor"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        
        flavor_entry = create_styled_entry(form_frame)
        flavor_entry.insert(0, product['flavor'])
        flavor_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Price
        price_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("price", "Price"),
            style='subheading'
        )
        price_label.pack(pady=(0, 5))
        
        price_entry = create_styled_entry(form_frame)
        price_entry.insert(0, str(product['price']))
        price_entry.pack(fill='x', padx=20, pady=(0, 20))
        
        # Status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_menu = create_styled_option_menu(
            form_frame,
            values=["Available", "Out of Stock", "Discontinued"]
        )
        status_menu.set(product['status'])
        status_menu.pack(fill='x', padx=20, pady=(0, 20))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.update_product(
                dialog,
                product_name,
                name_entry.get(),
                type_entry.get(),
                flavor_entry.get(),
                price_entry.get(),
                status_menu.get()
            )
        )
        save_button.pack(fill='x', padx=20, pady=(0, 20))
        
        # Cancel button
        cancel_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("cancel", "Cancel"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(fill='x', padx=20, pady=(0, 20))

    def save_product(self, dialog, name, type, flavor, price, status):
        """Save a new product"""
        if not all([name, type, flavor, price]):
            show_error("Please fill all fields", self.current_language)
            return
            
        try:
            price = float(price)
        except ValueError:
            show_error("Invalid price format", self.current_language)
            return
            
        # Create new product
        product = {
            'id': str(len(self.products) + 1),
            'name': name,
            'type': type,
            'flavor': flavor,
            'price': price,
            'status': status
        }
        
        # Add to products list
        self.products.append(product)
        
        # Save to MongoDB
        save_data("products", self.products)
        
        # Close dialog and refresh
        dialog.destroy()
        self.manage_products()
        show_success(self.LANGUAGES[self.current_language].get("product_added", "Product added successfully"), self.current_language)

    def update_product(self, dialog, old_name, name, type, flavor, price, status):
        """Update an existing product"""
        if not all([name, type, flavor, price]):
            show_error("Please fill all fields", self.current_language)
            return
            
        try:
            price = float(price)
        except ValueError:
            show_error("Invalid price format", self.current_language)
            return
            
        # Find and update product
        for product in self.products:
            if product['name'] == old_name:
                product['name'] = name
                product['type'] = type
                product['flavor'] = flavor
                product['price'] = price
                product['status'] = status
                break
        
        # Save to MongoDB
        save_data("products", self.products)
        
        # Close dialog and refresh
        dialog.destroy()
        self.manage_products()
        show_success(self.LANGUAGES[self.current_language].get("product_updated", "Product updated successfully"), self.current_language)

    def delete_product(self, product):
        """Delete a product"""
        self.products.remove(product)
        save_data("products", self.products)
        self.manage_products()
        show_success(self.LANGUAGES[self.current_language].get("product_deleted", "Product deleted successfully"), self.current_language)

    def refresh_products_list(self):
        """Refresh the products treeview"""
        self.products = load_data("products")
        self.filtered_products = self.products  # Initialize filtered products
        self.update_products_tree()

    def update_products_tree(self):
        """Update the products treeview with filtered products"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        for product in self.filtered_products:
            self.products_tree.insert("", "end", values=(
                product["Name"],
                product["Type"],
                product["Flavor"],
                product["Quantity"],
                f"${product['Price']:.2f}"
            ))

    def add_product_dialog(self):
        """Show dialog to add a new product"""
        self.add_product_window = ctk.CTkToplevel(self.root)
        self.add_product_window.title(self.LANGUAGES[self.current_language]["add_product"])
        self.add_product_window.geometry("400x500")
        self.add_product_window.configure(fg_color="#1f1f1f")

        title_label = ctk.CTkLabel(self.add_product_window, text=self.LANGUAGES[self.current_language]["add_product"],
                                   font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        title_label.pack(pady=10)

        fields = [
            ("Name:", "entry"),
            ("Type:", "combobox", self.HOOKAH_TYPES),
            ("Flavor:", "combobox", self.HOOKAH_FLAVORS),
            ("Quantity:", "entry"),
            ("Price:", "entry"),
            ("Supplier:", "entry"),
            ("Last Restock:", "date"),
            ("Active:", "checkbox")
        ]

        self.product_entries = []
        for i, (label, field_type, *options) in enumerate(fields):
            frame = ctk.CTkFrame(self.add_product_window, fg_color="#1f1f1f")
            frame.pack(fill='x', padx=20, pady=5)

            label_widget = ctk.CTkLabel(frame, text=label, text_color="white", font=ctk.CTkFont(size=12))
            label_widget.pack(side='left', padx=5)

            if field_type == "entry":
                entry = ctk.CTkEntry(frame)
                entry.pack(side='right', expand=True, fill='x', padx=5)
            elif field_type == "combobox":
                entry = ctk.CTkComboBox(frame, values=options[0])
                entry.pack(side='right', expand=True, fill='x', padx=5)
            elif field_type == "date":
                entry = DateEntry(frame, width=12, background='red',
                                foreground='white', borderwidth=2)
                entry.pack(side='right', padx=5)
            elif field_type == "checkbox":
                entry = ctk.CTkCheckBox(frame)
                entry.pack(side='right', padx=5)

            self.product_entries.append(entry)

        add_btn = ctk.CTkButton(self.add_product_window, text=self.LANGUAGES[self.current_language]["add_product"],
                                command=self.save_product)
        add_btn.pack(pady=20)

    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def filter_products(self, *args):
        """Filter products based on search query"""
        query = self.search_var.get().lower()
        if not query:
            self.filtered_products = self.products
        else:
            self.filtered_products = [p for p in self.products if query in p["Name"].lower() or
                                      query in p["Type"].lower() or
                                      query in p["Flavor"].lower()]
        self.update_products_tree()
