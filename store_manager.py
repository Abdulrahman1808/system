import customtkinter as ctk
from tkinter import messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id
from theme import (
    COLORS, create_styled_button, create_styled_entry, create_styled_frame, create_styled_label, create_styled_option_menu
)
from tkcalendar import DateEntry
from datetime import datetime

class StoreManager:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.products = load_data("store_products") or []
        self.inventory = load_data("inventory") or []
        self.current_page = 0
        self.items_per_page = 20
        self.add_inventory_dialog = None
        self.add_inventory_menu = None

    def refresh_store(self):
        self.products = load_data("store_products") or []
        self.inventory = load_data("inventory") or []
        # تحديث القائمة المنسدلة فقط إذا كانت نافذة الإضافة مفتوحة ومازالت موجودة
        if (self.add_inventory_dialog and self.add_inventory_menu and 
            hasattr(self.add_inventory_dialog, 'winfo_exists') and 
            self.add_inventory_dialog.winfo_exists()):
            try:
                inventory_names = [item['name'] for item in self.inventory if item.get('name', '').strip()]
                self.add_inventory_menu.configure(values=inventory_names)
            except Exception as e:
                print(f"[WARNING] Failed to update dropdown: {e}")
                self.add_inventory_dialog = None
                self.add_inventory_menu = None
        else:
            self.add_inventory_dialog = None
            self.add_inventory_menu = None
        self.manage_store()

    def manage_store(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
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
            text=self.LANGUAGES[self.current_language].get("manage_store", "Manage Store"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_store
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        # زر إضافة من المخزن
        add_from_inventory_btn = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("add_from_inventory", "Add from Inventory"),
            style='primary',
            command=self.add_from_inventory_dialog
        )
        add_from_inventory_btn.pack(side='right', padx=20, pady=20)
        
        # فلترة منتجات المحل فقط
        store_products = [p for p in self.products if p.get('location', '').strip().lower() in ['المحل', 'shop', 'المحل / shop']]
        # ترتيب حسب التاريخ تنازلياً
        def parse_date(date_str):
            try:
                # جرب عدة تنسيقات
                for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except Exception:
                        continue
                return datetime.min
            except Exception:
                return datetime.min
        store_products.sort(key=lambda p: parse_date(p.get('date', '')), reverse=True)
        # Pagination
        total_items = len(store_products)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_products = store_products[start_idx:end_idx]
        
        # جدول المنتجات
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        headers = [
            ("product_name", "Product Name / اسم المنتج"),
            ("barcode", "Barcode / باركود"),
            ("product_type", "Type / النوع"),
            ("retail_quantity", "Retail Qty / عدد القطاعي"),
            ("price", "Retail Price / سعر القطاعي"),
            ("date", "Date / التاريخ"),
            ("actions", "Actions / الإجراءات")
        ]
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=default_text,
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        for i, product in enumerate(page_products, 1):
            name_label = create_styled_label(
                scrollable_table,
                text=product.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            barcode_label = create_styled_label(
                scrollable_table,
                text=product.get('barcode', ''),
                style='body'
            )
            barcode_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            type_label = create_styled_label(
                scrollable_table,
                text=product.get('type', ''),
                style='body'
            )
            type_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            qty_label = create_styled_label(
                scrollable_table,
                text=str(product.get('quantity', 0)),
                style='body'
            )
            qty_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            retail_label = create_styled_label(
                scrollable_table,
                text=str(product.get('retail_quantity', 0)),
                style='body'
            )
            retail_label.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            price_label = create_styled_label(
                scrollable_table,
                text=f"${float(product.get('retail_price', product.get('price', 0)) or 0):.2f}",
                style='body'
            )
            price_label.grid(row=i, column=5, padx=10, pady=10, sticky='w')
            
            date_label = create_styled_label(
                scrollable_table,
                text=self.format_date(product.get('date', '')),
                style='body'
            )
            date_label.grid(row=i, column=6, padx=10, pady=10, sticky='w')
            
            # أزرار الإجراءات
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=7, padx=10, pady=10, sticky='w')
            
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=80,
                command=lambda pid=product.get('id'): self.edit_store_product(pid)
            )
            edit_button.pack(side='left', padx=5)
            
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='error',
                width=80,
                command=lambda pid=product.get('id'): self.delete_store_product(pid)
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

    def add_from_inventory_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("add_from_inventory", "Add from Inventory"))
        dialog.geometry("400x470")
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        inventory_names = [item['name'] for item in self.inventory if item.get('name', '').strip()]
        inventory_menu = create_styled_option_menu(form_frame, values=inventory_names)
        inventory_menu.pack(fill='x', padx=20, pady=(20, 10))
        self.add_inventory_dialog = dialog
        self.add_inventory_menu = inventory_menu
        
        # دالة تنظيف المراجع عند إغلاق النافذة
        def cleanup_references():
            self.add_inventory_dialog = None
            self.add_inventory_menu = None
        
        # ربط دالة التنظيف بإغلاق النافذة
        dialog.protocol("WM_DELETE_WINDOW", lambda: [cleanup_references(), dialog.destroy()])
        
        # عدد القطاعي
        retail_qty_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("retail_quantity", "Retail Quantity"), style='subheading')
        retail_qty_label.pack(pady=(0, 5))
        retail_qty_entry = create_styled_entry(form_frame)
        retail_qty_entry.pack(fill='x', padx=20, pady=(0, 10))
        # سعر القطاعي
        retail_price_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("retail_price", "Retail Price"), style='subheading')
        retail_price_label.pack(pady=(0, 5))
        retail_price_entry = create_styled_entry(form_frame)
        retail_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        # باقي الحقول كما هي
        qty_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("quantity", "Quantity"), style='subheading')
        qty_label.pack(pady=(0, 5))
        qty_entry = create_styled_entry(form_frame)
        qty_entry.pack(fill='x', padx=20, pady=(0, 10))
        # حقل السعر
        price_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("price", "Price"), style='subheading')
        price_label.pack(pady=(0, 5))
        price_entry = create_styled_entry(form_frame)
        price_entry.pack(fill='x', padx=20, pady=(0, 10))
        # نوع المنتج (قائمة منسدلة)
        type_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_type", "Type") + " / نوع المنتج", style='subheading')
        type_label.pack(pady=(0, 5))
        type_options = [self.LANGUAGES[self.current_language].get("wholesale", "Wholesale"), self.LANGUAGES[self.current_language].get("retail", "Retail")]
        type_menu = create_styled_option_menu(form_frame, values=type_options)
        type_menu.pack(fill='x', padx=20, pady=(0, 10))
        # التاريخ
        date_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("date", "Date") + " / التاريخ", style='subheading')
        date_label.pack(pady=(0, 5))
        date_entry = DateEntry(form_frame, width=18)
        date_entry.pack(fill='x', padx=20, pady=(0, 10))
        # نكهة المنتج
        flavor_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_flavor", "Flavor") + " / نكهة المنتج", style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_value = create_styled_label(form_frame, text="-", style='body')
        flavor_value.pack(fill='x', padx=20, pady=(0, 10))
        # وزن المنتج
        weight_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_weight", "Weight") + " / وزن المنتج", style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_value = create_styled_label(form_frame, text="-", style='body')
        weight_value.pack(fill='x', padx=20, pady=(0, 10))
        # باركود (عرض فقط)
        barcode_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("barcode", "Barcode") + " / باركود", style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_value = create_styled_label(form_frame, text="-", style='body')
        barcode_value.pack(fill='x', padx=20, pady=(0, 10))
        # عند اختيار منتج من القائمة
        def on_inventory_select(selected_name):
            selected = next((item for item in self.inventory if item.get('name', '') == selected_name), None)
            if selected:
                type_menu.set(selected.get('type', type_options[0]))
                flavor_value.configure(text=selected.get('flavor', '-'))
                weight_value.configure(text=selected.get('weight', '-'))
                barcode_value.configure(text=selected.get('barcode', '-'))
            else:
                type_menu.set(type_options[0])
                flavor_value.configure(text='-')
                weight_value.configure(text='-')
                barcode_value.configure(text='-')
        inventory_menu.configure(command=on_inventory_select)
        def transfer():
            selected_name = inventory_menu.get()
            try:
                qty = int(qty_entry.get())
                price = float(price_entry.get()) if price_entry.get() else 0
                retail_qty = int(retail_qty_entry.get()) if retail_qty_entry.get() else 0
                retail_price = float(retail_price_entry.get()) if retail_price_entry.get() else 0
            except Exception:
                show_error("Invalid quantity", self.current_language)
                return
            transfer_type = type_menu.get()
            transfer_date = date_entry.get()
            # ابحث عن المنتج في المخزن
            inv_item = next((item for item in self.inventory if item['name'] == selected_name), None)
            if not inv_item or inv_item.get('quantity', 0) < qty:
                show_error("Not enough quantity in inventory", self.current_language)
                return
            # ابحث عن المنتج في المحل بنفس الاسم ونفس التاريخ فقط
            store_item = next((p for p in self.products if p['name'] == selected_name and p.get('location', '').strip().lower() in ['المحل', 'shop', 'المحل / shop'] and p.get('date', '') == transfer_date), None)
            if store_item:
                if transfer_type == self.LANGUAGES[self.current_language].get("wholesale", "Wholesale"):
                    store_item['quantity'] = store_item.get('quantity', 0) + qty
                    store_item['price'] = price
                    store_item['retail_quantity'] = retail_qty
                    store_item['retail_price'] = retail_price
                    store_item['date'] = transfer_date
                else:
                    store_item['retail_quantity'] = store_item.get('retail_quantity', 0) + qty
                    store_item['price'] = price
                    store_item['retail_price'] = retail_price
                    store_item['date'] = transfer_date
            else:
                # أضف منتج جديد للمحل بنفس البيانات الأساسية
                new_product = inv_item.copy()
                if transfer_type == self.LANGUAGES[self.current_language].get("wholesale", "Wholesale"):
                    new_product['quantity'] = qty
                    new_product['retail_quantity'] = retail_qty
                    new_product['retail_price'] = retail_price
                    new_product['date'] = transfer_date
                else:
                    new_product['quantity'] = 0
                    new_product['retail_quantity'] = qty
                    new_product['retail_price'] = retail_price
                    new_product['date'] = transfer_date
                new_product['id'] = get_next_id('store_products')
                new_product['location'] = 'المحل / Shop'
                new_product['source'] = 'inventory'
                new_product['price'] = price
                self.products.append(new_product)
            # خصم الكمية من المخزن
            inv_item['quantity'] -= qty
            # خصم الكمية من المنتج في ملف المنتجات الخاص بالمخزن الأصلي
            inventory_location = inv_item.get('location', None)
            if inventory_location:
                product_in_inventory = next((p for p in self.products if p['name'] == selected_name and p.get('location', '') == inventory_location), None)
                if product_in_inventory:
                    if transfer_type == self.LANGUAGES[self.current_language].get("wholesale", "Wholesale"):
                        product_in_inventory['quantity'] = max(0, product_in_inventory.get('quantity', 0) - qty)
                    else:
                        product_in_inventory['retail_quantity'] = max(0, product_in_inventory.get('retail_quantity', 0) - qty)
            # --- حفظ البيانات في جميع المسارات ---
            save_data("store_products", self.products)
            save_data("inventory", self.inventory)
            # --- نهاية الحفظ ---
            print(f"[INFO] Product '{selected_name}' transferred as {transfer_type} on {transfer_date}")
            show_success("تم النقل بنجاح!", self.current_language)
            # تنظيف المراجع قبل إغلاق النافذة
            self.add_inventory_dialog = None
            self.add_inventory_menu = None
            dialog.destroy()
            self.refresh_store()
        transfer_btn = create_styled_button(form_frame, text=self.LANGUAGES[self.current_language].get("transfer", "Transfer"), style='primary', command=transfer)
        transfer_btn.pack(pady=20)

    def edit_store_product(self, product_id):
        """Edit a store product"""
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if not product:
            show_error("Product not found", self.current_language)
            return
        
        # فتح نافذة تعديل بسيطة
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Store Product")
        dialog.geometry("300x200")
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        
        form_frame = create_styled_frame(dialog, style='card')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # الكمية
        qty_label = create_styled_label(form_frame, text="Quantity / الكمية", style='subheading')
        qty_label.pack(pady=(0, 5))
        qty_entry = create_styled_entry(form_frame)
        qty_entry.insert(0, str(product.get('quantity', 0)))
        qty_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # الكمية القطاعية
        retail_qty_label = create_styled_label(form_frame, text="Retail Quantity / عدد القطاعي", style='subheading')
        retail_qty_label.pack(pady=(0, 5))
        retail_qty_entry = create_styled_entry(form_frame)
        retail_qty_entry.insert(0, str(product.get('retail_quantity', 0)))
        retail_qty_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # سعر القطاعي
        retail_price_label = create_styled_label(form_frame, text="Retail Price / سعر القطاعي", style='subheading')
        retail_price_label.pack(pady=(0, 5))
        retail_price_entry = create_styled_entry(form_frame)
        retail_price_entry.insert(0, str(product.get('retail_price', product.get('price', 0))))
        retail_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # نوع المنتج
        type_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_type", "Type") + " / نوع المنتج", style='subheading')
        type_label.pack(pady=(0, 5))
        type_value = create_styled_label(form_frame, text=product.get('type', '-'), style='body')
        type_value.pack(fill='x', padx=20, pady=(0, 10))
        
        # نكهة المنتج
        flavor_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_flavor", "Flavor") + " / نكهة المنتج", style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_value = create_styled_label(form_frame, text=product.get('flavor', '-'), style='body')
        flavor_value.pack(fill='x', padx=20, pady=(0, 10))
        
        # وزن المنتج
        weight_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_weight", "Weight") + " / وزن المنتج", style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_value = create_styled_label(form_frame, text=product.get('weight', '-'), style='body')
        weight_value.pack(fill='x', padx=20, pady=(0, 10))
        
        # باركود
        barcode_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("barcode", "Barcode") + " / باركود", style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_value = create_styled_label(form_frame, text=product.get('barcode', '-'), style='body')
        barcode_value.pack(fill='x', padx=20, pady=(0, 10))
        
        # تاريخ التنزيل
        date_label = create_styled_label(form_frame, text="Date / التاريخ", style='subheading')
        date_label.pack(pady=(0, 5))
        date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        if product.get('date', ''):
            try:
                date_entry.set_date(product.get('date', ''))
            except Exception:
                pass
        date_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        def save_changes():
            try:
                new_qty = int(qty_entry.get())
                new_retail_qty = int(retail_qty_entry.get())
                new_retail_price = float(retail_price_entry.get()) if retail_price_entry.get() else 0
                new_date = date_entry.get()
                product['quantity'] = new_qty
                product['retail_quantity'] = new_retail_qty
                product['retail_price'] = new_retail_price
                product['date'] = new_date
                save_data("store_products", self.products)
                show_success("Product updated successfully!", self.current_language)
                dialog.destroy()
                self.refresh_store()
            except ValueError:
                show_error("Invalid quantity values", self.current_language)
        
        save_btn = create_styled_button(form_frame, text="Save", style='primary', command=save_changes)
        save_btn.pack(pady=10)

    def delete_store_product(self, product_id):
        """Delete a store product"""
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
                save_data("store_products", self.products)
                self.refresh_store()
                show_success(self.LANGUAGES[self.current_language].get("product_deleted_success", "Product deleted successfully!"), self.current_language)
            except ValueError:
                show_error(self.LANGUAGES[self.current_language].get("product_not_found", "Product not found."), self.current_language)

    def goto_previous_page(self):
        """Go to the previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.manage_store()

    def goto_next_page(self):
        """Go to the next page"""
        # فلترة منتجات المحل فقط
        store_products = [p for p in self.products if p.get('location', '').strip().lower() in ['المحل', 'shop', 'المحل / shop']]
        
        total_items = len(store_products)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.manage_store()

    def format_date(self, date_str):
        try:
            # جرب عدة تنسيقات
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%d/%m/%Y")
                except Exception:
                    continue
            return date_str
        except Exception:
            return date_str 