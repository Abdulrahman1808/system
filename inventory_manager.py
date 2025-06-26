import customtkinter as ctk
from tkinter import ttk, messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id, import_from_excel
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label, create_styled_option_menu
)

class InventoryManager:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.inventory = load_data("inventory") or []
        self.selected_items = set()
        self.selected_store = "All Stores"  # المخزن المحدد للفلترة

    def refresh_inventory(self):
        """Refresh the inventory list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            if import_from_excel('inventory'):
                print("[DEBUG] Successfully imported data from Excel")
            else:
                print("[DEBUG] No Excel data to import or import failed")

            # Load inventory from database
            self.inventory = load_data("inventory") or []
            print(f"[DEBUG] Loaded inventory count: {len(self.inventory)}")
            print(f"[DEBUG] Loaded inventory: {self.inventory}")
            
            # Refresh the display
            self.manage_inventory()
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            show_error(f"Error refreshing inventory: {str(e)}", self.current_language)

    def manage_inventory(self):
        """Create a modern inventory management interface"""
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
            text=self.LANGUAGES[self.current_language].get("manage_inventory", "Manage Inventory"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_inventory
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_items = len(self.inventory)
        low_stock = len([i for i in self.inventory if i.get('quantity', 0) < i.get('min_quantity', 0)])
        out_of_stock = len([i for i in self.inventory if i.get('quantity', 0) <= 0])
        
        # Create summary cards
        summary_cards = [
            ("total_items", "Total Items", total_items),
            ("low_stock", "Low Stock", low_stock),
            ("out_of_stock", "Out of Stock", out_of_stock)
        ]
        
        for i, (key, default_text, value) in enumerate(summary_cards):
            card = create_styled_frame(summary_frame, style='card')
            card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
            
            label = create_styled_label(
                card,
                text=self.get_bilingual(key, default_text, default_text),
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
        
        # فلترة حسب المخزن
        filter_label = create_styled_label(
            search_frame,
            text=self.get_bilingual("filter_by_store", "Filter by Store", "تصفية حسب المخزن"),
            style='subheading'
        )
        filter_label.pack(side='left', padx=20, pady=20)
        
        # قائمة المخازن المتاحة
        store_names = self.get_store_names()
        self.store_filter = create_styled_option_menu(
            search_frame,
            values=["All Stores"] + store_names
        )
        self.store_filter.set(self.selected_store)
        self.store_filter.pack(side='left', padx=20, pady=20)
        
        # زر تطبيق الفلتر
        apply_filter_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("apply_filter", "Apply Filter", "تطبيق الفلتر"),
            style='outline',
            command=self.apply_store_filter
        )
        apply_filter_button.pack(side='left', padx=20, pady=20)
        
        search_entry = create_styled_entry(
            search_frame,
            placeholder_text=self.get_bilingual("search_inventory", "Search inventory...", "بحث في المخزون")
        )
        search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        
        filter_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("filter", "Filter", "تصفية"),
            style='outline'
        )
        filter_button.pack(side='right', padx=20, pady=20)
        
        add_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("add_item", "Add Item", "إضافة عنصر"),
            style='primary',
            command=self.add_item
        )
        add_button.pack(side='right', padx=20, pady=20)
        
        # زر حذف المحدد
        delete_selected_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("delete_selected", "Delete Selected", "حذف المحدد"),
            style='error',
            command=self.delete_selected_items
        )
        delete_selected_button.pack(side='right', padx=20, pady=20)
        
        # Inventory table (scrollable)
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Use CTkScrollableFrame for the inventory list
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        
        # Table headers
        headers = [
            ("select", "Select"),
            ("item_name", "Item Name"),
            ("category", "Category"),
            ("quantity", "Quantity"),
            ("min_quantity", "Min Quantity"),
            ("location", "Location"),
            ("actions", "Actions")
        ]
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=self.get_bilingual(key, default_text, default_text),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Inventory list
        # فلترة المنتجات حسب المخزن المحدد
        filtered_inventory = self.inventory
        if self.selected_store != "All Stores":
            filtered_inventory = [item for item in self.inventory if item.get('location', '') == self.selected_store]
        
        for i, item in enumerate(filtered_inventory, 1):
            # Checkbox لتحديد العنصر
            var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                scrollable_table,
                variable=var,
                text="",
                command=lambda v=var, item_id=item.get('id'): self.toggle_select_item(v, item_id)
            )
            checkbox.grid(row=i, column=0, padx=10, pady=10)
            
            name_label = create_styled_label(
                scrollable_table,
                text=item.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            category_label = create_styled_label(
                scrollable_table,
                text=item.get('category', ''),
                style='body'
            )
            category_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            quantity_label = create_styled_label(
                scrollable_table,
                text=str(item.get('quantity', 0)),
                style='body'
            )
            quantity_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            min_quantity_label = create_styled_label(
                scrollable_table,
                text=str(item.get('min_quantity', 0)),
                style='body'
            )
            min_quantity_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            location_label = create_styled_label(
                scrollable_table,
                text=item.get('location', ''),
                style='body'
            )
            location_label.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=6, padx=10, pady=10, sticky='w')
            
            edit_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("edit", "Edit", "تعديل"),
                style='outline',
                width=80,
                command=lambda i=item: self.edit_item(i)
            )
            edit_button.pack(side='left', padx=5)
            
            delete_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("delete", "Delete", "حذف"),
                style='outline',
                width=80,
                command=lambda i=item: self.delete_item(i)
            )
            delete_button.pack(side='left', padx=5)

    def add_item(self):
        """Add a new inventory item (اختيار من المنتجات المعرفة فقط)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("add_item", "Add Item", "إضافة عنصر"))
        dialog.geometry("400x600")
        
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True)
        
        # تحميل المنتجات المعرفة
        products = load_data("products") or []
        product_names = [p['name'] for p in products]
        
        # اختيار المنتج فقط (بدون إدخال يدوي)
        product_label = create_styled_label(form_frame, text=self.get_bilingual("product_name", "Product Name", "اسم المنتج"), style='subheading')
        product_label.pack(pady=(20, 5))
        product_menu = create_styled_option_menu(form_frame, values=product_names)
        product_menu.pack(fill='x', padx=20, pady=(0, 15))
        
        # مواصفات المنتج (للقراءة فقط)
        type_label = create_styled_label(form_frame, text=self.get_bilingual("product_type", "Type", "نوع المنتج"), style='subheading')
        type_label.pack(pady=(0, 5))
        type_value = create_styled_label(form_frame, text="-", style='body')
        type_value.pack(fill='x', padx=20, pady=(0, 10))
        flavor_label = create_styled_label(form_frame, text=self.get_bilingual("product_flavor", "Flavor", "نكهة المنتج"), style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_value = create_styled_label(form_frame, text="-", style='body')
        flavor_value.pack(fill='x', padx=20, pady=(0, 10))
        weight_label = create_styled_label(form_frame, text=self.get_bilingual("product_weight", "Weight", "وزن المنتج"), style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_value = create_styled_label(form_frame, text="-", style='body')
        weight_value.pack(fill='x', padx=20, pady=(0, 10))
        barcode_label = create_styled_label(form_frame, text=self.get_bilingual("barcode", "Barcode", "باركود"), style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_value = create_styled_label(form_frame, text="-", style='body')
        barcode_value.pack(fill='x', padx=20, pady=(0, 10))
        # عند اختيار منتج، اعرض المواصفات
        def on_product_select(value):
            selected = next((p for p in products if p['name'] == value), None)
            if selected:
                type_value.configure(text=selected.get('type', '-'))
                flavor_value.configure(text=selected.get('flavor', '-'))
                weight_value.configure(text=selected.get('weight', '-'))
                barcode_value.configure(text=selected.get('barcode', '-'))
        product_menu.configure(command=on_product_select)
        
        # الكمية
        quantity_label = create_styled_label(form_frame, text=self.get_bilingual("quantity", "Quantity", "الكمية"), style='subheading')
        quantity_label.pack(pady=(0, 5))
        quantity_entry = create_styled_entry(form_frame)
        quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # الكمية الصغرى
        min_quantity_label = create_styled_label(form_frame, text=self.get_bilingual("min_quantity", "Min Quantity", "الكمية الصغرى"), style='subheading')
        min_quantity_label.pack(pady=(0, 5))
        min_quantity_entry = create_styled_entry(form_frame)
        min_quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # الموقع
        location_label = create_styled_label(form_frame, text=self.get_bilingual("location", "Location", "الموقع"), style='subheading')
        location_label.pack(pady=(0, 5))
        import json, os
        stores_file = os.path.join("excel_data", "stores.json")
        store_names = ["المحل / Shop"]
        if os.path.exists(stores_file):
            with open(stores_file, 'r', encoding='utf-8') as f:
                stores = json.load(f)
                store_names += [store['name'] for store in stores]
        location_menu = create_styled_option_menu(form_frame, values=store_names)
        location_menu.pack(fill='x', padx=20, pady=(0, 15))
        
        # زر الحفظ
        save_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=lambda: self.save_item(
                dialog,
                product_menu.get(),
                type_value.cget('text'),
                int(quantity_entry.get() or 0),
                int(min_quantity_entry.get() or 0),
                location_menu.get()
            )
        )
        save_button.pack(pady=20)

    def edit_item(self, item):
        """Edit an existing inventory item"""
        # Create a new window for editing item
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("edit_item", "Edit Item", "تعديل العنصر"))
        dialog.geometry("400x500")
        
        # Create scrollable frame for the form content
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Item form
        form_frame = create_styled_frame(scrollable_form_frame, style='card') # Use styled frame inside scrollable
        form_frame.pack(fill='both', expand=True) # Removed padx, pady as they are on the scrollable frame
        
        # Name
        name_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("item_name", "Item Name", "اسم العنصر"),
            style='subheading'
        )
        name_label.pack(pady=(20, 5))
        
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, item.get('name', ''))
        name_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Category
        category_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("category", "Category", "الفئة"),
            style='subheading'
        )
        category_label.pack(pady=(0, 5))
        
        category_entry = create_styled_entry(form_frame)
        category_entry.insert(0, item.get('category', ''))
        category_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Quantity
        quantity_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("quantity", "Quantity", "الكمية"),
            style='subheading'
        )
        quantity_label.pack(pady=(0, 5))
        
        quantity_entry = create_styled_entry(form_frame)
        quantity_entry.insert(0, str(item.get('quantity', 0)))
        quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Min Quantity
        min_quantity_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("min_quantity", "Min Quantity", "الكمية الصغرى"),
            style='subheading'
        )
        min_quantity_label.pack(pady=(0, 5))
        
        min_quantity_entry = create_styled_entry(form_frame)
        min_quantity_entry.insert(0, str(item.get('min_quantity', 0)))
        min_quantity_entry.pack(fill='x', padx=20, pady=(0, 15))
        
        # Location
        location_label = create_styled_label(
            form_frame,
            text=self.get_bilingual("location", "Location", "الموقع"),
            style='subheading'
        )
        location_label.pack(pady=(0, 5))
        import json, os
        stores_file = os.path.join("excel_data", "stores.json")
        store_names = ["المحل / Shop"]
        if os.path.exists(stores_file):
            with open(stores_file, 'r', encoding='utf-8') as f:
                stores = json.load(f)
                store_names += [store['name'] for store in stores]
        location_menu = create_styled_option_menu(
            form_frame,
            values=store_names
        )
        location_menu.set(item.get('location', store_names[0]))
        location_menu.pack(fill='x', padx=20, pady=(0, 15))
        
        # Save button
        save_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=lambda: self.update_item(
                dialog,
                item,
                name_entry.get(),
                category_entry.get(),
                int(quantity_entry.get() or 0),
                int(min_quantity_entry.get() or 0),
                location_menu.get()
            )
        )
        save_button.pack(pady=20)
        
        # Cancel button
        cancel_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("cancel", "Cancel", "إلغاء"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(pady=20)

    def save_item(self, dialog, name, category, quantity, min_quantity, location):
        """Save a new inventory item"""
        if not name or not category or quantity < 0 or min_quantity < 0:
            show_error(self.get_bilingual("invalid_item", "Please fill all fields correctly", "يرجى ملء جميع الحقون الصحيحة"), self.current_language)
            return

        new_item = {
            'id': get_next_id('inventory'),
            'name': name,
            'category': category,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'location': location
        }
        
        self.inventory.append(new_item)
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.get_bilingual("item_added", "Item added successfully", "تم إضافة العنصر بنجاح"), self.current_language)

    def update_item(self, dialog, item, name, category, quantity, min_quantity, location):
        """Update an existing inventory item"""
        if not name or not category or quantity < 0 or min_quantity < 0:
            show_error(self.get_bilingual("invalid_item", "Please fill all fields correctly", "يرجى ملء جميع الحقون الصحيحة"), self.current_language)
            return

        item.update({
            'name': name,
            'category': category,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'location': location
        })
        
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.get_bilingual("item_updated", "Item updated successfully", "تم تحديث العنصر بنجاح"), self.current_language)

    def delete_item(self, item):
        """Delete an inventory item"""
        self.inventory.remove(item)
        save_data("inventory", self.inventory)
        self.manage_inventory()
        show_success(self.get_bilingual("item_deleted", "Item deleted successfully", "تم حذف العنصر بنجاح"), self.current_language)

    def get_store_names(self):
        """Load store names from stores.json file"""
        import json, os
        stores_file = os.path.join("excel_data", "stores.json")
        if not os.path.exists(stores_file):
            return []
        with open(stores_file, 'r', encoding='utf-8') as f:
            stores = json.load(f)
        return [store['name'] for store in stores]

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def toggle_select_item(self, var, item_id):
        if var.get():
            self.selected_items.add(item_id)
        else:
            self.selected_items.discard(item_id)

    def delete_selected_items(self):
        if not self.selected_items:
            show_error(self.get_bilingual("no_selection", "No items selected", "لم يتم تحديد عناصر"), self.current_language)
            return
        confirm = messagebox.askyesno(
            self.get_bilingual("confirm_delete", "Confirm Delete", "تأكيد الحذف"),
            self.get_bilingual("delete_selected_confirm", "Are you sure you want to delete the selected items?", "هل أنت متأكد أنك تريد حذف العناصر المحددة؟")
        )
        if not confirm:
            return
        self.inventory = [item for item in self.inventory if item.get('id') not in self.selected_items]
        save_data("inventory", self.inventory)
        self.selected_items.clear()
        show_success(self.get_bilingual("items_deleted", "Selected items deleted successfully", "تم حذف العناصر المحددة بنجاح"), self.current_language)
        self.refresh_inventory()

    def apply_store_filter(self):
        """Apply the selected store filter"""
        selected_store = self.store_filter.get()
        if selected_store == "All Stores":
            self.selected_store = "All Stores"
            self.refresh_inventory()
        else:
            self.selected_store = selected_store
            self.refresh_inventory()
