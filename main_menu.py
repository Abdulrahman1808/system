import tkinter as tk
from tkinter import ttk
import subprocess
from inventory_manager import InventoryManager
from ui_elements import show_error
from add_worker import AddWorker

import customtkinter as ctk
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label, toggle_theme,
    create_modern_card, create_gradient_label, create_glass_frame,
    create_status_indicator, create_animated_button
)

class MainMenu:
    def __init__(self, root, current_language, languages, callbacks):
        self.root = root
        self.LANGUAGES = languages
        self.callbacks = callbacks

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def create_main_menu(self):
        """Create the main menu interface with modern design"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container with gradient background
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Create modern sidebar with glass effect
        self.sidebar = ctk.CTkScrollableFrame(
            main_frame, 
            orientation='vertical', 
            fg_color=COLORS['sidebar'],
            width=280,
            corner_radius=0
        )
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        
        # Add modern shadow effect to sidebar
        shadow_frame = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS['shadow_color'],
            corner_radius=0,
            width=2,
            height=self.root.winfo_height()
        )
        shadow_frame.place(x=280, y=0)
        shadow_frame.lower()
        
        # Modern logo/Title with gradient
        logo_frame = create_glass_frame(self.sidebar)
        logo_frame.pack(fill='x', padx=20, pady=(30, 20))
        
        title_label = create_gradient_label(
            logo_frame,
            text=self.get_bilingual("app_title", "Hookah Shop Manager", "مدير متجر الشيشة"),
            gradient_colors=[COLORS['primary'], COLORS['secondary']]
        )
        title_label.pack(pady=20)
        
        # Modern menu items with hover effects
        menu_items = [
            ("manage_products", "Manage Products", self.callbacks['manage_products'], "📦", "primary"),
            ("manage_inventory", "Manage Inventory", self.callbacks['manage_inventory'], "📊", "secondary"),
            ("manage_store", "Manage Store", self.callbacks['manage_store'], "🏪", "accent"),
            ("record_sale", "Record Sale", self.callbacks['record_sale'], "💰", "success"),
            ("view_sales", "View Sales Records", self.callbacks['view_sales'], "📈", "info"),
            ("manage_suppliers", "Manage Suppliers", self.callbacks['manage_suppliers'], "🤝", "warning"),
            ("manage_employees", "Manage Employees", self.callbacks['manage_employees'], "👥", "primary"),
            ("manage_customers", "Manage Customers", self.callbacks['manage_customers'], "👤", "secondary"),
            ("reporting_analytics", "Reporting & Analytics", self.callbacks['reporting_analytics'], "📊", "accent"),
            ("expenses_bills", "Expenses & Bills", self.callbacks['expenses_bills'], "💸", "warning"),
            ("notifications", "Notifications", self.callbacks['notifications'], "🔔", "info"),
            ("manage_stores", "Manage Stores", self.open_manage_stores, "🏬", "success")
        ]
        
        for key, default_text, callback, icon, color_style in menu_items:
            # Create modern menu item with glass effect
            menu_item_frame = create_glass_frame(self.sidebar)
            menu_item_frame.pack(fill='x', padx=10, pady=5)
            
            button = create_animated_button(
                menu_item_frame,
                text=f"{icon} {self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text))}",
                style='ghost',
                command=callback,
                height=50
            )
            button.pack(fill='x', padx=10, pady=5)
            button.text_key = key
        
        # Modern theme toggle with glass effect
        theme_frame = create_glass_frame(self.sidebar)
        theme_frame.pack(fill='x', padx=10, pady=20)
        
        theme_button = create_animated_button(
            theme_frame,
            text=f"🌓 {self.get_bilingual('toggle_theme', 'Toggle Theme', 'تبديل المظهر')}",
            style='outline',
            command=self.toggle_theme,
            height=45
        )
        theme_button.pack(fill='x', padx=10, pady=5)
        theme_button.text_key = "toggle_theme"
        
        # Modern logout button
        logout_frame = create_glass_frame(self.sidebar)
        logout_frame.pack(side='bottom', fill='x', padx=10, pady=20)
        
        logout_button = create_animated_button(
            logout_frame,
            text="🚪 " + self.get_bilingual("logout", "Logout", "تسجيل الخروج"),
            style='error',
            command=self.callbacks['logout'],
            height=50
        )
        logout_button.pack(fill='x', padx=10, pady=5)
        logout_button.text_key = "logout"
        
        # Modern content area with glass effect
        content_frame = create_glass_frame(main_frame)
        content_frame.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        # Welcome section with gradient
        welcome_frame = create_modern_card(
            content_frame,
            title=self.get_bilingual("welcome", "Welcome to Hookah Shop Manager", "مرحباً بك في مدير متجر الشيشة"),
            content=self.get_bilingual("welcome_subtitle", "Your complete business management solution", "حلك الشامل لإدارة الأعمال")
        )
        welcome_frame.pack(fill='x', pady=(0, 30))
        
        # Quick actions section
        quick_actions_label = create_gradient_label(
            content_frame,
            text=self.get_bilingual("quick_actions", "Quick Actions", "إجراءات سريعة"),
            gradient_colors=[COLORS['primary'], COLORS['secondary']]
        )
        quick_actions_label.pack(pady=(0, 20))
        
        # Modern quick action cards in a responsive grid
        quick_actions_frame = create_styled_frame(content_frame, style='section')
        quick_actions_frame.pack(fill='both', expand=True)
        
        # Configure responsive grid
        quick_actions_frame.grid_columnconfigure(0, weight=1)
        quick_actions_frame.grid_columnconfigure(1, weight=1)
        quick_actions_frame.grid_columnconfigure(2, weight=1)
        quick_actions_frame.grid_columnconfigure(3, weight=1)
        
        # Enhanced quick action cards
        quick_actions = [
            ("record_sale", "Record Sale", self.callbacks['record_sale'], "💰", "Record a new sale transaction", "success"),
            ("manage_products", "Manage Products", self.callbacks['manage_products'], "📦", "Add or modify products", "primary"),
            ("view_sales", "View Sales", self.callbacks['view_sales'], "📈", "View sales history and reports", "info"),
            ("manage_employees", "Manage Employees", self.callbacks['manage_employees'], "👥", "Manage employee information", "secondary")
        ]
        
        for i, (key, default_text, callback, icon, description, color_style) in enumerate(quick_actions):
            # Create modern card with glass effect
            card = create_modern_card(
                quick_actions_frame,
                title=f"{icon} {self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text))}",
                content=description
            )
            card.grid(row=0, column=i, padx=15, pady=15, sticky='nsew')
            
            # Add action button
            action_button = create_animated_button(
                card,
                text=self.get_bilingual("open", "Open", "فتح"),
                style=color_style,
                command=callback,
                height=40
            )
            action_button.pack(fill='x', padx=20, pady=(0, 20))
        
        # Add status indicators
        status_frame = create_styled_frame(content_frame, style='section')
        status_frame.pack(fill='x', pady=20)
        
        # Status indicators row
        status_indicators_frame = create_styled_frame(status_frame, style='section')
        status_indicators_frame.pack(fill='x')
        
        # Configure status grid
        status_indicators_frame.grid_columnconfigure(0, weight=1)
        status_indicators_frame.grid_columnconfigure(1, weight=1)
        status_indicators_frame.grid_columnconfigure(2, weight=1)
        status_indicators_frame.grid_columnconfigure(3, weight=1)
        
        # Create status indicators
        status_indicators = [
            ("System Status", "Online", "success"),
            ("Database", "Connected", "info"),
            ("Updates", "Available", "warning"),
            ("Security", "Protected", "success")
        ]
        
        for i, (title, status, color) in enumerate(status_indicators):
            indicator = create_status_indicator(
                status_indicators_frame,
                status=color,
                text=f"{title}: {status}"
            )
            indicator.grid(row=0, column=i, padx=10, pady=10, sticky='ew')

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = toggle_theme()
        # Refresh the menu to apply new theme
        self.create_main_menu()

    def open_excel(self, filename):
        """Open an Excel file"""
        try:
            subprocess.Popen(['start', filename], shell=True)
        except Exception as e:
            show_error(f"Error opening {filename}: {str(e)}", self.LANGUAGES['ar'].get('language', 'اللغة'))

    def open_add_worker(self):
        """Open the add worker dialog"""
        AddWorker(self.root, self.LANGUAGES['ar'].get('language', 'اللغة'), self.LANGUAGES)

    def switch_language(self, language):
        """Switch the application language"""
        if language in self.LANGUAGES:
            self.LANGUAGES = language
            self.create_main_menu()
        else:
            show_error(f"Language {language} not supported", self.LANGUAGES['ar'].get('language', 'اللغة'))

    def open_manage_stores(self):
        """Open the manage stores interface"""
        from manage_stores import ManageStores
        manage_stores_ui = ManageStores(self.root, self.LANGUAGES, self.create_main_menu)
        manage_stores_ui.manage_stores()
