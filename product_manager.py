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
import os
from datetime import datetime
from PIL import Image

class ProductManager:
    def __init__(self, root, current_language, languages, back_callback, hookah_types=None, hookah_flavors=None, record_sale_instance=None):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.hookah_types = hookah_types or []
        self.hookah_flavors = hookah_flavors or []
        self.products = load_data("products") or []
        self.record_sale_instance = record_sale_instance

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
            ("image", "Image"),
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
            image_path = product.get('image_path')
            if image_path and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((50, 50)) # Resize for list view
                    # Use CTkImage for compatibility with customtkinter
                    img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                    image_label = ctk.CTkLabel(scrollable_table, image=img_tk, text="")
                    image_label.image = img_tk # Keep a reference!
                except Exception as e:
                    print(f"[ERROR] Could not load product image {image_path}: {e}")
                    image_label = create_styled_label(scrollable_table, text=self.LANGUAGES[self.current_language].get("error_loading_image", "Error loading image"), style='small')
            else:
                 image_label = create_styled_label(scrollable_table, text=self.LANGUAGES[self.current_language].get("no_image", "No Image"), style='small')

            image_label.grid(row=i, column=0, padx=10, pady=5, sticky='w') # Place in the first column

            name_label = create_styled_label(
                scrollable_table,
                text=product.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=1, padx=10, pady=10, sticky='w') # Shifted to second column
            
            type_label = create_styled_label(
                scrollable_table,
                text=product.get('type', ''),
                style='body'
            )
            type_label.grid(row=i, column=2, padx=10, pady=10, sticky='w') # Shifted
            
            flavor_label = create_styled_label(
                scrollable_table,
                text=product.get('flavor', ''),
                style='body'
            )
            flavor_label.grid(row=i, column=3, padx=10, pady=10, sticky='w') # Shifted
            
            price_label = create_styled_label(
                scrollable_table,
                text=f"${product.get('price', 0):.2f}",
                style='body'
            )
            price_label.grid(row=i, column=4, padx=10, pady=10, sticky='w') # Shifted
            
            status_label = create_styled_label(
                scrollable_table,
                text=product.get('status', 'active'),
                style='body'
            )
            status_label.grid(row=i, column=5, padx=10, pady=10, sticky='w') # Shifted
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=6, padx=10, pady=10, sticky='w') # Shifted
            
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
        
        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create form
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True)
        
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
        name_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product type
        type_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_type", "Product Type"),
            style='subheading'
        )
        type_label.pack(pady=(0, 5))
        
        type_entry = create_styled_entry(form_frame)
        type_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product flavor
        flavor_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_flavor", "Product Flavor"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        
        flavor_entry = create_styled_entry(form_frame)
        flavor_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Price
        price_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("price", "Price"),
            style='subheading'
        )
        price_label.pack(pady=(0, 5))
        
        price_entry = create_styled_entry(form_frame)
        price_entry.pack(fill='x', padx=20, pady=(0, 10))
        
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
        status_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Image selection
        image_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_image", "Product Image"),
            style='subheading'
        )
        image_label.pack(pady=(0, 5))
        
        image_frame = create_styled_frame(form_frame, style='card')
        image_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        self.add_image_path_label = create_styled_label(
            image_frame,
            text=self.LANGUAGES[self.current_language].get("no_image_selected", "No image selected"),
            style='body'
        )
        self.add_image_path_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        select_image_button = create_styled_button(
            image_frame,
            text=self.LANGUAGES[self.current_language].get("select_image", "Select Image"),
            style='outline',
            width=100,
            command=self.select_image
        )
        select_image_button.pack(side='right')
        
        # Store the selected image path temporarily for the dialog
        self.selected_image_path = None

        # Image preview (for Add dialog)
        self.add_image_preview = ctk.CTkLabel(form_frame, text="", width=100, height=100)
        self.add_image_preview.pack(pady=(10, 10))

        # Save button
        save_button = create_styled_button(
            scrollable_form_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=lambda: self.save_product(
                dialog,
                name_entry.get(),
                type_entry.get(),
                flavor_entry.get(),
                price_entry.get(),
                status_menu.get(),
                self.selected_image_path
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
        dialog.geometry("400x550")
        dialog.configure(fg_color=COLORS['background'])
        dialog.grab_set()
        
        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create form
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True)
        
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
        name_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product type
        type_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_type", "Type"),
            style='subheading'
        )
        type_label.pack(pady=(0, 5))
        
        type_menu = create_styled_option_menu(
            form_frame,
            values=[self.LANGUAGES[self.current_language].get(t, t.capitalize()) for t in self.hookah_types]
        )
        type_menu.set(product['type'])
        type_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product flavor
        flavor_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_flavor", "Flavor"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        
        flavor_menu = create_styled_option_menu(
            form_frame,
            values=[self.LANGUAGES[self.current_language].get(f, f.capitalize()) for f in self.hookah_flavors]
        )
        flavor_menu.set(product['flavor'])
        flavor_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product price
        price_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_price", "Price"),
            style='subheading'
        )
        price_label.pack(pady=(0, 5))
        
        price_entry = create_styled_entry(form_frame)
        price_entry.insert(0, str(product['price']))
        price_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product status
        status_label = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_status", "Status"),
            style='subheading'
        )
        status_label.pack(pady=(0, 5))
        
        status_menu = create_styled_option_menu(
            form_frame,
            values=[self.LANGUAGES[self.current_language].get('status_active', 'Active'),
                    self.LANGUAGES[self.current_language].get('status_discontinued', 'Discontinued')]
        )
        status_menu.set(self.LANGUAGES[self.current_language].get(f'status_{product.get('status', 'active')}', product.get('status', 'Active')))
        status_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Image selection
        image_label_edit = create_styled_label(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("product_image", "Product Image"),
            style='subheading'
        )
        image_label_edit.pack(pady=(0, 5))
        
        image_frame_edit = create_styled_frame(form_frame, style='card')
        image_frame_edit.pack(fill='x', padx=20, pady=(0, 10))
        
        self.edit_image_path_label = create_styled_label(
            image_frame_edit,
            text=product.get('image_path', self.LANGUAGES[self.current_language].get("no_image_selected", "No image selected")),
            style='body'
        )
        self.edit_image_path_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        select_image_button_edit = create_styled_button(
            image_frame_edit,
            text=self.LANGUAGES[self.current_language].get("select_image", "Select Image"),
            style='outline',
            width=100,
            command=self.select_image
        )
        select_image_button_edit.pack(side='right')
        
        # Store the selected image path temporarily for the dialog
        self.selected_image_path = product.get('image_path', None)

        # Image preview (for Edit dialog)
        self.edit_image_preview = ctk.CTkLabel(form_frame, text="", width=100, height=100)
        self.edit_image_preview.pack(pady=(10, 10))
        # Display existing image if available
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            try:
                img = Image.open(self.selected_image_path)
                img.thumbnail((100, 100)) # Resize for preview
                img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                self.edit_image_preview.configure(image=img_tk, text="")
            except Exception as e:
                print(f"[ERROR] Could not load image for preview: {e}")

        # Update button
        update_button = create_styled_button(
            form_frame,
            text=self.LANGUAGES[self.current_language].get("update", "Update"),
            style='primary',
            command=lambda: self.update_product(
                dialog,
                product['name'],
                name_entry.get(),
                type_menu.get(),
                flavor_menu.get(),
                price_entry.get(),
                status_menu.get(),
                self.selected_image_path
            )
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

    def select_image(self):
        """Open a file dialog to select an image and copy it to the images directory"""
        try:
            # Use tkinter's file dialog to select an image file
            file_path = ctk.filedialog.askopenfilename(
                title=self.LANGUAGES[self.current_language].get("select_image_file", "Select Image File"),
                filetypes=(
                    (self.LANGUAGES[self.current_language].get("image_files", "Image Files"), "*.png *.jpg *.jpeg *.gif"),
                    (self.LANGUAGES[self.current_language].get("all_files", "All files"), "*.*")
                )
            )

            if file_path:
                # Ensure the images directory exists
                images_dir = "images/products"
                os.makedirs(images_dir, exist_ok=True)

                # Generate a unique filename (using original filename with a timestamp)
                original_filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
                new_filename = f"{timestamp}_{original_filename}"
                destination_path = os.path.join(images_dir, new_filename)

                # Copy the file
                import shutil
                shutil.copy2(file_path, destination_path)
                print(f"[DEBUG] Copied image from {file_path} to {destination_path}")

                # Store the relative path (or just the filename) in the product data
                # Let's store the relative path from the workspace root
                relative_path = os.path.relpath(destination_path, os.getcwd())
                self.selected_image_path = relative_path

                # Update the label and preview in the currently open dialog (add or edit)
                try:
                    img = Image.open(file_path)
                    img.thumbnail((100, 100)) # Resize for preview
                    img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))

                    if hasattr(self, 'add_image_path_label') and self.add_image_path_label.winfo_exists():
                         self.add_image_path_label.configure(text=os.path.basename(relative_path))
                         if hasattr(self, 'add_image_preview') and self.add_image_preview.winfo_exists():
                             self.add_image_preview.configure(image=img_tk, text="")

                    elif hasattr(self, 'edit_image_path_label') and self.edit_image_path_label.winfo_exists():
                         self.edit_image_path_label.configure(text=os.path.basename(relative_path))
                         if hasattr(self, 'edit_image_preview') and self.edit_image_preview.winfo_exists():
                              self.edit_image_preview.configure(image=img_tk, text="")

                except Exception as e:
                     print(f"[ERROR] Could not create image preview: {e}")
                     show_error(f"Error creating image preview: {str(e)}", self.current_language) # Show error to user as well

                show_success(self.LANGUAGES[self.current_language].get("image_selected_success", "Image selected successfully."), self.current_language)

        except Exception as e:
            show_error(f"Error selecting image: {str(e)}", self.current_language)
            import traceback
            traceback.print_exc()

    def save_product(self, dialog, name, type, flavor, price, status, image_path):
        """Save a new product"""
        if not name or not price:
            show_error(self.LANGUAGES[self.current_language].get("name_price_required", "Product Name and Price are required."), self.current_language)
            return
            
        try:
            price = float(price)
        except ValueError:
            show_error(self.LANGUAGES[self.current_language].get("invalid_price", "Invalid price. Please enter a number."), self.current_language)
            return
            
        # Check if product with the same name already exists
        if any(p.get('name', '').lower() == name.lower() for p in self.products):
            show_error(self.LANGUAGES[self.current_language].get("product_exists", "Product with this name already exists."), self.current_language)
            return
            
        new_product = {
            'id': get_next_id('products'),
            'name': name,
            'type': type,
            'flavor': flavor,
            'price': price,
            'status': status,
            'image_path': image_path
        }
        
        self.products.append(new_product)
        save_data("products", self.products)
        # Notify RecordSale to refresh its list
        if self.record_sale_instance:
            self.record_sale_instance.refresh_products()
        self.refresh_products()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get("product_added_success", "Product added successfully!"), self.current_language)

    def update_product(self, dialog, old_name, name, type, flavor, price, status, image_path):
        """Update an existing product"""
        if not name or not price:
            show_error(self.LANGUAGES[self.current_language].get("name_price_required", "Product Name and Price are required."), self.current_language)
            return
            
        try:
            price = float(price)
        except ValueError:
            show_error(self.LANGUAGES[self.current_language].get("invalid_price", "Invalid price. Please enter a number."), self.current_language)
            return
            
        # Find the product by old_name and update
        for product in self.products:
            if product.get('name', '') == old_name:
                product['name'] = name
                product['type'] = type
                product['flavor'] = flavor
                product['price'] = price
                product['status'] = status
                product['image_path'] = image_path
                break
        
        save_data("products", self.products)
        # Notify RecordSale to refresh its list
        if self.record_sale_instance:
            self.record_sale_instance.refresh_products()
        self.refresh_products()
        dialog.destroy()
        show_success(self.LANGUAGES[self.current_language].get("product_updated_success", "Product updated successfully!"), self.current_language)

    def delete_product(self, product):
        """Delete a product"""
        confirm = messagebox.askyesno(
            self.LANGUAGES[self.current_language].get("confirm_delete", "Confirm Delete"),
            self.LANGUAGES[self.current_language].get("confirm_delete_product", f"Are you sure you want to delete {product.get('name', 'this product')}?")
        )
        if confirm:
            try:
                self.products.remove(product)
                save_data("products", self.products)
                # Notify RecordSale to refresh its list
                if self.record_sale_instance:
                    self.record_sale_instance.refresh_products()
                self.refresh_products()
                show_success(self.LANGUAGES[self.current_language].get("product_deleted_success", "Product deleted successfully!"), self.current_language)
            except ValueError:
                show_error(self.LANGUAGES[self.current_language].get("product_not_found", "Product not found."), self.current_language)

    def refresh_products_list(self):
        """Refresh the displayed list of products"""
        self.manage_products()

    def update_products_tree(self):
        """Update the treeview with current product data"""
        pass

    def add_product_dialog(self):
        """Show dialog to add a product (old method?)"""
        pass

    def clear_frame(self):
        """Clear the current frame (helper function)"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def filter_products(self, *args):
        """Filter products based on search and selected category"""
        pass
