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
import json

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
        self.current_page = 0
        self.products_per_page = 20

    def refresh_products(self):
        """Refresh the products list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            if import_from_excel('products'):
                print("[DEBUG] Successfully imported data from Excel")
            else:
                print("[DEBUG] No Excel data to import or import failed")

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
        
        self.search_var = ctk.StringVar()
        search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("search_products", "Search products..."),
            textvariable=self.search_var
        )
        search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        self.search_var.trace_add('write', lambda *args: self.filter_products())
        
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
            ("product_flavor", "Flavor"),
            ("product_weight", "Weight"),
            ("barcode", "Barcode"),
            ("wholesale_supplier_price", "Wholesale Supplier Price"),
            ("wholesale_sale_price", "Wholesale Sale Price"),
            ("retail_sale_price", "Retail Sale Price"),
            ("product_status", "Status"),
            ("actions", "Actions")
        ]
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=default_text,
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # فلترة المنتجات لتشمل المتاحة والجارية
        filtered_products = [p for p in self.products if str(p.get('status', '')).strip().lower() in ['active', 'available'] and p.get('source', 'defined') != 'inventory']
        total_products = len(filtered_products)
        total_pages = max(1, (total_products + self.products_per_page - 1) // self.products_per_page)
        start_idx = self.current_page * self.products_per_page
        end_idx = start_idx + self.products_per_page
        page_products = filtered_products[start_idx:end_idx]
        for i, product in enumerate(page_products, 1 + start_idx):
            image_path = str(product.get('image_path', '')) if product.get('image_path') is not None else ''
            if image_path and os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((50, 50))
                    img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
                    image_label = ctk.CTkLabel(scrollable_table, image=img_tk, text="")
                    image_label.image = img_tk
                except Exception as e:
                    print(f"[ERROR] Could not load product image {image_path}: {e}")
                    image_label = create_styled_label(scrollable_table, text=self.LANGUAGES[self.current_language].get("error_loading_image", "Error loading image"), style='small')
            else:
                image_label = create_styled_label(scrollable_table, text=self.LANGUAGES[self.current_language].get("no_image", "No Image"), style='small')
            image_label.grid(row=i, column=0, padx=10, pady=5, sticky='w')
            name_label = create_styled_label(
                scrollable_table,
                text=str(product.get('name', '')),
                style='body'
            )
            name_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            flavor_label = create_styled_label(
                scrollable_table,
                text=str(product.get('flavor', '')),
                style='body'
            )
            flavor_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            weight_label = create_styled_label(
                scrollable_table,
                text=str(product.get('weight', '')),
                style='body'
            )
            weight_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            barcode_label = create_styled_label(
                scrollable_table,
                text=str(product.get('barcode', '')),
                style='body'
            )
            barcode_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            wholesale_supplier_price_label = create_styled_label(
                scrollable_table,
                text=str(product.get('wholesale_supplier_price', '')),
                style='body'
            )
            wholesale_supplier_price_label.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            wholesale_sale_price_label = create_styled_label(
                scrollable_table,
                text=str(product.get('wholesale_sale_price', '')),
                style='body'
            )
            wholesale_sale_price_label.grid(row=i, column=6, padx=10, pady=10, sticky='w')
            retail_sale_price_label = create_styled_label(
                scrollable_table,
                text=str(product.get('retail_sale_price', '')),
                style='body'
            )
            retail_sale_price_label.grid(row=i, column=7, padx=10, pady=10, sticky='w')
            status_label = create_styled_label(
                scrollable_table,
                text=str(product.get('status', 'active')),
                style='body'
            )
            status_label.grid(row=i, column=8, padx=10, pady=10, sticky='w')
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=9, padx=10, pady=10, sticky='w')
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda pid=product.get('id'): self.edit_product(pid)
            )
            edit_button.pack(side='left', padx=5)
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='error',
                width=80,
                command=lambda pid=product.get('id'): self.delete_product(pid)
            )
            delete_button.pack(side='left', padx=5)
        
        # أزرار التنقل بين الصفحات
        nav_frame = create_styled_frame(main_frame, style='card')
        nav_frame.pack(fill='x', padx=20, pady=(0, 10))
        prev_btn = create_styled_button(
            nav_frame,
            text=self.LANGUAGES[self.current_language].get("previous", "Previous"),
            style='outline',
            command=self.goto_previous_page
        )
        prev_btn.pack(side='left', padx=10, pady=10)
        page_label = create_styled_label(
            nav_frame,
            text=f"{self.current_page + 1} / {total_pages}",
            style='subheading'
        )
        page_label.pack(side='left', padx=10, pady=10)
        next_btn = create_styled_button(
            nav_frame,
            text=self.LANGUAGES[self.current_language].get("next", "Next"),
            style='outline',
            command=self.goto_next_page
        )
        next_btn.pack(side='left', padx=10, pady=10)

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
            text=self.get_bilingual("add_product", "Add Product", "إضافة منتج"),
            style='heading'
        )
        title_label.pack(pady=20)
        
        # Location (Dropdown)
        location_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("location", "Location", "المكان"),
            style='subheading'
        )
        location_label.pack(pady=(0, 5))
        stores_file = os.path.join("excel_data", "stores.json")
        locations = ["المحل / Shop"]
        if os.path.exists(stores_file):
            with open(stores_file, 'r', encoding='utf-8') as f:
                stores = json.load(f)
                locations += [store['name'] for store in stores]
        location_menu = create_styled_option_menu(
            form_frame,
            values=locations
        )
        location_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product name (قائمة منسدلة أو إدخال جديد)
        name_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_name", "Product Name", "اسم المنتج"),
            style='subheading'
        )
        name_label.pack(pady=(0, 5))
        
        # إطار لاسم المنتج
        name_frame = create_styled_frame(form_frame, style='card')
        name_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # قائمة منسدلة بالمنتجات الموجودة في المخزن
        inventory = load_data("inventory") or []
        inventory_names = [item.get('name', '') for item in inventory if item.get('quantity', 0) > 0]
        self.name_menu = create_styled_option_menu(
            name_frame,
            values=["-- اختر منتج من المخزن --"] + inventory_names + ["-- إضافة منتج جديد --"]
        )
        self.name_menu.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # حقل إدخال اسم المنتج الجديد
        self.name_entry = create_styled_entry(name_frame)
        self.name_entry.pack(side='right', fill='x', expand=True)
        self.name_entry.pack_forget()  # مخفي افتراضياً
        
        def on_name_selection(value):
            if value == "-- إضافة منتج جديد --":
                self.name_menu.pack_forget()
                self.name_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
            elif value != "-- اختر منتج من المخزن --":
                # إذا تم اختيار منتج من المخزن، املأ البيانات تلقائياً
                selected_item = next((item for item in inventory if item.get('name') == value), None)
                if selected_item:
                    # املأ البيانات تلقائياً
                    if hasattr(self, 'flavor_entry'):
                        self.flavor_entry.delete(0, 'end')
                        self.flavor_entry.insert(0, selected_item.get('flavor', ''))
                    if hasattr(self, 'weight_menu'):
                        self.weight_menu.set(selected_item.get('weight', '-'))
                    if hasattr(self, 'quantity_menu'):
                        self.quantity_menu.set(str(selected_item.get('quantity', 1)))
                    if hasattr(self, 'barcode_entry'):
                        self.barcode_entry.delete(0, 'end')
                        self.barcode_entry.insert(0, selected_item.get('barcode', ''))
        
        self.name_menu.configure(command=on_name_selection)
        
        # Product flavor (اختياري)
        flavor_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_flavor", "Product Flavor (Optional)", "نكهة المنتج (اختياري)"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        self.flavor_entry = create_styled_entry(form_frame)
        self.flavor_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product weight (Dropdown اختياري)
        weight_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_weight", "Product Weight (Optional)", "وزن المنتج (اختياري)"),
            style='subheading'
        )
        weight_label.pack(pady=(0, 5))
        weight_options = [
            self.get_bilingual("weight_50g", "50g", "50 جم"),
            self.get_bilingual("weight_100g", "100g", "100 جم"),
            self.get_bilingual("weight_150g", "150g", "150 جم"),
            self.get_bilingual("weight_250g", "250g", "250 جم"),
            self.get_bilingual("weight_300g", "300g", "300 جم"),
            self.get_bilingual("weight_350g", "350g", "350 جم"),
            self.get_bilingual("weight_400g", "400g", "400 جم"),
            self.get_bilingual("weight_450g", "450g", "450 جم"),
            self.get_bilingual("weight_500g", "500g", "500 جم"),
            self.get_bilingual("weight_750g", "750g", "750 جم"),
            self.get_bilingual("weight_1kg", "1kg", "1 كجم"),
            self.get_bilingual("weight_1500g", "1500g", "1500 جم"),
            self.get_bilingual("weight_11750g", "1750g", "1750 جم"),
            
            self.get_bilingual("weight_2kg", "2kg", "2 كجم"),
            self.get_bilingual("weight_2500g", "2500g", "2500 جم"),
            self.get_bilingual("weight_3kg", "3kg", "3 كجم"),
            self.get_bilingual("weight_3500g", "3500g", "3500 جم"),
            self.get_bilingual("weight_4kg", "4kg", "4 كجم"),
            self.get_bilingual("weight_4500g", "4500g", "4500 جم"),
        ]
        # أضف خيارات 2-10 كيلو
        for kg in range(2, 11):
            weight_options.append(self.get_bilingual(f"weight_{kg}kg", f"{kg}kg", f"{kg} كجم"))
        self.weight_menu = create_styled_option_menu(
            form_frame,
            values=["-"] + weight_options
        )
        self.weight_menu.set("-")
        self.weight_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Barcode (إجباري)
        barcode_label_text = ("Barcode / باركود" if self.current_language == 'en' else "باركود / Barcode")
        barcode_label = create_styled_label(
            form_frame,
            text=barcode_label_text,
            style='subheading'
        )
        barcode_label.pack(pady=(0, 5))
        self.barcode_entry = create_styled_entry(form_frame)
        self.barcode_entry.pack(fill='x', padx=20, pady=(0, 10))
        
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

        # Wholesale Supplier Price
        wholesale_supplier_price_label = create_styled_label(form_frame, text="Wholesale Supplier Price / سعر الجملة من التاجر", style='subheading')
        wholesale_supplier_price_label.pack(pady=(0, 5))
        wholesale_supplier_price_entry = create_styled_entry(form_frame)
        wholesale_supplier_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Wholesale Sale Price
        wholesale_sale_price_label = create_styled_label(form_frame, text="Wholesale Sale Price / سعر الجملة للبيع", style='subheading')
        wholesale_sale_price_label.pack(pady=(0, 5))
        wholesale_sale_price_entry = create_styled_entry(form_frame)
        wholesale_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Retail Sale Price
        retail_sale_price_label = create_styled_label(form_frame, text="Retail Sale Price / سعر البيع قطاعى", style='subheading')
        retail_sale_price_label.pack(pady=(0, 5))
        retail_sale_price_entry = create_styled_entry(form_frame)
        retail_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Save button
        def save():
            # الحصول على اسم المنتج من القائمة المنسدلة أو حقل الإدخال
            if self.name_menu.winfo_ismapped():
                # إذا كانت القائمة المنسدلة ظاهرة
                selected_name = self.name_menu.get()
                if selected_name in ["-- اختر منتج من المخزن --", "-- إضافة منتج جديد --"]:
                    show_error("Please select a product or choose 'Add New Product'", self.current_language)
                    return
                name = selected_name
            else:
                # إذا كان حقل الإدخال ظاهر
                name = self.name_entry.get().strip()
                if not name:
                    show_error("Please enter a product name", self.current_language)
                    return
            
            flavor = self.flavor_entry.get().strip() if self.flavor_entry.get().strip() else ""
            weight = self.weight_menu.get() if self.weight_menu.get() != "-" else ""
            status = status_menu.get()
            location = location_menu.get()
            wholesale_supplier_price = wholesale_supplier_price_entry.get()
            wholesale_sale_price = wholesale_sale_price_entry.get()
            retail_sale_price = retail_sale_price_entry.get()
            self.save_product(dialog, name, flavor, weight, status, self.selected_image_path, self.barcode_entry.get(), location, wholesale_supplier_price, wholesale_sale_price, retail_sale_price)
        save_button = create_styled_button(
            scrollable_form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=save
        )
        save_button.pack(fill='x', padx=20, pady=(0, 20))

    def edit_product(self, product_id=None):
        """Edit an existing product"""
        if product_id is None:
            return
        # Find the product by id
        product = None
        for p in self.products:
            if p.get('id') == product_id:
                product = p
                break
        if not product:
            show_error("Product not found", self.current_language)
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("edit_product", "Edit Product", "تعديل المنتج"))
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
            text=self.get_bilingual("edit_product", "Edit Product", "تعديل المنتج"),
            style='heading'
        )
        title_label.pack(pady=20)
        
        # Product name
        name_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_name", "Product Name", "اسم المنتج"),
            style='subheading'
        )
        name_label.pack(pady=(0, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, product['name'])
        name_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product flavor
        flavor_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_flavor", "Product Flavor", "نكهة المنتج"),
            style='subheading'
        )
        flavor_label.pack(pady=(0, 5))
        
        flavor_menu = create_styled_option_menu(
            form_frame,
            values=[self.LANGUAGES[self.current_language].get(f, f.capitalize()) for f in self.hookah_flavors]
        )
        flavor_menu.set(product['flavor'])
        flavor_menu.pack(fill='x', padx=20, pady=(0, 10))
        
        # Product weight
        weight_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("product_weight", "Product Weight", "وزن المنتج"),
            style='subheading'
        )
        weight_label.pack(pady=(0, 5))
        weight_options = [
            self.get_bilingual("weight_50g", "50g", "50 جم"),
            self.get_bilingual("weight_100g", "100g", "100 جم"),
            self.get_bilingual("weight_150g", "150g", "150 جم"),
            self.get_bilingual("weight_250g", "250g", "250 جم"),
            self.get_bilingual("weight_300g", "300g", "300 جم"),
            self.get_bilingual("weight_350g", "350g", "350 جم"),
            self.get_bilingual("weight_400g", "400g", "400 جم"),
            self.get_bilingual("weight_450g", "450g", "450 جم"),
            self.get_bilingual("weight_500g", "500g", "500 جم"),
            self.get_bilingual("weight_750g", "750g", "750 جم"),
            self.get_bilingual("weight_1kg", "1kg", "1 كجم"),
            self.get_bilingual("weight_1500g", "1500g", "1500 جم"),
            self.get_bilingual("weight_11750g", "11750g", "1750 جم"),
            self.get_bilingual("weight_2kg", "2kg", "2 كجم"),
            self.get_bilingual("weight_2500g", "2500g", "2500 جم"),
            self.get_bilingual("weight_3kg", "3kg", "3 كجم"),
            self.get_bilingual("weight_3500g", "3500g", "3500 جم"),
            self.get_bilingual("weight_4kg", "4kg", "4 كجم"),
            self.get_bilingual("weight_4500g", "4500g", "4500 جم"),
        ]
        # أضف خيارات 2-10 كيلو
        for kg in range(2, 11):
            weight_options.append(self.get_bilingual(f"weight_{kg}kg", f"{kg}kg", f"{kg} كجم"))
        weight_menu = create_styled_option_menu(
            form_frame,
            values=["-"] + weight_options
        )
        weight_menu.set(product.get('weight', '-'))
        weight_menu.pack(fill='x', padx=20, pady=(0, 10))
        
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
        if self.selected_image_path and os.path.exists(str(self.selected_image_path)):
            try:
                img = Image.open(str(self.selected_image_path))
                img.thumbnail((100, 100)) # Resize for preview
                img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                self.edit_image_preview.configure(image=img_tk, text="")
            except Exception as e:
                print(f"[ERROR] Could not load image for preview: {e}")

        # Location (Dropdown)
        location_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("location", "Location", "المكان"),
            style='subheading'
        )
        location_label.pack(pady=(0, 5))
        stores_file = os.path.join("excel_data", "stores.json")
        locations = ["المحل / Shop"]
        if os.path.exists(stores_file):
            with open(stores_file, 'r', encoding='utf-8') as f:
                stores = json.load(f)
                locations += [store['name'] for store in stores]
        location_menu = create_styled_option_menu(
            form_frame,
            values=locations
        )
        location_menu.set(product.get('location', locations[0]))
        location_menu.pack(fill='x', padx=20, pady=(0, 10))
        # Barcode (إجباري)
        barcode_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("barcode", "Barcode", "باركود"),
            style='subheading'
        )
        barcode_label.pack(pady=(0, 5))
        barcode_entry = create_styled_entry(form_frame)
        barcode_entry.insert(0, product.get('barcode', ''))
        barcode_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Wholesale Supplier Price
        wholesale_supplier_price_label = create_styled_label(form_frame, text="Wholesale Supplier Price / سعر الجملة من التاجر", style='subheading')
        wholesale_supplier_price_label.pack(pady=(0, 5))
        wholesale_supplier_price_entry = create_styled_entry(form_frame)
        wholesale_supplier_price_entry.insert(0, str(product.get('wholesale_supplier_price', '')))
        wholesale_supplier_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Wholesale Sale Price
        wholesale_sale_price_label = create_styled_label(form_frame, text="Wholesale Sale Price / سعر الجملة للبيع", style='subheading')
        wholesale_sale_price_label.pack(pady=(0, 5))
        wholesale_sale_price_entry = create_styled_entry(form_frame)
        wholesale_sale_price_entry.insert(0, str(product.get('wholesale_sale_price', '')))
        wholesale_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Retail Sale Price
        retail_sale_price_label = create_styled_label(form_frame, text="Retail Sale Price / سعر البيع قطاعى", style='subheading')
        retail_sale_price_label.pack(pady=(0, 5))
        retail_sale_price_entry = create_styled_entry(form_frame)
        retail_sale_price_entry.insert(0, str(product.get('retail_sale_price', '')))
        retail_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # Update button
        update_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("update", "Update", "تحديث"),
            style='primary',
            command=lambda: self.update_product(
                dialog,
                product['name'],
                name_entry.get(),
                flavor_menu.get(),
                weight_menu.get(),
                self.selected_image_path,
                barcode_entry.get(),
                location_menu.get(),
                wholesale_supplier_price_entry.get(),
                wholesale_sale_price_entry.get(),
                retail_sale_price_entry.get()
            )
        )
        update_button.pack(pady=20)
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=lambda: self.update_product(
                dialog,
                product['name'],
                name_entry.get(),
                flavor_menu.get(),
                weight_menu.get(),
                self.selected_image_path,
                barcode_entry.get(),
                location_menu.get(),
                wholesale_supplier_price_entry.get(),
                wholesale_sale_price_entry.get(),
                retail_sale_price_entry.get()
            )
        )
        save_button.pack(pady=10)
        
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

    def save_product(self, dialog, name, flavor, weight, status, image_path, barcode, location, wholesale_supplier_price, wholesale_sale_price, retail_sale_price):
        """Save a new product"""
        if not name or not barcode:
            show_error(self.get_bilingual("name_weight_required", "Product Name and Weight are required.", "اسم المنتج، ووزن المنتج مطلوبان"), "en")
            return
        # تحقق من تكرار الباركود أو الاسم في أماكن أخرى
        if any((p.get('name', '').lower() == name.lower() or p.get('barcode', '') == barcode) for p in self.products if p.get('location', '').strip().lower() != location.strip().lower()):
            show_error(self.get_bilingual("product_exists", "Product with this name or barcode already exists in another location.", "يوجد منتج بهذا الاسم أو الباركود في مكان آخر."), "en")
            return
        new_product = {
            'id': get_next_id('products'),
            'name': name,
            'flavor': flavor,
            'weight': weight,
            'status': status,
            'image_path': image_path,
            'barcode': barcode,
            'location': location,
            'wholesale_supplier_price': wholesale_supplier_price,
            'wholesale_sale_price': wholesale_sale_price,
            'retail_sale_price': retail_sale_price
        }
        self.products.append(new_product)
        save_data("products", self.products)
        if self.record_sale_instance:
            self.record_sale_instance.refresh_products()
        self.refresh_products()
        dialog.destroy()
        show_success(self.get_bilingual("product_added_success", "Product added successfully!", "تمت إضافة المنتج بنجاح!"), "en")

    def update_product(self, dialog, old_name, name, flavor, weight, image_path, barcode, location, wholesale_supplier_price, wholesale_sale_price, retail_sale_price):
        """Update an existing product"""
        if not name or not barcode:
            show_error(self.get_bilingual("name_weight_required", "Product Name and Weight are required.", "اسم المنتج، ووزن المنتج مطلوبان"), "en")
            return
        # Find the product by old_name and update
        for product in self.products:
            if product.get('name', '') == old_name:
                product['name'] = name
                product['flavor'] = flavor
                product['weight'] = weight
                product['image_path'] = image_path
                product['barcode'] = barcode
                product['location'] = location
                product['wholesale_supplier_price'] = wholesale_supplier_price
                product['wholesale_sale_price'] = wholesale_sale_price
                product['retail_sale_price'] = retail_sale_price
                break
        save_data("products", self.products)
        if self.record_sale_instance:
            self.record_sale_instance.refresh_products()
        self.refresh_products()
        dialog.destroy()
        show_success(self.get_bilingual("product_updated_success", "Product updated successfully!", "تم تحديث المنتج بنجاح!"), "en")

    def delete_product(self, product_id):
        """Delete a product by id"""
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if not product:
            show_error(self.LANGUAGES[self.current_language].get("product_not_found", "Product not found."), self.current_language)
            return
        confirm = messagebox.askyesno(
            self.LANGUAGES[self.current_language].get("confirm_delete", "Confirm Delete"),
            self.LANGUAGES[self.current_language].get("confirm_delete_product", f"Are you sure you want to delete {product.get('name', 'this product')}?")
        )
        if confirm:
            try:
                self.products.remove(product)
                save_data("products", self.products)
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
        """فلترة المنتجات حسب البحث في الاسم أو الباركود، وإذا كان البحث يطابق باركود منتج يظهر المنتج فقط"""
        query = getattr(self, 'search_var', None)
        if query is not None:
            query = query.get().strip()
        else:
            return
        all_products = load_data("products") or []
        if query:
            # إذا كان البحث يطابق باركود منتج بالضبط
            product_by_barcode = next((p for p in all_products if str(p.get('barcode', '')) == query), None)
            if product_by_barcode:
                self.products = [product_by_barcode]
            else:
                self.products = [p for p in all_products if query.lower() in str(p.get('name', '')).lower() or query in str(p.get('barcode', ''))]
        else:
            self.products = all_products
        self.current_page = 0
        self.manage_products()

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def goto_next_page(self):
        filtered_products = [p for p in self.products if str(p.get('status', '')).strip().lower() in ['active', 'available'] and p.get('source', 'defined') != 'inventory']
        total_products = len(filtered_products)
        total_pages = max(1, (total_products + self.products_per_page - 1) // self.products_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.manage_products()

    def goto_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.manage_products()
