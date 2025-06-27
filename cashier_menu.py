import customtkinter as ctk
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label
)
from data_handler import load_data
from datetime import datetime, date

class CashierMenu:
    def __init__(self, root, current_language, languages, callbacks):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.callbacks = callbacks

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def get_today_sales_stats(self):
        """Get today's sales statistics"""
        try:
            sales_data = load_data("sales") or []
            today = date.today().strftime("%Y-%m-%d")
            
            today_sales = [sale for sale in sales_data if sale.get('date', '').startswith(today)]
            
            total_sales = len(today_sales)
            total_amount = sum(float(sale.get('total_amount', 0)) for sale in today_sales)
            
            return total_sales, total_amount
        except Exception as e:
            print(f"Error getting sales stats: {e}")
            return 0, 0

    def create_cashier_menu(self):
        """Create the cashier menu interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Header
        header_frame = create_styled_frame(main_frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        # Title and current time
        title_frame = create_styled_frame(header_frame, style='card')
        title_frame.pack(side='left', padx=20, pady=20)
        
        title_label = create_styled_label(
            title_frame,
            text=self.get_bilingual("cashier_account", "Cashier Account", "حساب الكاشير"),
            style='heading'
        )
        title_label.pack()
        
        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        time_label = create_styled_label(
            title_frame,
            text=f"🕐 {current_time}",
            style='body'
        )
        time_label.pack()
        
        # Logout button
        logout_button = create_styled_button(
            header_frame,
            text=self.get_bilingual("logout", "Logout", "تسجيل الخروج"),
            style='error',
            command=self.callbacks['logout']
        )
        logout_button.pack(side='right', padx=20, pady=20)
        
        # Main content area
        content_frame = create_styled_frame(main_frame, style='section')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Welcome message
        welcome_label = create_styled_label(
            content_frame,
            text=self.get_bilingual("welcome", "Welcome to Cashier System", "مرحباً بك في نظام الكاشير"),
            style='subheading'
        )
        welcome_label.pack(pady=(0, 20))
        
        # Today's stats
        total_sales, total_amount = self.get_today_sales_stats()
        stats_frame = create_styled_frame(content_frame, style='card')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        today_stats_en = "Today's Statistics"
        stats_text = f"📊 {self.get_bilingual('today_stats', today_stats_en, 'إحصائيات اليوم')}: {total_sales} {self.get_bilingual('sales', 'Sales', 'مبيعات')} - ${total_amount:.2f}"
        stats_label = create_styled_label(
            stats_frame,
            text=stats_text,
            style='body'
        )
        stats_label.pack(pady=10)
        
        # Quick actions for cashier
        quick_actions_frame = create_styled_frame(content_frame, style='section')
        quick_actions_frame.pack(fill='both', expand=True)
        
        # Configure grid
        quick_actions_frame.grid_columnconfigure(0, weight=1)
        quick_actions_frame.grid_columnconfigure(1, weight=1)
        
        # Cashier quick actions
        cashier_actions = [
            ("record_sale", "Record Sale", self.callbacks['record_sale'], "💰", "Record a new sale transaction"),
            ("view_sales", "View Sales", self.callbacks['view_sales'], "📈", "View today's sales and history")
        ]
        
        for i, (key, default_text, callback, icon, description) in enumerate(cashier_actions):
            card = create_styled_frame(quick_actions_frame, style='quick_action_card')
            card.grid(row=0, column=i, padx=15, pady=15, sticky='nsew')
            
            # Icon and title
            title_frame = create_styled_frame(card, style='card')
            title_frame.pack(fill='x', padx=20, pady=(20, 10))
            
            icon_label = create_styled_label(
                title_frame,
                text=icon,
                style='heading'
            )
            icon_label.pack(pady=(0, 10))
            
            title_label = create_styled_label(
                title_frame,
                text=self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text)),
                style='subheading'
            )
            title_label.pack(pady=(0, 10))
            
            # Description
            desc_label = create_styled_label(
                card,
                text=description,
                style='body'
            )
            desc_label.pack(padx=20, pady=(0, 20))
            
            # Action button
            action_button = create_styled_button(
                card,
                text=self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text)),
                style='quick_action',
                command=callback,
                height=45
            )
            action_button.pack(fill='x', padx=20, pady=(0, 20)) 