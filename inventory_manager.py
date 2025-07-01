import customtkinter as ctk
from tkinter import ttk, messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id, import_from_excel
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label, create_styled_option_menu
)
import tkinter as tk

class InventoryManager:
    def __init__(self, root, current_language, languages, back_callback, store_manager_instance=None):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.inventory = load_data("inventory") or []
        self.selected_items = set()
        self.selected_store = "All Stores"  # المخزن المحدد للفلترة
        self.current_page = 0
        self.items_per_page = 20
        self.add_item_dialog = None
        self.product_menu = None
        self.store_manager_instance = store_manager_instance

    def refresh_inventory(self):
        """Refresh the inventory list from database and update display"""
        try:
            # Load inventory from database first
            self.inventory = load_data("inventory") or []
            print(f"[DEBUG] Loaded inventory count: {len(self.inventory)}")
            print(f"[DEBUG] Loaded inventory: {self.inventory}")
            
            # تحديث القائمة المنسدلة فقط إذا كانت نافذة الإضافة مفتوحة
            if self.add_item_dialog and self.product_menu:
                inventory_names = [item['name'] for item in self.inventory]
                self.product_menu.configure(values=inventory_names)
            
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
            text=self.LANGUAGES[self.current_language].get("manage_inventory", "ادارة المخزون"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_from_products
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_items = len(self.inventory)
        low_stock = len([
            i for i in self.inventory
            if i.get('quantity', 0) <= 2 or i.get('retail_quantity', 0) <= 6
        ])
        out_of_stock = len([
            i for i in self.inventory
            if i.get('quantity', 0) <= 0 and i.get('retail_quantity', 0) <= 0
        ])
        
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
            text=self.get_bilingual("add_item", "", "إضافة عنصر"),
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
        
        # زر استيراد البيانات من الإكسل
        import_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("import_excel", "Import from Excel", "استيراد من إكسل"),
            style='outline',
            command=self.import_from_excel
        )
        import_button.pack(side='right', padx=20, pady=20)
        
        # Inventory table (scrollable)
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        table_canvas_frame = tk.Frame(table_frame, bg=COLORS['surface'])
        table_canvas_frame.pack(fill='both', expand=True)
        canvas = tk.Canvas(table_canvas_frame, highlightthickness=0, bg=COLORS['surface'])
        canvas.pack(side='top', fill='both', expand=True)
        h_scroll = tk.Scrollbar(table_frame, orient='horizontal', command=canvas.xview)
        h_scroll.pack(side='bottom', fill='x')
        v_scroll = tk.Scrollbar(table_canvas_frame, orient='vertical', command=canvas.yview)
        v_scroll.pack(side='right', fill='y')
        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set, bg=COLORS['surface'])
        table_inner = ctk.CTkFrame(canvas, fg_color=COLORS['surface'])
        table_window = canvas.create_window((0, 0), window=table_inner, anchor='nw')
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
        table_inner.bind('<Configure>', on_configure)
        def on_canvas_configure(event):
            pass
        canvas.bind('<Configure>', on_canvas_configure)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_table = table_inner
        
        # Table headers
        headers = [
            ("item_name", self.get_bilingual("item_name", "Item Name", "اسم المنتج"), 180, 'w'),
            ("carton_count", self.get_bilingual("carton_count", "Carton Count", "عدد الكراتين"), 110, 'nsew'),
            ("carton_fraction", self.get_bilingual("carton_fraction", "Carton Fraction", "كسر الكرتونة"), 120, 'nsew'),
            ("units_per_carton", self.get_bilingual("units_per_carton", "Units/Carton", "عدد في الكرتونة"), 110, 'nsew'),
            ("unit_type", self.get_bilingual("unit_type", "Unit Type", "نوع الوحدة"), 100, 'nsew'),
            ("total_wholesale", self.get_bilingual("total_wholesale", "Total Wholesale", "إجمالي الجملة"), 120, 'nsew'),
            ("retail_quantity", self.get_bilingual("retail_quantity", "Retail Qty", "عدد القطاعي"), 110, 'nsew'),
            ("extra_retail_quantity", self.get_bilingual("extra_retail_quantity", "Extra Retail Qty", "العدد الزائد القطاعي"), 120, 'nsew'),
            ("total_quantity", self.get_bilingual("total_quantity", "Total Qty", "الإجمالي الكلي"), 110, 'nsew'),
            ("location", self.get_bilingual("location", "Location", "المخزن"), 120, 'nsew'),
            ("actions", self.get_bilingual("actions", "Actions", "إجراءات"), 140, 'nsew')
        ]
        for i, (key, label, width, align) in enumerate(headers):
            header = create_styled_label(scrollable_table, text=label, style='subheading')
            header.grid(row=0, column=i, padx=5, pady=10, sticky=align)
            scrollable_table.grid_columnconfigure(i, minsize=width)
        
        # Inventory list
        # فلترة المنتجات حسب المخزن المحدد
        filtered_inventory = self.inventory
        if self.selected_store != "All Stores":
            filtered_inventory = [item for item in self.inventory if item.get('location', '') == self.selected_store]
        
        # Pagination
        total_items = len(filtered_inventory)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = filtered_inventory[start_idx:end_idx]
        
        for i, item in enumerate(page_items, 1):
            row_bg = COLORS['surface'] if i % 2 == 0 else COLORS['background']
            # اسم المنتج
            name_label = create_styled_label(
                scrollable_table,
                text=item.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=5, pady=10, sticky='w')
            name_label.configure(bg_color=row_bg)
            # عدد الكراتين
            carton_count_val = item.get('carton_count', 0)
            try:
                carton_count_val = int(float(carton_count_val))
            except Exception:
                carton_count_val = 0
            carton_count_label = create_styled_label(
                scrollable_table,
                text=str(carton_count_val),
                style='body'
            )
            carton_count_label.grid(row=i, column=1, padx=5, pady=10, sticky='nsew')
            carton_count_label.configure(bg_color=row_bg)
            # كسر الكرتونة
            carton_fraction_label = create_styled_label(
                scrollable_table,
                text=str(item.get('carton_fraction', 0)),
                style='body'
            )
            carton_fraction_label.grid(row=i, column=2, padx=5, pady=10, sticky='nsew')
            carton_fraction_label.configure(bg_color=row_bg)
            # عدد في الكرتونة
            units_per_carton_val = item.get('units_per_carton', 0)
            try:
                units_per_carton_val = int(float(units_per_carton_val))
            except Exception:
                units_per_carton_val = 0
            units_per_carton_label = create_styled_label(
                scrollable_table,
                text=str(units_per_carton_val),
                style='body'
            )
            units_per_carton_label.grid(row=i, column=3, padx=5, pady=10, sticky='nsew')
            units_per_carton_label.configure(bg_color=row_bg)
            # نوع الوحدة
            unit_type_val = item.get('unit_type') or item.get('type') or ''
            unit_type_label = create_styled_label(
                scrollable_table,
                text=unit_type_val,
                style='body'
            )
            unit_type_label.grid(row=i, column=4, padx=5, pady=10, sticky='nsew')
            unit_type_label.configure(bg_color=row_bg)
            # إجمالي الجملة
            carton_count = float(item.get('carton_count', 0) or 0)
            carton_fraction = float(item.get('carton_fraction', 0) or 0)
            units_per_carton = float(item.get('units_per_carton', 0) or 0)
            total_wholesale = (carton_count + carton_fraction) * units_per_carton
            total_wholesale_label = create_styled_label(
                scrollable_table,
                text=str(int(total_wholesale) if total_wholesale.is_integer() else f"{total_wholesale:.2f}"),
                style='body'
            )
            total_wholesale_label.grid(row=i, column=5, padx=5, pady=10, sticky='nsew')
            total_wholesale_label.configure(bg_color=row_bg)
            # إجمالي القطاعي
            retail_qty = float(item.get('retail_quantity', 0) or 0)
            retail_qty_label = create_styled_label(
                scrollable_table,
                text=str(int(retail_qty) if retail_qty.is_integer() else f"{retail_qty:.2f}"),
                style='body'
            )
            retail_qty_label.grid(row=i, column=6, padx=5, pady=10, sticky='nsew')
            retail_qty_label.configure(bg_color=row_bg)
            # العدد الزائد القطاعي
            extra_retail = float(item.get('extra_retail_quantity', 0) or 0)
            extra_retail_label = create_styled_label(
                scrollable_table,
                text=str(int(extra_retail) if extra_retail.is_integer() else f"{extra_retail:.2f}"),
                style='body'
            )
            extra_retail_label.grid(row=i, column=7, padx=5, pady=10, sticky='nsew')
            extra_retail_label.configure(bg_color=row_bg)
            # الإجمالي الكلي
            total_retail = retail_qty + extra_retail
            total_qty = total_wholesale + total_retail
            total_qty_label = create_styled_label(
                scrollable_table,
                text=str(int(total_qty) if total_qty.is_integer() else f"{total_qty:.2f}"),
                style='body'
            )
            total_qty_label.grid(row=i, column=8, padx=5, pady=10, sticky='nsew')
            total_qty_label.configure(bg_color=row_bg)
            # الموقع
            location_label = create_styled_label(
                scrollable_table,
                text=item.get('location', ''),
                style='body'
            )
            location_label.grid(row=i, column=9, padx=5, pady=10, sticky='nsew')
            location_label.configure(bg_color=row_bg)
            # الإجراءات
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=10, padx=5, pady=10, sticky='nsew')
            actions_frame.configure(fg_color=row_bg)
            edit_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("edit", "Edit", "تعديل"),
                style='outline',
                width=60,
                command=lambda i=item: self.edit_item(i)
            )
            edit_button.pack(side='left', padx=2)
            delete_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("delete", "Delete", "حذف"),
                style='outline',
                width=60,
                command=lambda i=item: self.delete_item(i)
            )
            delete_button.pack(side='left', padx=2)
        
        # أزرار التنقل بين الصفحات
        nav_frame = create_styled_frame(main_frame, style='card')
        nav_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        prev_btn = create_styled_button(
            nav_frame,
            text=self.get_bilingual("previous", "Previous", "السابق"),
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
            text=self.get_bilingual("next", "Next", "التالي"),
            style='outline',
            command=self.goto_next_page
        )
        next_btn.pack(side='left', padx=10, pady=10)

    def add_item(self):
        """Add a new inventory item (اختيار من المنتجات المعرفة فقط)"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("add_item", "Add Item", "إضافة عنصر"))
        dialog.geometry("400x600")
        dialog.grab_set()  # تجعل النافذة modal
        dialog.attributes('-topmost', True)  # تجعل النافذة فوق كل النوافذ
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True)
        # نافذة اختيار المنتج الاحترافية
        def open_product_selector():
            selector = ctk.CTkToplevel(self.root)
            selector.title(self.get_bilingual("select_product", "Select Product", "اختر منتج"))
            selector.geometry("600x500")
            selector.grab_set()
            search_var = ctk.StringVar()
            search_entry = create_styled_entry(selector, placeholder_text=self.get_bilingual("search", "Search...", "بحث..."), textvariable=search_var)
            search_entry.pack(fill='x', padx=20, pady=(20, 10))
            table_frame = create_styled_frame(selector, style='card')
            table_frame.pack(fill='both', expand=True, padx=20, pady=10)
            headers = [
                ("name", self.get_bilingual("product_name", "Product Name", "اسم المنتج")),
                ("barcode", self.get_bilingual("barcode", "Barcode", "باركود")),
                ("weight", self.get_bilingual("product_weight", "Weight", "وزن المنتج")),
                ("date_added", self.get_bilingual("date_added", "Date Added", "تاريخ الإضافة"))
            ]
            for i, (_, label) in enumerate(headers):
                header = create_styled_label(table_frame, text=label, style='subheading')
                header.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
                table_frame.grid_columnconfigure(i, weight=1)
            from data_handler import load_data
            all_products = load_data("products") or []
            for p in all_products:
                if not p.get('date_added'):
                    p['date_added'] = p.get('date', '')
            all_products.sort(key=lambda p: p.get('date_added', ''), reverse=True)
            filtered_products = all_products.copy()
            product_rows = []
            selected_row_idx = [None]  # mutable for closure
            # دعم الصفحات
            items_per_page = 10
            current_page = [0]
            def update_table():
                for row in product_rows:
                    for cell in row:
                        cell.destroy()
                product_rows.clear()
                # حساب الصفحات
                total_items = len(filtered_products)
                total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
                start_idx = current_page[0] * items_per_page
                end_idx = start_idx + items_per_page
                page_products = filtered_products[start_idx:end_idx]
                for idx, product in enumerate(page_products, 1):
                    row = []
                    for col, key in enumerate(["name", "barcode", "weight", "date_added"]):
                        val = product.get(key, "-")
                        cell = create_styled_label(table_frame, text=val, style='body')
                        cell.grid(row=idx, column=col, padx=5, pady=3, sticky='nsew')
                        row.append(cell)
                    def on_select(event, p=product, row_idx=idx-1):
                        # تظليل الصف
                        for r, r_cells in enumerate(product_rows):
                            for c in r_cells:
                                c.configure(bg_color=COLORS['surface'] if r % 2 == 0 else COLORS['background'])
                        for c in row:
                            c.configure(bg_color="#2257a5")
                        selected_row_idx[0] = row_idx
                    row[0].bind('<Button-1>', on_select)
                    row[0].bind('<Double-Button-1>', lambda e, p=product: (fill_product_fields(p), selector.destroy()))
                    product_rows.append(row)
                # أزرار الصفحات
                if hasattr(update_table, 'nav_frame'):
                    update_table.nav_frame.destroy()
                nav_frame = create_styled_frame(selector, style='card')
                nav_frame.pack(fill='x', padx=20, pady=(0, 10))
                update_table.nav_frame = nav_frame
                prev_btn = create_styled_button(nav_frame, text=self.get_bilingual("previous", "Previous", "السابق"), style='outline', command=lambda: go_page(-1))
                prev_btn.pack(side='left', padx=10, pady=10)
                page_label = create_styled_label(nav_frame, text=f"{current_page[0]+1} / {total_pages}", style='subheading')
                page_label.pack(side='left', padx=10, pady=10)
                next_btn = create_styled_button(nav_frame, text=self.get_bilingual("next", "Next", "التالي"), style='outline', command=lambda: go_page(1))
                next_btn.pack(side='left', padx=10, pady=10)
                prev_btn.configure(state='normal' if current_page[0] > 0 else 'disabled')
                next_btn.configure(state='normal' if current_page[0] < total_pages-1 else 'disabled')
            def go_page(delta):
                total_items = len(filtered_products)
                total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
                current_page[0] = max(0, min(current_page[0]+delta, total_pages-1))
                selected_row_idx[0] = None
                update_table()
            def on_search(*args):
                q = search_var.get().strip().lower()
                if not q:
                    filtered_products[:] = all_products
                else:
                    filtered_products[:] = [p for p in all_products if q in str(p.get('name', '')).lower() or q in str(p.get('barcode', '')).lower()]
                current_page[0] = 0
                selected_row_idx[0] = None
                update_table()
            search_var.trace_add('write', on_search)
            update_table()
            def on_choose():
                idx = selected_row_idx[0]
                start_idx = current_page[0] * items_per_page
                if idx is not None and 0 <= idx < items_per_page:
                    product = filtered_products[start_idx + idx]
                    fill_product_fields(product)
                selector.destroy()
            choose_btn = create_styled_button(selector, text=self.get_bilingual("choose", "Choose", "اختيار"), style='primary', command=on_choose)
            choose_btn.pack(pady=10)
        # دالة تعبئة الحقول
        selected_product_name = ['']  # متغير قابل للتغيير داخل الدوال الداخلية

        def fill_product_fields(product):
            selected_product_name[0] = product.get('name', '')
            type_menu.set(product.get('type', type_options[0]))
            flavor_entry.delete(0, 'end')
            flavor_entry.insert(0, product.get('flavor', '-'))
            weight_entry.delete(0, 'end')
            weight_entry.insert(0, product.get('weight', '-'))
            barcode_entry.delete(0, 'end')
            barcode_entry.insert(0, product.get('barcode', '-'))
            wholesale_supplier_price_entry.delete(0, 'end')
            wholesale_supplier_price_entry.insert(0, str(product.get('wholesale_supplier_price', '')))
            wholesale_sale_price_entry.delete(0, 'end')
            wholesale_sale_price_entry.insert(0, str(product.get('wholesale_sale_price', '')))
            retail_sale_price_entry.delete(0, 'end')
            retail_sale_price_entry.insert(0, str(product.get('retail_sale_price', '')))
            carton_count_entry.delete(0, 'end')
            carton_count_entry.insert(0, str(product.get('carton_count', '')))
            units_per_carton_entry.delete(0, 'end')
            units_per_carton_entry.insert(0, str(product.get('units_per_carton', '')))
            retail_quantity_entry.delete(0, 'end')
            retail_quantity_entry.insert(0, str(product.get('retail_quantity', 0)))
            current_fraction = str(product.get('carton_fraction', '0'))
            for val, label in fraction_options:
                if val == current_fraction:
                    fraction_menu.set(label)
                    break
            else:
                fraction_menu.set(fraction_options[0][1])

        # زر فتح نافذة اختيار المنتج
        product_label = create_styled_label(form_frame, text=self.get_bilingual("product_name", "Product Name", "اسم المنتج"), style='subheading')
        product_label.pack(pady=(20, 5))
        select_btn = create_styled_button(form_frame, text=self.get_bilingual("select_product", "Select Product", "اختر منتج"), style='outline', command=open_product_selector)
        select_btn.pack(fill='x', padx=20, pady=(0, 15))
        # نوع المنتج (قائمة منسدلة)
        type_label = create_styled_label(form_frame, text=self.get_bilingual("product_type", "Type", "نوع المنتج"), style='subheading')
        type_label.pack(pady=(0, 5))
        type_options = [self.get_bilingual("wholesale", "Wholesale", "جملة"), self.get_bilingual("retail", "Retail", "قطاعى")]
        type_menu = create_styled_option_menu(form_frame, values=type_options)
        type_menu.set(type_options[0])
        type_menu.pack(fill='x', padx=20, pady=(0, 10))
        flavor_label = create_styled_label(form_frame, text=self.get_bilingual("product_flavor", "Flavor", "نكهة المنتج"), style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_entry = create_styled_entry(form_frame)
        flavor_entry.insert(0, '-')
        flavor_entry.pack(fill='x', padx=20, pady=(0, 10))
        weight_label = create_styled_label(form_frame, text=self.get_bilingual("product_weight", "Weight", "وزن المنتج"), style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_entry = create_styled_entry(form_frame)
        weight_entry.insert(0, '-')
        weight_entry.pack(fill='x', padx=20, pady=(0, 10))
        barcode_label = create_styled_label(form_frame, text=self.get_bilingual("barcode", "Barcode", "باركود"), style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_entry = create_styled_entry(form_frame)
        barcode_entry.insert(0, '-')
        barcode_entry.pack(fill='x', padx=20, pady=(0, 10))
        # عدد الكراتين
        carton_count_label = create_styled_label(form_frame, text=self.get_bilingual("carton_count", "Carton Count", "عدد الكراتين"), style='subheading')
        carton_count_label.pack(pady=(0, 5))
        carton_count_entry = create_styled_entry(form_frame)
        carton_count_entry.pack(fill='x', padx=20, pady=(0, 10))
        # كسر الكرتونة
        fraction_label = create_styled_label(form_frame, text=self.get_bilingual("carton_fraction", "Carton Fraction", "كسر الكرتونة"), style='subheading')
        fraction_label.pack(pady=(0, 5))
        fraction_options = [
            ("0", self.get_bilingual("no_fraction", "No Fraction", "لا شيء")),
            ("0.25", self.get_bilingual("quarter_carton", "Quarter Carton", "ربع كرتونة")),
            ("0.5", self.get_bilingual("half_carton", "Half Carton", "نصف كرتونة")),
            ("0.75", self.get_bilingual("three_quarters_carton", "Three Quarters Carton", "ثلاثة أرباع كرتونة")),
            ("0.33", self.get_bilingual("third_carton", "Third Carton", "ثلث كرتونة")),
            ("0.66", self.get_bilingual("two_thirds_carton", "Two Thirds Carton", "ثلثي كرتونة"))
        ]
        fraction_menu = create_styled_option_menu(form_frame, values=[label for val, label in fraction_options])
        current_fraction = '0'
        for val, label in fraction_options:
            if val == current_fraction:
                fraction_menu.set(label)
                break
        else:
            fraction_menu.set(fraction_options[0][1])
        fraction_menu.pack(fill='x', padx=20, pady=(0, 10))
        # عدد في الكرتونة
        units_per_carton_label = create_styled_label(form_frame, text=self.get_bilingual("units_per_carton", "Units/Carton", "عدد في الكرتونة"), style='subheading')
        units_per_carton_label.pack(pady=(0, 5))
        units_per_carton_entry = create_styled_entry(form_frame)
        units_per_carton_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # عدد القطاعي
        retail_quantity_label = create_styled_label(form_frame, text=self.get_bilingual("retail_quantity", "Retail Qty", "عدد القطاعي"), style='subheading')
        retail_quantity_label.pack(pady=(0, 5))
        retail_quantity_entry = create_styled_entry(form_frame)
        retail_quantity_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # عدد زائد قطاعى (اختياري)
        extra_retail_label = create_styled_label(form_frame, text=self.get_bilingual("extra_retail_quantity", "Extra Retail Qty (Optional)", "عدد زائد قطاعى (اختياري)"), style='subheading')
        extra_retail_label.pack(pady=(0, 5))
        extra_retail_entry = create_styled_entry(form_frame)
        extra_retail_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # أسعار
        wholesale_supplier_price_label = create_styled_label(form_frame, text="Wholesale Supplier Price / سعر الجملة من التاجر", style='subheading')
        wholesale_supplier_price_label.pack(pady=(0, 5))
        wholesale_supplier_price_entry = create_styled_entry(form_frame)
        wholesale_supplier_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        wholesale_sale_price_label = create_styled_label(form_frame, text="Wholesale Sale Price / سعر الجملة للبيع", style='subheading')
        wholesale_sale_price_label.pack(pady=(0, 5))
        wholesale_sale_price_entry = create_styled_entry(form_frame)
        wholesale_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        retail_sale_price_label = create_styled_label(form_frame, text="Retail Sale Price / سعر البيع قطاعى", style='subheading')
        retail_sale_price_label.pack(pady=(0, 5))
        retail_sale_price_entry = create_styled_entry(form_frame)
        retail_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))
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
        def get_fraction_value(selected_label):
            for val, label in fraction_options:
                if label == selected_label:
                    return float(val)
            return 0.0
        def save_with_validation():
            try:
                fraction_val = get_fraction_value(fraction_menu.get())
                extra_retail_val = float(extra_retail_entry.get() or 0)
                retail_quantity_val = float(retail_quantity_entry.get() or 0)
            except ValueError:
                show_error(self.get_bilingual("invalid_item", "Please enter a valid value", "يرجى إدخال قيمة صحيحة"), self.current_language)
                return
            self.save_item(
                dialog,
                selected_product_name[0],
                type_menu.get(),
                0,  # Default quantity since quantity field was removed
                location_menu.get(),
                flavor_entry.get(),
                weight_entry.get(),
                barcode_entry.get(),
                int(carton_count_entry.get() or 0),
                fraction_val,
                float(units_per_carton_entry.get() or 0),
                wholesale_supplier_price_entry.get(),
                wholesale_sale_price_entry.get(),
                retail_sale_price_entry.get(),
                extra_retail_val,
                retail_quantity_val
            )
        save_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=save_with_validation
        )
        save_button.pack(pady=20)

    def edit_item(self, item):
        """Edit an existing inventory item"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("edit_item", "Edit Item", "تعديل العنصر"))
        dialog.geometry("400x600")
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True)
        # تعريف store_names هنا
        import json, os
        stores_file = os.path.join("excel_data", "stores.json")
        store_names = ["المحل / Shop"]
        if os.path.exists(stores_file):
            with open(stores_file, 'r', encoding='utf-8') as f:
                stores = json.load(f)
                store_names += [store['name'] for store in stores]
        name_label = create_styled_label(form_frame, text=self.get_bilingual("item_name", "Item Name", "اسم العنصر"), style='subheading')
        name_label.pack(pady=(20, 5))
        name_entry = create_styled_entry(form_frame)
        name_entry.insert(0, item.get('name', ''))
        name_entry.pack(fill='x', padx=20, pady=(0, 15))
        # نوع المنتج (قائمة منسدلة)
        type_label = create_styled_label(form_frame, text=self.get_bilingual("product_type", "Type", "نوع المنتج"), style='subheading')
        type_label.pack(pady=(0, 5))
        type_options = [self.get_bilingual("wholesale", "Wholesale", "جملة"), self.get_bilingual("retail", "Retail", "قطاعى")]
        type_menu = create_styled_option_menu(form_frame, values=type_options)
        if item.get('type') in type_options:
            type_menu.set(item.get('type'))
        elif item.get('unit_type') in type_options:
            type_menu.set(item.get('unit_type'))
        else:
            type_menu.set(type_options[0])
        type_menu.pack(fill='x', padx=20, pady=(0, 10))
        flavor_label = create_styled_label(form_frame, text=self.get_bilingual("product_flavor", "Flavor", "نكهة المنتج"), style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_entry = create_styled_entry(form_frame)
        flavor_entry.insert(0, item.get('flavor', '-'))
        flavor_entry.pack(fill='x', padx=20, pady=(0, 10))
        weight_label = create_styled_label(form_frame, text=self.get_bilingual("product_weight", "Weight", "وزن المنتج"), style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_entry = create_styled_entry(form_frame)
        weight_entry.insert(0, item.get('weight', '-'))
        weight_entry.pack(fill='x', padx=20, pady=(0, 10))
        barcode_label = create_styled_label(form_frame, text=self.get_bilingual("barcode", "Barcode", "باركود"), style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_entry = create_styled_entry(form_frame)
        barcode_entry.insert(0, item.get('barcode', '-'))
        barcode_entry.pack(fill='x', padx=20, pady=(0, 10))
        location_label = create_styled_label(form_frame, text=self.get_bilingual("location", "Location", "الموقع"), style='subheading')
        location_label.pack(pady=(0, 5))
        location_menu = create_styled_option_menu(form_frame, values=store_names)
        location_menu.set(item.get('location', store_names[0]))
        location_menu.pack(fill='x', padx=20, pady=(0, 15))
        # عدد الكراتين
        carton_count_label = create_styled_label(form_frame, text=self.get_bilingual("carton_count", "Carton Count", "عدد الكراتين"), style='subheading')
        carton_count_label.pack(pady=(0, 5))
        carton_count_entry = create_styled_entry(form_frame)
        carton_count_entry.insert(0, str(item.get('carton_count', 0)))
        carton_count_entry.pack(fill='x', padx=20, pady=(0, 10))
        # كسر الكرتونة
        fraction_label = create_styled_label(form_frame, text=self.get_bilingual("carton_fraction", "Carton Fraction", "كسر الكرتونة"), style='subheading')
        fraction_label.pack(pady=(0, 5))
        fraction_options = [
            ("0", self.get_bilingual("no_fraction", "No Fraction", "لا شيء")),
            ("0.25", self.get_bilingual("quarter_carton", "Quarter Carton", "ربع كرتونة")),
            ("0.5", self.get_bilingual("half_carton", "Half Carton", "نصف كرتونة")),
            ("0.75", self.get_bilingual("three_quarters_carton", "Three Quarters Carton", "ثلاثة أرباع كرتونة")),
            ("0.33", self.get_bilingual("third_carton", "Third Carton", "ثلث كرتونة")),
            ("0.66", self.get_bilingual("two_thirds_carton", "Two Thirds Carton", "ثلثي كرتونة"))
        ]
        fraction_menu = create_styled_option_menu(form_frame, values=[label for val, label in fraction_options])
        current_fraction = '0'
        for val, label in fraction_options:
            if val == current_fraction:
                fraction_menu.set(label)
                break
        else:
            fraction_menu.set(fraction_options[0][1])
        fraction_menu.pack(fill='x', padx=20, pady=(0, 10))
        # عدد في الكرتونة
        units_per_carton_label = create_styled_label(form_frame, text=self.get_bilingual("units_per_carton", "Units/Carton", "عدد في الكرتونة"), style='subheading')
        units_per_carton_label.pack(pady=(0, 5))
        units_per_carton_entry = create_styled_entry(form_frame)
        units_per_carton_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # عدد القطاعي
        retail_quantity_label = create_styled_label(form_frame, text=self.get_bilingual("retail_quantity", "Retail Qty", "عدد القطاعي"), style='subheading')
        retail_quantity_label.pack(pady=(0, 5))
        retail_quantity_entry = create_styled_entry(form_frame)
        retail_quantity_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # عدد زائد قطاعى (اختياري)
        extra_retail_label = create_styled_label(form_frame, text=self.get_bilingual("extra_retail_quantity", "Extra Retail Qty (Optional)", "عدد زائد قطاعى (اختياري)"), style='subheading')
        extra_retail_label.pack(pady=(0, 5))
        extra_retail_entry = create_styled_entry(form_frame)
        extra_retail_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # أسعار
        wholesale_supplier_price_label = create_styled_label(form_frame, text="Wholesale Supplier Price / سعر الجملة من التاجر", style='subheading')
        wholesale_supplier_price_label.pack(pady=(0, 5))
        wholesale_supplier_price_entry = create_styled_entry(form_frame)
        wholesale_supplier_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        wholesale_sale_price_label = create_styled_label(form_frame, text="Wholesale Sale Price / سعر الجملة للبيع", style='subheading')
        wholesale_sale_price_label.pack(pady=(0, 5))
        wholesale_sale_price_entry = create_styled_entry(form_frame)
        wholesale_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        retail_sale_price_label = create_styled_label(form_frame, text="Retail Sale Price / سعر البيع قطاعى", style='subheading')
        retail_sale_price_label.pack(pady=(0, 5))
        retail_sale_price_entry = create_styled_entry(form_frame)
        retail_sale_price_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # في نافذة التعديل أيضاً
        def get_fraction_value(selected_label):
            for val, label in fraction_options:
                if label == selected_label:
                    return float(val)
            return 0.0
        def update_with_validation():
            try:
                fraction_val = get_fraction_value(fraction_menu.get())
                extra_retail_val = float(extra_retail_entry.get() or 0)
                retail_quantity_val = float(retail_quantity_entry.get() or 0)
            except ValueError:
                show_error(self.get_bilingual("invalid_item", "Please enter valid numbers", "يرجى إدخال أرقام صحيحة"), self.current_language)
                return
            self.update_item(
                dialog,
                item,
                name_entry.get(),
                0,  # quantity
                location_menu.get(),
                type_menu.get(),
                flavor_entry.get(),
                weight_entry.get(),
                barcode_entry.get(),
                int(carton_count_entry.get() or 0),
                fraction_val,
                float(units_per_carton_entry.get() or 0),
                wholesale_supplier_price_entry.get(),
                wholesale_sale_price_entry.get(),
                retail_sale_price_entry.get(),
                extra_retail_val,
                retail_quantity_val
            )
        save_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("save", "Save", "حفظ"),
            style='primary',
            command=update_with_validation
        )
        save_button.pack(pady=20)
        cancel_button = create_styled_button(
            form_frame,
            text=self.get_bilingual("cancel", "Cancel", "إلغاء"),
            style='outline',
            command=dialog.destroy
        )
        cancel_button.pack(pady=20)

    def save_item(self, dialog, name, type_value, quantity, location, flavor, weight, barcode, carton_count, fraction_val, units_per_carton, wholesale_supplier_price, wholesale_sale_price, retail_sale_price, extra_retail_quantity, retail_quantity):
        """Save a new inventory item"""
        if not name or not type_value:
            show_error(self.get_bilingual("invalid_item", "Please fill all fields correctly", "يرجى ملء جميع الحقون الصحيحة"), self.current_language)
            return
        # التحقق من وجود عنصر بنفس الباركود
        if barcode and barcode != '-':
            existing_item = next((item for item in self.inventory if item.get('barcode') == barcode), None)
            if existing_item:
                # إنشاء نافذة اختيار
                choice_dialog = ctk.CTkToplevel(dialog)
                choice_dialog.title(self.get_bilingual("item_exists", "Item Exists", "العنصر موجود"))
                choice_dialog.geometry("400x300")
                choice_dialog.grab_set()
                choice_dialog.attributes('-topmost', True)
                # إطار النافذة
                choice_frame = create_styled_frame(choice_dialog, style='card')
                choice_frame.pack(fill='both', expand=True, padx=20, pady=20)
                # رسالة التحذير
                warning_label = create_styled_label(
                    choice_frame,
                    text=self.get_bilingual("item_exists_message", 
                                          f"Item with barcode '{barcode}' already exists.\nName: {existing_item.get('name', 'N/A')}\nCurrent quantities - Wholesale: {existing_item.get('quantity', 0)}, Retail: {existing_item.get('retail_quantity', 0)}",
                                          f"العنصر بالباركود '{barcode}' موجود مسبقاً.\nالاسم: {existing_item.get('name', 'غير محدد')}\nالكميات الحالية - الجملة: {existing_item.get('quantity', 0)}, القطاعي: {existing_item.get('retail_quantity', 0)}"),
                    style='subheading'
                )
                warning_label.pack(pady=20)
                # أزرار الاختيار
                buttons_frame = create_styled_frame(choice_frame, style='card')
                buttons_frame.pack(pady=20)
                def merge_quantities():
                    """دمج الكميات مع العنصر الموجود"""
                    existing_item['quantity'] = existing_item.get('quantity', 0) + quantity
                    existing_item['retail_quantity'] = existing_item.get('retail_quantity', 0) + retail_quantity
                    # تحديث البيانات الأخرى إذا كانت مختلفة
                    if existing_item.get('name') != name:
                        existing_item['name'] = name
                    if existing_item.get('type') != type_value:
                        existing_item['type'] = type_value
                        existing_item['unit_type'] = type_value
                        existing_item['category'] = type_value
                    if existing_item.get('flavor') != flavor:
                        existing_item['flavor'] = flavor
                    if existing_item.get('weight') != weight:
                        existing_item['weight'] = weight
                    if existing_item.get('location') != location:
                        existing_item['location'] = location
                    existing_item['carton_count'] = carton_count
                    existing_item['carton_fraction'] = fraction_val
                    existing_item['units_per_carton'] = units_per_carton
                    existing_item['wholesale_supplier_price'] = wholesale_supplier_price
                    existing_item['wholesale_sale_price'] = wholesale_sale_price
                    existing_item['retail_sale_price'] = retail_sale_price
                    existing_item['extra_retail_quantity'] = extra_retail_quantity
                    existing_item['retail_quantity'] = retail_quantity
                    save_data("inventory", self.inventory)
                    choice_dialog.destroy()
                    dialog.destroy()
                    self.manage_inventory()
                    show_success(self.get_bilingual("quantities_merged", "Quantities merged successfully", "تم دمج الكميات بنجاح"), self.current_language)
                    # تحديث شاشة المحل إذا كانت موجودة
                    if hasattr(self, 'store_manager_instance') and self.store_manager_instance:
                        self.store_manager_instance.refresh_store()
                def add_as_new():
                    """إضافة كعنصر جديد"""
                    new_item = {
                        'id': get_next_id('inventory'),
                        'name': name,
                        'type': type_value,
                        'unit_type': type_value,
                        'category': type_value,
                        'flavor': flavor,
                        'weight': weight,
                        'barcode': barcode,
                        'quantity': quantity,
                        'location': location,
                        'carton_count': carton_count,
                        'carton_fraction': fraction_val,
                        'units_per_carton': units_per_carton,
                        'wholesale_supplier_price': wholesale_supplier_price,
                        'wholesale_sale_price': wholesale_sale_price,
                        'retail_sale_price': retail_sale_price,
                        'extra_retail_quantity': extra_retail_quantity,
                        'retail_quantity': retail_quantity
                    }
                    self.inventory.append(new_item)
                    save_data("inventory", self.inventory)
                    choice_dialog.destroy()
                    dialog.destroy()
                    self.manage_inventory()
                    show_success(self.get_bilingual("item_added", "Item added successfully", "تمت إضافة العنصر بنجاح"), self.current_language)
                    # تحديث شاشة المحل إذا كانت موجودة
                    if hasattr(self, 'store_manager_instance') and self.store_manager_instance:
                        self.store_manager_instance.refresh_store()
                def cancel_operation():
                    """إلغاء العملية"""
                    choice_dialog.destroy()
                # زر دمج الكميات
                merge_button = create_styled_button(
                    buttons_frame,
                    text=self.get_bilingual("merge_quantities", "Merge Quantities", "دمج الكميات"),
                    style='primary',
                    command=merge_quantities
                )
                merge_button.pack(side='left', padx=10, pady=10)
                # زر إضافة كعنصر جديد
                add_new_button = create_styled_button(
                    buttons_frame,
                    text=self.get_bilingual("add_as_new", "Add as New", "إضافة كعنصر جديد"),
                    style='outline',
                    command=add_as_new
                )
                add_new_button.pack(side='left', padx=10, pady=10)
                # زر الإلغاء
                cancel_button = create_styled_button(
                    buttons_frame,
                    text=self.get_bilingual("cancel", "Cancel", "إلغاء"),
                    style='error',
                    command=cancel_operation
                )
                cancel_button.pack(side='left', padx=10, pady=10)
                return  # إيقاف تنفيذ الدالة الأصلية
        # إذا لم يكن هناك عنصر موجود، أضف العنصر الجديد
        new_item = {
            'id': get_next_id('inventory'),
            'name': name,
            'type': type_value,
            'unit_type': type_value,
            'category': type_value,  # تساوي بين type و category
            'flavor': flavor,
            'weight': weight,
            'barcode': barcode,
            'quantity': quantity,
            'location': location,
            'carton_count': carton_count,
            'carton_fraction': fraction_val,
            'units_per_carton': units_per_carton,
            'wholesale_supplier_price': wholesale_supplier_price,
            'wholesale_sale_price': wholesale_sale_price,
            'retail_sale_price': retail_sale_price,
            'extra_retail_quantity': extra_retail_quantity,
            'retail_quantity': retail_quantity
        }
        self.inventory.append(new_item)
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.get_bilingual("item_added", "Item added successfully", "تمت إضافة العنصر بنجاح"), self.current_language)
        # تحديث شاشة المحل إذا كانت موجودة
        if hasattr(self, 'store_manager_instance') and self.store_manager_instance:
            self.store_manager_instance.refresh_store()

    def update_item(self, dialog, item, name, quantity, location, type_value, flavor, weight, barcode, carton_count, fraction_val, units_per_carton, wholesale_supplier_price, wholesale_sale_price, retail_sale_price, extra_retail_quantity, retail_quantity):
        """Update an existing inventory item"""
        if not name or not type_value or quantity < 0:
            show_error(self.get_bilingual("invalid_item", "Please fill all fields correctly", "يرجى ملء جميع الحقون الصحيحة"), self.current_language)
            return
        item.update({
            'name': name,
            'quantity': quantity,
            'location': location,
            'type': type_value,
            'unit_type': type_value,
            'category': type_value,  # تساوي بين type و category
            'flavor': flavor,
            'weight': weight,
            'barcode': barcode,
            'carton_count': carton_count,
            'carton_fraction': fraction_val,
            'units_per_carton': units_per_carton,
            'wholesale_supplier_price': wholesale_supplier_price,
            'wholesale_sale_price': wholesale_sale_price,
            'retail_sale_price': retail_sale_price,
            'extra_retail_quantity': extra_retail_quantity,
            'retail_quantity': retail_quantity
        })
        save_data("inventory", self.inventory)
        dialog.destroy()
        self.manage_inventory()
        show_success(self.get_bilingual("item_updated", "Item updated successfully", "تم تحديث العنصر بنجاح"), self.current_language)
        if hasattr(self, 'store_manager_instance') and self.store_manager_instance:
            self.store_manager_instance.refresh_store()

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
        self.manage_inventory()

    def apply_store_filter(self):
        """Apply the selected store filter"""
        selected_store = self.store_filter.get()
        if selected_store == "All Stores":
            self.selected_store = "All Stores"
        else:
            self.selected_store = selected_store
        self.manage_inventory()

    def import_from_excel(self):
        from data_handler import import_from_excel
        if import_from_excel("inventory"):
            # Reload inventory data after import
            self.inventory = load_data("inventory") or []
            self.manage_inventory()
            show_success(self.get_bilingual("import_success", "Data imported successfully", "تم استيراد البيانات بنجاح"), self.current_language)
        else:
            show_error(self.get_bilingual("import_failed", "Failed to import data", "فشل في استيراد البيانات"), self.current_language)

    def refresh_from_products(self):
        products = load_data("products") or []
        updated = False
        for item in self.inventory:
            # ابحث عن منتج مطابق بالاسم أو الباركود
            match = next((p for p in products if (p.get('barcode') and p.get('barcode') == item.get('barcode')) or (p.get('name') and p.get('name') == item.get('name'))), None)
            if match:
                # حدث الحقول الناقصة فقط
                for key in ["barcode", "name", "type", "flavor", "weight"]:
                    if match.get(key) and (not item.get(key) or item.get(key) == "-"):
                        item[key] = match[key]
                        updated = True
                # تحديث category ليكون مساوي لـ type
                if item.get('type') and item.get('type') != item.get('category'):
                    item['category'] = item['type']
                    updated = True
        if updated:
            save_data("inventory", self.inventory)
        self.manage_inventory()

    def goto_previous_page(self):
        """Go to the previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.manage_inventory()

    def goto_next_page(self):
        """Go to the next page"""
        # فلترة المنتجات حسب المخزن المحدد
        filtered_inventory = self.inventory
        if self.selected_store != "All Stores":
            filtered_inventory = [item for item in self.inventory if item.get('location', '') == self.selected_store]
        
        total_items = len(filtered_inventory)
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.manage_inventory()
