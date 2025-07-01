import customtkinter as ctk
from tkinter import messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, get_next_id
from theme import (
    COLORS, create_styled_button, create_styled_entry, create_styled_frame, create_styled_label, create_styled_option_menu
)
from tkcalendar import DateEntry
from datetime import datetime
import tkinter as tk

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
        # إطار خاص للجدول والسكورلات
        table_canvas_frame = tk.Frame(table_frame, bg=COLORS['surface'])
        table_canvas_frame.pack(fill='both', expand=True)
        canvas = tk.Canvas(table_canvas_frame, highlightthickness=0, bg=COLORS['surface'])
        canvas.pack(side='top', fill='both', expand=True)
        # Scrollbars
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
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception:
                pass
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_table = table_inner
        # ترتيب الأعمدة: اسم المنتج، عدد الكراتين، كسر الكرتونة، عدد في الكرتونة، نوع الوحدة، إجمالي الجملة، عدد القطاعي، الإجمالي الكلي، التاريخ، الإجراءات
        headers = [
            ("product_name", self.LANGUAGES[self.current_language].get("product_name", "Product Name / اسم المنتج"), 180, 'w'),
            ("carton_count", self.LANGUAGES[self.current_language].get("carton_count", "Cartons / عدد الكراتين"), 110, 'nsew'),
            ("carton_fraction", self.LANGUAGES[self.current_language].get("carton_fraction", "Carton Fraction / كسر الكرتونة"), 120, 'nsew'),
            ("units_per_carton", self.LANGUAGES[self.current_language].get("units_per_carton", "Units/Carton / عدد في الكرتونة"), 110, 'nsew'),
            ("unit_type", self.LANGUAGES[self.current_language].get("unit_type", "Unit Type / نوع الوحدة"), 100, 'nsew'),
            ("total_wholesale", self.LANGUAGES[self.current_language].get("total_wholesale", "Total Wholesale / إجمالي الجملة"), 120, 'nsew'),
            ("retail_quantity", self.LANGUAGES[self.current_language].get("retail_quantity", "Retail Qty / عدد القطاعي"), 110, 'nsew'),
            ("total_quantity", self.LANGUAGES[self.current_language].get("total_quantity", "Total Qty / الإجمالي الكلي"), 110, 'nsew'),
            ("date", self.LANGUAGES[self.current_language].get("date", "Date / التاريخ"), 110, 'nsew'),
            ("actions", self.LANGUAGES[self.current_language].get("actions", "Actions / الإجراءات"), 140, 'nsew')
        ]
        for i, (key, label, width, align) in enumerate(headers):
            header = create_styled_label(scrollable_table, text=label, style='subheading')
            header.grid(row=0, column=i, padx=5, pady=10, sticky=align)
            scrollable_table.grid_columnconfigure(i, minsize=width)
        for i, product in enumerate(page_products, 1):
            row_bg = COLORS['surface'] if i % 2 == 0 else COLORS['background']
            # اسم المنتج
            name_label = create_styled_label(
                scrollable_table,
                text=product.get('name', ''),
                style='body'
            )
            name_label.grid(row=i, column=0, padx=5, pady=10, sticky='w')
            name_label.configure(bg_color=row_bg)
            # عدد الكراتين
            carton_count_label = create_styled_label(
                scrollable_table,
                text=str(product.get('carton_count', 0)),
                style='body'
            )
            carton_count_label.grid(row=i, column=1, padx=5, pady=10, sticky='nsew')
            carton_count_label.configure(bg_color=row_bg)
            # كسر الكرتونة
            carton_fraction_label = create_styled_label(
                scrollable_table,
                text=str(product.get('carton_fraction', 0)),
                style='body'
            )
            carton_fraction_label.grid(row=i, column=2, padx=5, pady=10, sticky='nsew')
            carton_fraction_label.configure(bg_color=row_bg)
            # عدد في الكرتونة
            units_per_carton_label = create_styled_label(
                scrollable_table,
                text=str(product.get('units_per_carton', 0)),
                style='body'
            )
            units_per_carton_label.grid(row=i, column=3, padx=5, pady=10, sticky='nsew')
            units_per_carton_label.configure(bg_color=row_bg)
            # نوع الوحدة
            unit_type_label = create_styled_label(
                scrollable_table,
                text=product.get('unit_type', ''),
                style='body'
            )
            unit_type_label.grid(row=i, column=4, padx=5, pady=10, sticky='nsew')
            unit_type_label.configure(bg_color=row_bg)
            # إجمالي الجملة
            carton_count = float(product.get('carton_count', 0) or 0)
            carton_fraction = float(product.get('carton_fraction', 0) or 0)
            units_per_carton = float(product.get('units_per_carton', 0) or 0)
            total_wholesale = (carton_count + carton_fraction) * units_per_carton
            total_wholesale_label = create_styled_label(
                scrollable_table,
                text=str(int(total_wholesale) if total_wholesale.is_integer() else f"{total_wholesale:.2f}"),
                style='body'
            )
            total_wholesale_label.grid(row=i, column=5, padx=5, pady=10, sticky='nsew')
            total_wholesale_label.configure(bg_color=row_bg)
            # عدد القطاعي
            retail_qty_label = create_styled_label(
                scrollable_table,
                text=str(product.get('retail_quantity', 0)),
                style='body'
            )
            retail_qty_label.grid(row=i, column=6, padx=5, pady=10, sticky='nsew')
            retail_qty_label.configure(bg_color=row_bg)
            # الإجمالي الكلي
            total_qty = total_wholesale + float(product.get('retail_quantity', 0) or 0)
            total_qty_label = create_styled_label(
                scrollable_table,
                text=str(int(total_qty) if total_qty.is_integer() else f"{total_qty:.2f}"),
                style='body'
            )
            total_qty_label.grid(row=i, column=7, padx=5, pady=10, sticky='nsew')
            total_qty_label.configure(bg_color=row_bg)
            # التاريخ
            date_label = create_styled_label(
                scrollable_table,
                text=self.format_date(product.get('date', '')),
                style='body'
            )
            date_label.grid(row=i, column=8, padx=5, pady=10, sticky='nsew')
            date_label.configure(bg_color=row_bg)
            # الإجراءات
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=9, padx=5, pady=10, sticky='nsew')
            actions_frame.configure(fg_color=row_bg)
            edit_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("edit", "Edit"),
                style='outline',
                width=60,
                command=lambda pid=product.get('id'): self.edit_store_product(pid)
            )
            edit_button.pack(side='left', padx=2)
            delete_button = create_styled_button(
                actions_frame,
                text=self.LANGUAGES[self.current_language].get("delete", "Delete"),
                style='error',
                width=60,
                command=lambda pid=product.get('id'): self.delete_store_product(pid)
            )
            delete_button.pack(side='left', padx=2)

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

    def open_product_dialog(self, product=None):
        is_edit = product is not None
        dialog_title = self.LANGUAGES[self.current_language].get("edit_store_product", "Edit Store Product") if is_edit else self.LANGUAGES[self.current_language].get("add_from_inventory", "Add from Inventory")
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(dialog_title)
        dialog.geometry("400x600")
        dialog.grab_set()
        dialog.attributes('-topmost', True)
        scrollable_form_frame = ctk.CTkScrollableFrame(dialog, orientation='vertical')
        scrollable_form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        form_frame = create_styled_frame(scrollable_form_frame, style='card')
        form_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # --- زر اختيار منتج من المخزون (فقط في وضع الإضافة) ---
        selected_inventory_product = {'product': None}
        if not is_edit:
            def open_inventory_selector():
                selector = ctk.CTkToplevel(self.root)
                selector.title(self.LANGUAGES[self.current_language].get("select_product", "Select Product"))
                selector.geometry("600x500")
                selector.grab_set()
                search_var = ctk.StringVar()
                search_entry = create_styled_entry(selector, placeholder_text=self.LANGUAGES[self.current_language].get("search", "Search..."), textvariable=search_var)
                search_entry.pack(fill='x', padx=20, pady=(20, 10))
                table_frame = create_styled_frame(selector, style='card')
                table_frame.pack(fill='both', expand=True, padx=20, pady=10)
                headers = [
                    ("name", self.LANGUAGES[self.current_language].get("product_name", "Product Name / اسم المنتج")),
                    ("barcode", self.LANGUAGES[self.current_language].get("barcode", "Barcode / باركود")),
                    ("weight", self.LANGUAGES[self.current_language].get("product_weight", "Weight / وزن المنتج")),
                    ("carton_count", self.LANGUAGES[self.current_language].get("carton_count", "Carton Count / عدد الكراتين"))
                ]
                for i, (_, label) in enumerate(headers):
                    header = create_styled_label(table_frame, text=label, style='subheading')
                    header.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
                    table_frame.grid_columnconfigure(i, weight=1)
                inventory_products = [item for item in self.inventory if item.get('name', '').strip()]
                filtered_products = inventory_products.copy()
                product_rows = []
                selected_row_idx = [None]
                items_per_page = 10
                current_page = [0]
                def update_table():
                    for row in product_rows:
                        for cell in row:
                            cell.destroy()
                    product_rows.clear()
                    # إزالة جميع إطارات أزرار الصفحات القديمة
                    for child in selector.winfo_children():
                        if isinstance(child, ctk.CTkFrame) and getattr(child, '_is_nav_frame', False):
                            child.destroy()
                    total_items = len(filtered_products)
                    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
                    start_idx = current_page[0] * items_per_page
                    end_idx = start_idx + items_per_page
                    page_products = filtered_products[start_idx:end_idx]
                    for idx, product in enumerate(page_products, 1):
                        row = []
                        for col, key in enumerate(["name", "barcode", "weight", "carton_count"]):
                            val = product.get(key, "-")
                            cell = create_styled_label(table_frame, text=val, style='body')
                            cell.grid(row=idx, column=col, padx=5, pady=3, sticky='nsew')
                            row.append(cell)
                        def on_select(event, p=product, row_idx=idx-1):
                            for r, r_cells in enumerate(product_rows):
                                for c in r_cells:
                                    c.configure(bg_color=COLORS['surface'] if r % 2 == 0 else COLORS['background'])
                            for c in row:
                                c.configure(bg_color="#2257a5")
                            selected_row_idx[0] = row_idx
                        row[0].bind('<Button-1>', on_select)
                        row[0].bind('<Double-Button-1>', lambda e, p=product: (fill_fields_from_inventory(p), selector.destroy()))
                        product_rows.append(row)
                    # أزرار الصفحات
                    nav_frame = create_styled_frame(selector, style='card')
                    nav_frame._is_nav_frame = True  # علامة مخصصة
                    nav_frame.pack(fill='x', padx=20, pady=(0, 10))
                    prev_btn = create_styled_button(nav_frame, text=self.LANGUAGES[self.current_language].get("previous", "Previous"), style='outline', command=lambda: go_page(-1))
                    prev_btn.pack(side='left', padx=10, pady=10)
                    page_label = create_styled_label(nav_frame, text=f"{current_page[0]+1} / {total_pages}", style='subheading')
                    page_label.pack(side='left', padx=10, pady=10)
                    next_btn = create_styled_button(nav_frame, text=self.LANGUAGES[self.current_language].get("next", "Next"), style='outline', command=lambda: go_page(1))
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
                        filtered_products[:] = inventory_products
                    else:
                        filtered_products[:] = [p for p in inventory_products if q in str(p.get('name', '')).lower() or q in str(p.get('barcode', '')).lower()]
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
                        fill_fields_from_inventory(product)
                    selector.destroy()
                choose_btn = create_styled_button(selector, text=self.LANGUAGES[self.current_language].get("choose", "Choose"), style='primary', command=on_choose)
                choose_btn.pack(pady=10)
            def fill_fields_from_inventory(product):
                selected_inventory_product['product'] = product
                name_value.configure(text=product.get('name', '-'))
                # ضبط نوع المنتج بناءً على أقرب تطابق
                prod_type = str(product.get('type', '')).strip().lower()
                matched = None
                for opt in type_options:
                    if prod_type and prod_type in opt.lower():
                        matched = opt
                        break
                if matched:
                    type_menu.set(matched)
                else:
                    type_menu.set(type_options[0])
                carton_count_entry.delete(0, 'end')
                carton_count_entry.insert(0, str(product.get('carton_count', 0)))
                units_per_carton_entry.delete(0, 'end')
                units_per_carton_entry.insert(0, str(product.get('units_per_carton', 0)))
                unit_type_entry.delete(0, 'end')
                unit_type_entry.insert(0, str(product.get('unit_type', '')))
                wholesale_qty_entry.delete(0, 'end')
                wholesale_qty_entry.insert(0, str(product.get('wholesale_quantity', 0)))
                wholesale_price_entry.delete(0, 'end')
                wholesale_price_entry.insert(0, str(product.get('wholesale_price', 0)))
                retail_qty_entry.delete(0, 'end')
                retail_qty_entry.insert(0, str(product.get('retail_quantity', 0)))
                retail_price_entry.delete(0, 'end')
                retail_price_entry.insert(0, str(product.get('retail_price', 0)))
                flavor_entry.delete(0, 'end')
                flavor_entry.insert(0, str(product.get('flavor', '-')))
                weight_entry.delete(0, 'end')
                weight_entry.insert(0, str(product.get('weight', '-')))
                barcode_value.configure(text=product.get('barcode', '-'))
                # كسر الكرتونة
                current_fraction = str(product.get('carton_fraction', '0'))
                for val, label in fraction_options:
                    if val == current_fraction:
                        fraction_menu.set(label)
                        break
                else:
                    fraction_menu.set(fraction_options[0][1])
            select_btn = create_styled_button(form_frame, text=self.LANGUAGES[self.current_language].get("select_product", "Select Product / اختر منتج"), style='outline', command=open_inventory_selector)
            select_btn.pack(fill='x', padx=20, pady=(0, 10))
        # اسم المنتج (عرض فقط)
        name_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_name", "Product Name / اسم المنتج"), style='subheading')
        name_label.pack(pady=(0, 5))
        name_value = create_styled_label(form_frame, text=product.get('name', '-') if is_edit else '-', style='body')
        name_value.pack(fill='x', padx=20, pady=(0, 10))

        # النوع
        type_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_type", "Type / النوع"), style='subheading')
        type_label.pack(pady=(0, 5))
        type_options = [self.LANGUAGES[self.current_language].get("wholesale", "Wholesale / جملة"), self.LANGUAGES[self.current_language].get("retail", "Retail / قطاعي")]
        type_menu = create_styled_option_menu(form_frame, values=type_options)
        if is_edit:
            type_menu.set(product.get('type', type_options[0]))
        type_menu.pack(fill='x', padx=20, pady=(0, 10))

        # عدد الكراتين
        carton_count_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("carton_count", "Carton Count / عدد الكراتين"), style='subheading')
        carton_count_label.pack(pady=(0, 5))
        carton_count_entry = create_styled_entry(form_frame)
        if is_edit:
            carton_count_entry.insert(0, str(product.get('carton_count', 0)))
        carton_count_entry.pack(fill='x', padx=20, pady=(0, 10))

        # كسر الكرتونة
        fraction_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("carton_fraction", "Carton Fraction / كسر الكرتونة"), style='subheading')
        fraction_label.pack(pady=(0, 5))
        fraction_options = [
            ("0", self.LANGUAGES[self.current_language].get("no_fraction", "No Fraction / لا شيء")),
            ("0.25", self.LANGUAGES[self.current_language].get("quarter_carton", "Quarter Carton / ربع كرتونة")),
            ("0.5", self.LANGUAGES[self.current_language].get("half_carton", "Half Carton / نصف كرتونة")),
            ("0.75", self.LANGUAGES[self.current_language].get("three_quarters_carton", "Three Quarters Carton / ثلاثة أرباع كرتونة")),
            ("0.33", self.LANGUAGES[self.current_language].get("third_carton", "Third Carton / ثلث كرتونة")),
            ("0.66", self.LANGUAGES[self.current_language].get("two_thirds_carton", "Two Thirds Carton / ثلثي كرتونة"))
        ]
        fraction_menu = create_styled_option_menu(form_frame, values=[label for val, label in fraction_options])
        if is_edit:
            current_fraction = str(product.get('carton_fraction', '0'))
            for val, label in fraction_options:
                if val == current_fraction:
                    fraction_menu.set(label)
                    break
            else:
                fraction_menu.set(fraction_options[0][1])
        else:
            fraction_menu.set(fraction_options[0][1])
        fraction_menu.pack(fill='x', padx=20, pady=(0, 10))

        # عدد في الكرتونة
        units_per_carton_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("units_per_carton", "Units/Carton / عدد في الكرتونة"), style='subheading')
        units_per_carton_label.pack(pady=(0, 5))
        units_per_carton_entry = create_styled_entry(form_frame)
        if is_edit:
            units_per_carton_entry.insert(0, str(product.get('units_per_carton', 0)))
        units_per_carton_entry.pack(fill='x', padx=20, pady=(0, 10))

        # نوع الوحدة
        unit_type_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("unit_type", "Unit Type / نوع الوحدة"), style='subheading')
        unit_type_label.pack(pady=(0, 5))
        unit_type_entry = create_styled_entry(form_frame)
        if is_edit:
            unit_type_entry.insert(0, str(product.get('unit_type', '')))
        unit_type_entry.pack(fill='x', padx=20, pady=(0, 10))

        # سعر الجملة
        wholesale_qty_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("wholesale_quantity", "Wholesale Qty / عدد الجملة"), style='subheading')
        wholesale_qty_label.pack(pady=(0, 5))
        wholesale_qty_entry = create_styled_entry(form_frame)
        if is_edit:
            wholesale_qty_entry.insert(0, str(product.get('wholesale_quantity', 0)))
        wholesale_qty_entry.pack(fill='x', padx=20, pady=(0, 10))

        wholesale_price_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("wholesale_price", "Wholesale Price / سعر الجملة"), style='subheading')
        wholesale_price_label.pack(pady=(0, 5))
        wholesale_price_entry = create_styled_entry(form_frame)
        if is_edit:
            wholesale_price_entry.insert(0, str(product.get('wholesale_price', 0)))
        wholesale_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # عدد القطاعي
        retail_qty_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("retail_quantity", "Retail Qty / عدد القطاعي"), style='subheading')
        retail_qty_label.pack(pady=(0, 5))
        retail_qty_entry = create_styled_entry(form_frame)
        if is_edit:
            retail_qty_entry.insert(0, str(product.get('retail_quantity', 0)))
        retail_qty_entry.pack(fill='x', padx=20, pady=(0, 10))

        # سعر القطاعي
        retail_price_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("retail_price", "Retail Price / سعر القطاعي"), style='subheading')
        retail_price_label.pack(pady=(0, 5))
        retail_price_entry = create_styled_entry(form_frame)
        if is_edit:
            retail_price_entry.insert(0, str(product.get('retail_price', 0)))
        retail_price_entry.pack(fill='x', padx=20, pady=(0, 10))

        # نكهة المنتج
        flavor_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_flavor", "Flavor / نكهة المنتج"), style='subheading')
        flavor_label.pack(pady=(0, 5))
        flavor_entry = create_styled_entry(form_frame)
        if is_edit:
            flavor_entry.insert(0, str(product.get('flavor', '-')))
        flavor_entry.pack(fill='x', padx=20, pady=(0, 10))

        # وزن المنتج
        weight_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("product_weight", "Weight / وزن المنتج"), style='subheading')
        weight_label.pack(pady=(0, 5))
        weight_entry = create_styled_entry(form_frame)
        if is_edit:
            weight_entry.insert(0, str(product.get('weight', '-')))
        weight_entry.pack(fill='x', padx=20, pady=(0, 10))

        # باركود (عرض فقط)
        barcode_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("barcode", "Barcode / باركود"), style='subheading')
        barcode_label.pack(pady=(0, 5))
        barcode_value = create_styled_label(form_frame, text=product.get('barcode', '-') if is_edit else '-', style='body')
        barcode_value.pack(fill='x', padx=20, pady=(0, 10))

        # التاريخ
        date_label = create_styled_label(form_frame, text=self.LANGUAGES[self.current_language].get("date", "Date / التاريخ"), style='subheading')
        date_label.pack(pady=(0, 5))
        date_entry = DateEntry(form_frame, width=18)
        if is_edit and product.get('date', ''):
            try:
                date_entry.set_date(product.get('date', ''))
            except Exception:
                pass
        date_entry.pack(fill='x', padx=20, pady=(0, 10))

        def save():
            try:
                name = name_value.cget('text')
                type_val = type_menu.get()
                carton_count = int(carton_count_entry.get() or 0)
                carton_fraction = 0.0
                for val, label in fraction_options:
                    if label == fraction_menu.get():
                        carton_fraction = float(val)
                        break
                units_per_carton = int(units_per_carton_entry.get() or 0)
                unit_type = unit_type_entry.get()
                wholesale_price = float(wholesale_price_entry.get() or 0)
                retail_qty = int(retail_qty_entry.get() or 0)
                retail_price = float(retail_price_entry.get() or 0)
                date_val = date_entry.get()
            except Exception:
                show_error(self.LANGUAGES[self.current_language].get("invalid_values", "Invalid values"), self.current_language)
                return
            if not is_edit:
                # تحقق من اختيار منتج من المخزون
                if not selected_inventory_product['product']:
                    show_error(self.LANGUAGES[self.current_language].get("product_not_found", "Product not found"), self.current_language)
                    return
                inv_item = selected_inventory_product['product']
                # تحقق من توفر الكمية المطلوبة في المخزون
                total_requested = carton_count + carton_fraction
                available = float(inv_item.get('carton_count', 0))
                if total_requested > available:
                    show_error(self.LANGUAGES[self.current_language].get("not_enough_inventory", "Not enough inventory"), self.current_language)
                    return
                # إنقاص الكمية من المخزون
                inv_item['carton_count'] = available - total_requested
                save_data("inventory", self.inventory)
                new_product = inv_item.copy()
                new_product['type'] = type_val
                new_product['carton_count'] = carton_count
                new_product['carton_fraction'] = carton_fraction
                new_product['units_per_carton'] = units_per_carton
                new_product['unit_type'] = unit_type
                new_product['wholesale_price'] = wholesale_price
                new_product['retail_quantity'] = retail_qty
                new_product['retail_price'] = retail_price
                new_product['date'] = date_val
                new_product['id'] = get_next_id('store_products')
                new_product['location'] = 'المحل / Shop'
                new_product['source'] = 'inventory'
                self.products.append(new_product)
                save_data("store_products", self.products)
                show_success(self.LANGUAGES[self.current_language].get("added_success", "Product added successfully!"), self.current_language)
            else:
                product['type'] = type_val
                product['carton_count'] = carton_count
                product['carton_fraction'] = carton_fraction
                product['units_per_carton'] = units_per_carton
                product['unit_type'] = unit_type
                product['wholesale_price'] = wholesale_price
                product['retail_quantity'] = retail_qty
                product['retail_price'] = retail_price
                product['date'] = date_val
                save_data("store_products", self.products)
                show_success(self.LANGUAGES[self.current_language].get("updated_success", "Product updated successfully!"), self.current_language)
            dialog.destroy()
            self.refresh_store()

        save_btn = create_styled_button(form_frame, text=self.LANGUAGES[self.current_language].get("save", "Save / حفظ"), style='primary', command=save)
        save_btn.pack(pady=10)

    def add_from_inventory_dialog(self):
        self.open_product_dialog(product=None)

    def edit_store_product(self, product_id):
        product = next((p for p in self.products if p.get('id') == product_id), None)
        if not product:
            show_error(self.LANGUAGES[self.current_language].get("product_not_found", "Product not found"), self.current_language)
            return
        self.open_product_dialog(product=product)

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