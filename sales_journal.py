import customtkinter as ctk
from tkinter import ttk, messagebox
from ui_elements import show_error, show_success
from data_handler import load_data, save_data, import_from_excel
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label
)
from datetime import datetime

class ViewSalesRecords:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.sales = load_data("sales") or []

    def refresh_sales(self):
        """Refresh the sales list from database and update display"""
        try:
            # Import data from Excel before loading from JSON
            if import_from_excel('sales_journal'):
                print("[DEBUG] Successfully imported data from Excel")
            else:
                print("[DEBUG] No Excel data to import or import failed")

            # Load sales from database
            self.sales = load_data("sales") or []
            print(f"[DEBUG] Loaded sales count: {len(self.sales)}")
            print(f"[DEBUG] Loaded sales: {self.sales}")
            
            # Refresh the display
            self.view_sales()
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"[TRACEBACK] {traceback_str}")
            show_error(f"Error refreshing sales: {str(e)}", self.current_language)

    def view_sales(self):
        """Create a modern sales records view interface"""
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
            text=self.LANGUAGES[self.current_language].get("sales_records", "Sales Records"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)
        
        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_sales
        )
        refresh_button.pack(side='right', padx=20, pady=20)
        
        # Summary cards
        summary_frame = create_styled_frame(main_frame, style='card')
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Calculate summary data
        total_sales = len(self.sales)
        today_sales = len([s for s in self.sales if s.get('date', '').startswith(str(datetime.now().date()))])
        total_revenue = sum(s.get('total', 0) for s in self.sales)
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        # Create summary cards
        summary_cards = [
            ("total_sales", "Total Sales", total_sales),
            ("today_sales", "Today's Sales", today_sales),
            ("total_revenue", "Total Revenue", f"${total_revenue:.2f}"),
            ("avg_sale", "Average Sale", f"${avg_sale:.2f}")
        ]
        
        for i, (key, default_text, value) in enumerate(summary_cards):
            card = create_styled_frame(summary_frame, style='card')
            card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
            
            label = create_styled_label(
                card,
                text=self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text)),
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
            placeholder_text=self.get_bilingual("search_sales", "Search sales...", "بحث عن مبيعات")
        )
        search_entry.pack(side='left', padx=20, pady=20, fill='x', expand=True)
        
        filter_button = create_styled_button(
            search_frame,
            text=self.get_bilingual("filter", "Filter", "تصفية"),
            style='outline'
        )
        filter_button.pack(side='right', padx=20, pady=20)
        
        # Sales records table
        table_frame = create_styled_frame(main_frame, style='card')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create scrollable frame for the table
        scrollable_table = ctk.CTkScrollableFrame(table_frame, orientation='vertical')
        scrollable_table.pack(fill='both', expand=True)
        
        # Table headers
        headers = [
            ("date", "Date"),
            ("items", "Items"),
            ("quantity", "Quantity"),
            ("total", "Total"),
            ("actions", "Actions")
        ]
        
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                scrollable_table,
                text=self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text)),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Sales records list
        for i, sale in enumerate(self.sales, 1):
            # Date
            date_label = create_styled_label(
                scrollable_table,
                text=sale.get('date', ''),
                style='body'
            )
            date_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            # Items
            items_text = ", ".join(f"{item['product']['name']} (x{item['quantity']})" for item in sale.get('items', []))
            items_label = create_styled_label(
                scrollable_table,
                text=items_text,
                style='body'
            )
            items_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            # Total quantity
            total_quantity = sum(item['quantity'] for item in sale.get('items', []))
            quantity_label = create_styled_label(
                scrollable_table,
                text=str(total_quantity),
                style='body'
            )
            quantity_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            # Total amount
            total_label = create_styled_label(
                scrollable_table,
                text=f"${sale.get('total', 0):.2f}",
                style='body'
            )
            total_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
            
            # Action buttons
            actions_frame = create_styled_frame(scrollable_table, style='card')
            actions_frame.grid(row=i, column=4, padx=10, pady=10, sticky='w')
            
            view_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("view", "View", "إظهار"),
                style='outline',
                width=80,
                command=lambda s=sale: self.view_sale_details(s)
            )
            view_button.pack(side='left', padx=5)
            
            print_button = create_styled_button(
                actions_frame,
                text=self.get_bilingual("print", "Print", "طباعة"),
                style='outline',
                width=80,
                command=lambda s=sale: self.print_sale(s)
            )
            print_button.pack(side='left', padx=5)

    def view_sale_details(self, sale):
        """View detailed information about a sale"""
        # Create a new window for sale details
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("sale_details", "Sale Details", "تفاصيل المبيعة"))
        dialog.geometry("600x400")
        
        # Sale details
        details_frame = create_styled_frame(dialog, style='card')
        details_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Sale ID and date
        info_frame = create_styled_frame(details_frame, style='card')
        info_frame.pack(fill='x', padx=20, pady=20)
        
        id_label = create_styled_label(
            info_frame,
            text=f"Sale #{sale.get('id', '')}",
            style='heading'
        )
        id_label.pack(side='left', padx=10)
        
        date_label = create_styled_label(
            info_frame,
            text=sale.get('date', ''),
            style='subheading'
        )
        date_label.pack(side='right', padx=10)
        
        # Items list
        items_frame = create_styled_frame(details_frame, style='card')
        items_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Items headers
        headers = [
            ("item", "Item"),
            ("quantity", "Quantity"),
            ("price", "Price"),
            ("subtotal", "Subtotal")
        ]
        
        for i, (key, default_text) in enumerate(headers):
            header = create_styled_label(
                items_frame,
                text=self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text)),
                style='subheading'
            )
            header.grid(row=0, column=i, padx=10, pady=10, sticky='w')
        
        # Items list
        for i, item in enumerate(sale.get('items', []), 1):
            # Item name
            name_label = create_styled_label(
                items_frame,
                text=item['product']['name'],
                style='body'
            )
            name_label.grid(row=i, column=0, padx=10, pady=10, sticky='w')
            
            # Quantity
            quantity_label = create_styled_label(
                items_frame,
                text=str(item['quantity']),
                style='body'
            )
            quantity_label.grid(row=i, column=1, padx=10, pady=10, sticky='w')
            
            # Price
            price_label = create_styled_label(
                items_frame,
                text=f"${item['product']['price']:.2f}",
                style='body'
            )
            price_label.grid(row=i, column=2, padx=10, pady=10, sticky='w')
            
            # Subtotal
            subtotal_label = create_styled_label(
                items_frame,
                text=f"${item['product']['price'] * item['quantity']:.2f}",
                style='body'
            )
            subtotal_label.grid(row=i, column=3, padx=10, pady=10, sticky='w')
        
        # Total
        total_frame = create_styled_frame(details_frame, style='card')
        total_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        total_label = create_styled_label(
            total_frame,
            text=self.get_bilingual("total", "Total:", "المجموع"),
            style='subheading'
        )
        total_label.pack(side='left', padx=20, pady=20)
        
        total_value = create_styled_label(
            total_frame,
            text=f"${sale.get('total', 0):.2f}",
            style='heading'
        )
        total_value.pack(side='right', padx=20, pady=20)

    def print_sale(self, sale):
        """Print a sale record"""
        # Implement printing functionality
        show_success(self.get_bilingual("printing", "Printing sale record...", "طباعة سجل المبيعة"), self.current_language)

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)