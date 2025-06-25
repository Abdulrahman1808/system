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
    create_styled_label, toggle_theme
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
        """Create the main menu interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Create scrollable sidebar
        self.sidebar = ctk.CTkScrollableFrame(main_frame, orientation='vertical', fg_color=COLORS['sidebar'], width=250)
        self.sidebar.pack(side='left', fill='y', padx=0, pady=0)
        
        # Add shadow effect to sidebar
        self.sidebar.configure(border_width=0)
        shadow_frame = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS['shadow_color'],
            corner_radius=0,
            width=1,
            height=self.root.winfo_height()
        )
        shadow_frame.place(x=250, y=0)
        shadow_frame.lower()  # Place shadow behind the sidebar
        
        # Logo/Title
        title_label = create_styled_label(
            self.sidebar,
            text=self.get_bilingual("app_title", "Hookah Shop Manager", "مدير متجر الشيشة"),
            style='heading'
        )
        title_label.pack(pady=(30, 40))
        
        # Menu items with icons
        menu_items = [
            ("manage_products", "Manage Products", self.callbacks['manage_products'], "📦"),
            ("manage_inventory", "Manage Inventory", self.callbacks['manage_inventory'], "📊"),
            ("record_sale", "Record Sale", self.callbacks['record_sale'], "💰"),
            ("view_sales", "View Sales Records", self.callbacks['view_sales'], "📈"),
            ("manage_suppliers", "Manage Suppliers", self.callbacks['manage_suppliers'], "🤝"),
            ("manage_employees", "Manage Employees", self.callbacks['manage_employees'], "👥"),
            ("manage_customers", "Manage Customers", self.callbacks['manage_customers'], "👥"),
            ("reporting_analytics", "Reporting and Analytics", self.callbacks['reporting_analytics'], "📊"),
            ("expenses_bills", "Expenses and Bills", self.callbacks['expenses_bills'], "💸"),
            ("notifications", "Notifications", self.callbacks['notifications'], "🔔"),
            ("manage_stores", "Manage Stores", self.open_manage_stores, "🏬")
        ]
        
        for key, default_text, callback, icon in menu_items:
            button = create_styled_button(
                self.sidebar,
                text=f"{icon} {self.get_bilingual(key, default_text, self.LANGUAGES['ar'].get(key, default_text))}",
                style='sidebar',
                command=callback,
                height=45
            )
            button.text_key = key
            button.pack(fill='x', padx=5, pady=5)
        
        # Theme toggle
        theme_button = create_styled_button(
            self.sidebar,
            text=f"🌓 {self.get_bilingual('toggle_theme', 'Toggle Theme', 'تبديل المظهر')}",
            style='sidebar',
            command=self.toggle_theme,
            height=40
        )
        theme_button.text_key = "toggle_theme"
        theme_button.pack(fill='x', pady=5)
        
        # Logout button
        logout_button = create_styled_button(
            self.sidebar,
            text="🚪 " + self.get_bilingual("logout", "Logout", "تسجيل الخروج"),
            style='error',
            command=self.callbacks['logout'],
            height=45
        )
        logout_button.text_key = "logout"
        logout_button.pack(side='bottom', fill='x', padx=15, pady=20)
        
        # Content area
        content_frame = create_styled_frame(main_frame, style='section')
        content_frame.pack(side='right', fill='both', expand=True, padx=30, pady=30)
        
        # Welcome message
        welcome_label = create_styled_label(
            content_frame,
            text=self.get_bilingual("welcome", "Welcome to Hookah Shop Manager", "مرحباً بك في مدير متجر الشيشة"),
            style='heading'
        )
        welcome_label.text_key = "welcome"
        welcome_label.pack(pady=(0, 30))
        
        # Quick actions
        quick_actions_label = create_styled_label(
            content_frame,
            text=self.get_bilingual("quick_actions", "Quick Actions", "إجراءات سريعة"),
            style='subheading'
        )
        quick_actions_label.text_key = "quick_actions"
        quick_actions_label.pack(pady=(0, 20))
        
        # Quick action cards in a grid
        quick_actions_frame = create_styled_frame(content_frame, style='section')
        quick_actions_frame.pack(fill='both', expand=True)
        
        # Configure grid
        quick_actions_frame.grid_columnconfigure(0, weight=1)
        quick_actions_frame.grid_columnconfigure(1, weight=1)
        quick_actions_frame.grid_columnconfigure(2, weight=1)
        
        # Quick action cards
        quick_actions = [
            ("record_sale", "Record Sale", self.callbacks['record_sale'], "💰", "Record a new sale transaction"),
            ("manage_products", "Manage Products", self.callbacks['manage_products'], "📦", "Add or modify products"),
            ("view_sales", "View Sales", self.callbacks['view_sales'], "📈", "View sales history and reports"),
            ("manage_employees", "Manage Employees", self.callbacks['manage_employees'], "👥", "Manage employee information")
        ]
        
        for i, (key, default_text, callback, icon, description) in enumerate(quick_actions):
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

    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def open_add_worker(self):
        """Open the Add Worker interface"""
        add_worker_ui = AddWorker(self.root, self.LANGUAGES['ar'].get('language', 'اللغة'), self.LANGUAGES, self.create_main_menu)
        add_worker_ui.add_worker()

    def switch_language(self, language):
        """Switch the application language"""
        if language in self.LANGUAGES:
            self.LANGUAGES = language
            self.create_main_menu()
        else:
            show_error(f"Language {language} not supported", self.LANGUAGES['ar'].get('language', 'اللغة'))

    def open_manage_stores(self):
        """Open the Manage Stores interface"""
        from manage_stores import ManageStores
        manage_stores_ui = ManageStores(self.root, self.LANGUAGES, self.create_main_menu)
        manage_stores_ui.manage_stores()
