import customtkinter as ctk
import tkinter.messagebox as messagebox
from main_menu import MainMenu
from cashier_menu import CashierMenu
from inventory_manager import InventoryManager
from product_manager import ProductManager
from accounts_receivable import RecordSale
from sales_journal import ViewSalesRecords
from manage_suppliers import ManageSuppliers
from manage_employees import ManageEmployees
from manage_customers import CustomerManager
from reporting_analytics import ReportingAnalytics
from accounts_payable import ExpensesBillsManager
from notifications_manager import NotificationsManager
from theme import apply_theme, create_styled_frame, create_styled_label, create_styled_entry, create_styled_button
from data_handler import load_credentials, import_from_excel

class HookahShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hookah Shop Management System")
        self.root.geometry("1200x800")
        
        # Apply theme
        apply_theme(self.root)
        
        # Initialize language
        self.current_language = "en"
        self.LANGUAGES = {
            "en": {
                "login": "Login",
                "username": "Username",
                "password": "Password",
                "submit": "Submit",
                "error": "Error",
                "success": "Success",
                "welcome": "Welcome to Hookah Shop Management System",
                "manage_products": "Manage Products",
                "manage_inventory": "Manage Inventory",
                "record_sale": "Record Sale",
                "view_sales": "View Sales",
                "manage_suppliers": "Manage Suppliers",
                "manage_employees": "Manage Employees",
                "settings": "Settings",
                "logout": "Logout",
                "manage_customers": "Manage Customers",
                "reporting_analytics": "Reporting and Analytics",
                "admin_account": "Admin Account",
                "cashier_account": "Cashier Account",
                "select_account_type": "Select Account Type",
                "admin_login": "Admin Login",
                "cashier_login": "Cashier Login",
                "invalid_credentials": "Invalid credentials",
                "enter_credentials": "Please enter both username and password",
                "today_stats": "Today's Statistics",
                "sales": "Sales"
            },
            "ar": {
                "login": "تسجيل الدخول",
                "username": "اسم المستخدم",
                "password": "كلمة المرور",
                "submit": "إرسال",
                "error": "خطأ",
                "success": "نجاح",
                "welcome": "مرحباً بك في نظام إدارة متجر الشيشة",
                "manage_products": "إدارة المنتجات",
                "manage_inventory": "إدارة المخزون",
                "record_sale": "تسجيل المبيعات",
                "view_sales": "إظهار المبيعات",
                "manage_suppliers": "إدارة الموردين",
                "manage_employees": "إدارة الموظفين",
                "settings": "الإعدادات",
                "logout": "تسجيل خروج",
                "manage_customers": "إدارة الزبائن",
                "reporting_analytics": "التقارير والتحليلات",
                "admin_account": "حساب الإدارة",
                "cashier_account": "حساب الكاشير",
                "select_account_type": "اختر نوع الحساب",
                "admin_login": "تسجيل دخول الإدارة",
                "cashier_login": "تسجيل دخول الكاشير",
                "invalid_credentials": "بيانات غير صحيحة",
                "enter_credentials": "يرجى إدخال اسم المستخدم وكلمة المرور",
                "today_stats": "إحصائيات اليوم",
                "sales": "المبيعات"
            }
        }
        
        # Initialize screens
        self.initialize_screens()
        
        # Show account selection screen
        self.show_account_selection()
    
    def initialize_screens(self):
        """Initialize all screens and their callbacks"""
        self.callbacks = {
            'manage_products': self.show_product_manager,
            'manage_inventory': self.show_inventory_manager,
            'manage_store': self.show_store_manager,
            'record_sale': self.show_record_sale,
            'view_sales': self.show_sales_records,
            'manage_suppliers': self.show_suppliers,
            'manage_employees': self.show_employees,
            'settings': self.show_settings,
            'logout': self.logout,
            'switch_language': self.switch_language,
            'manage_customers': self.show_customer_manager,
            'reporting_analytics': self.show_reporting_analytics,
            'expenses_bills': self.show_expenses_bills,
            'notifications': self.show_notifications
        }
        
        # Initialize screen managers
        self.record_sale = RecordSale(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.product_manager = ProductManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu, record_sale_instance=self.record_sale)
        self.inventory_manager = InventoryManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.store_manager = None  # سننشئه عند الحاجة
        self.view_sales = ViewSalesRecords(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.manage_suppliers = ManageSuppliers(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.manage_employees = ManageEmployees(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.customer_manager = CustomerManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.reporting_analytics = ReportingAnalytics(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.expenses_bills = ExpensesBillsManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.notifications_manager = NotificationsManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu, self.callbacks)
        self.main_menu = MainMenu(self.root, self.current_language, self.LANGUAGES, self.callbacks)
        self.cashier_menu = CashierMenu(self.root, self.current_language, self.LANGUAGES, self.callbacks)
    
    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"
    
    def show_account_selection(self):
        """Show account type selection screen"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = create_styled_label(
            self.root,
            text=self.get_bilingual("welcome", "Welcome to Hookah Shop Management System", "مرحباً بك في نظام إدارة متجر الشيشة"),
            style='heading'
        )
        title_label.pack(pady=40)
        
        # Account type selection frame
        selection_frame = create_styled_frame(main_frame, style='card', width=600, height=400)
        selection_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Selection title
        selection_title = create_styled_label(
            selection_frame,
            text=self.get_bilingual("select_account_type", "Select Account Type", "اختر نوع الحساب"),
            style='subheading'
        )
        selection_title.pack(pady=30)
        
        # Admin account button
        admin_button = create_styled_button(
            selection_frame,
            text=f"👨‍💼 {self.get_bilingual('admin_account', 'Admin Account', 'حساب الإدارة')}",
            style='primary',
            command=lambda: self.show_login('admin'),
            height=60,
            width=300
        )
        admin_button.pack(pady=20)
        
        # Cashier account button
        cashier_button = create_styled_button(
            selection_frame,
            text=f"💼 {self.get_bilingual('cashier_account', 'Cashier Account', 'حساب الكاشير')}",
            style='secondary',
            command=lambda: self.show_login('cashier'),
            height=60,
            width=300
        )
        cashier_button.pack(pady=20)
    
    def show_login(self, account_type):
        """Show the login screen for specific account type"""
        self.current_account_type = account_type
        
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Login Frame (styled as a card)
        login_frame = create_styled_frame(self.root, style='card', width=400, height=450)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title Label
        title_text = self.get_bilingual("admin_login", "Admin Login", "تسجيل دخول الإدارة") if account_type == 'admin' else self.get_bilingual("cashier_login", "Cashier Login", "تسجيل دخول الكاشير")
        title_label = create_styled_label(
            self.root,
            text=title_text,
            style='heading'
        )
        title_label.pack(pady=40)

        # Input fields frame (inside the card)
        input_frame = create_styled_frame(login_frame, style='card')
        input_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Username
        username_label = create_styled_label(
            input_frame,
            text=self.get_bilingual("username", "Username", "اسم المستخدم"),
            style='body'
        )
        username_label.pack(pady=(0, 5))
        username_entry = create_styled_entry(input_frame)
        username_entry.pack(pady=(0, 15))

        # Password
        password_label = create_styled_label(
            input_frame,
            text=self.get_bilingual("password", "Password", "كلمة المرور"),
            style='body'
        )
        password_label.pack(pady=(0, 5))
        password_entry = create_styled_entry(input_frame, show="*")
        password_entry.pack(pady=(0, 20))

        # Submit Button
        submit_button = create_styled_button(
            input_frame,
            text=self.get_bilingual("submit", "Submit", "إرسال"),
            style='primary',
            command=lambda: self.process_login(username_entry.get(), password_entry.get())
        )
        submit_button.pack(pady=20)
        
        # Back button
        back_button = create_styled_button(
            input_frame,
            text=self.get_bilingual("back", "Back", "رجوع"),
            style='outline',
            command=self.show_account_selection
        )
        back_button.pack(pady=10)
    
    def process_login(self, username, password):
        """Process login attempt"""
        # تحقق فعلي من بيانات الدخول
        valid_credentials = {
            'admin': {'username': 'admin', 'password': 'admin123'},
            'cashier': {'username': 'cashier', 'password': 'cashier123'}
        }
        account_type = getattr(self, 'current_account_type', None)
        if account_type in valid_credentials:
            creds = valid_credentials[account_type]
            if username == creds['username'] and password == creds['password']:
                self.show_main_menu()
                return
            else:
                messagebox.showerror(
                    self.get_bilingual("error", "Error", "خطأ"),
                    self.get_bilingual("invalid_credentials", "Invalid credentials", "بيانات غير صحيحة")
                )
                return
        # في حال لم يتم اختيار نوع الحساب أو بيانات غير مكتملة
        messagebox.showerror(
            self.get_bilingual("error", "Error", "خطأ"),
            self.get_bilingual("enter_credentials", "Please enter both username and password", "يرجى إدخال اسم المستخدم وكلمة المرور")
        )
    
    def show_main_menu(self):
        """Show the main menu based on account type"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show appropriate menu based on account type
        if hasattr(self, 'current_account_type') and self.current_account_type == 'cashier':
            self.show_cashier_menu()
        else:
            self.main_menu.create_main_menu()
    
    def show_cashier_menu(self):
        """Show cashier-specific menu with sales functionality"""
        self.cashier_menu.create_cashier_menu()
    
    def show_product_manager(self):
        """Show the product manager screen"""
        self.product_manager.manage_products()
    
    def show_inventory_manager(self):
        """Show the inventory manager screen"""
        self.inventory_manager.manage_inventory()
    
    def show_record_sale(self):
        """Show the record sale screen"""
        # Set the back callback based on account type
        if hasattr(self, 'current_account_type') and self.current_account_type == 'cashier':
            self.record_sale.back_callback = self.show_cashier_menu
        else:
            self.record_sale.back_callback = self.show_main_menu
        self.record_sale.record_sale()
    
    def show_sales_records(self):
        """Show the sales records screen"""
        # Set the back callback based on account type
        if hasattr(self, 'current_account_type') and self.current_account_type == 'cashier':
            self.view_sales.back_callback = self.show_cashier_menu
        else:
            self.view_sales.back_callback = self.show_main_menu
        self.view_sales.view_sales()
    
    def show_suppliers(self):
        """Show the suppliers management screen"""
        self.manage_suppliers.manage_suppliers()
    
    def show_employees(self):
        """Show the employees management screen"""
        self.manage_employees.manage_employees()
    
    def show_customer_manager(self):
        """Show the customer manager screen"""
        self.customer_manager.manage_customers()
    
    def show_reporting_analytics(self):
        """Show the reporting and analytics screen"""
        self.reporting_analytics.create_reporting_analytics_interface()
    
    def show_expenses_bills(self):
        """Show the expenses and bills screen"""
        self.expenses_bills.create_expenses_bills_interface()
    
    def show_notifications(self):
        """Show the notifications and alerts screen"""
        self.notifications_manager.create_notifications_interface()
    
    def show_settings(self):
        """Show the settings screen"""
        # TODO: Implement settings screen
        pass
    
    def logout(self):
        """Logout and return to login screen"""
        self.show_account_selection()
    
    def switch_language(self, language):
        """Switch the application language"""
        if language in self.LANGUAGES:
            self.current_language = language
            self.show_main_menu()
    
    def show_store_manager(self):
        from store_manager import StoreManager
        if not self.store_manager:
            self.store_manager = StoreManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
            # اربط شاشة المخزون بشاشة المحل
            self.inventory_manager.store_manager_instance = self.store_manager
        self.store_manager.manage_store()

if __name__ == "__main__":
    root = ctk.CTk()
    app = HookahShopApp(root)
    root.mainloop()