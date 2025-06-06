import customtkinter as ctk
from main_menu import MainMenu
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
                "reporting_analytics": "Reporting and Analytics"
            }
        }
        
        # Initialize screens
        self.initialize_screens()
        
        # Show login screen
        self.show_login()
    
    def initialize_screens(self):
        """Initialize all screens and their callbacks"""
        self.callbacks = {
            'manage_products': self.show_product_manager,
            'manage_inventory': self.show_inventory_manager,
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
        self.view_sales = ViewSalesRecords(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.manage_suppliers = ManageSuppliers(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.manage_employees = ManageEmployees(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.customer_manager = CustomerManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.reporting_analytics = ReportingAnalytics(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.expenses_bills = ExpensesBillsManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu)
        self.notifications_manager = NotificationsManager(self.root, self.current_language, self.LANGUAGES, self.show_main_menu, self.callbacks)
        self.main_menu = MainMenu(self.root, self.current_language, self.LANGUAGES, self.callbacks)
    
    def show_login(self):
        """Show the login screen"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Login Frame (styled as a card)
        login_frame = create_styled_frame(self.root, style='card', width=400, height=450)
        login_frame.place(relx=0.5, rely=0.5, anchor='center') # Use place for centering
        
        # Title Label
        title_label = create_styled_label(
            self.root,
            text=self.LANGUAGES[self.current_language].get("welcome", "Welcome to Hookah Shop Management System"),
            style='heading'
        )
        title_label.pack(pady=40)

        # Input fields frame (inside the card)
        input_frame = create_styled_frame(login_frame, style='card') # Inner frame within the card
        input_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Username
        username_label = create_styled_label(
            input_frame,
            text=self.LANGUAGES[self.current_language].get("username", "Username"),
            style='body'
        )
        username_label.pack(pady=(0, 5))
        username_entry = create_styled_entry(input_frame)
        username_entry.pack(pady=(0, 15))

        # Password
        password_label = create_styled_label(
            input_frame,
            text=self.LANGUAGES[self.current_language].get("password", "Password"),
            style='body'
        )
        password_label.pack(pady=(0, 5))
        password_entry = create_styled_entry(input_frame, show="*")
        password_entry.pack(pady=(0, 20))

        # Submit Button
        submit_button = create_styled_button(
            input_frame,
            text=self.LANGUAGES[self.current_language].get("submit", "Submit"),
            style='primary',
            command=lambda: self.process_login(username_entry.get(), password_entry.get())
        )
        submit_button.pack(pady=20)
    
    def process_login(self, username, password):
        """Process login attempt"""
        # For now, allow any non-empty credentials
        if username and password:
            self.show_main_menu()
        else:
            ctk.messagebox.showerror(
                self.LANGUAGES[self.current_language]["error"],
                "Please enter both username and password"
            )
    
    def show_main_menu(self):
        """Show the main menu"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Show main menu
        self.main_menu.create_main_menu()
    
    def show_product_manager(self):
        """Show the product manager screen"""
        self.product_manager.manage_products()
    
    def show_inventory_manager(self):
        """Show the inventory manager screen"""
        self.inventory_manager.manage_inventory()
    
    def show_record_sale(self):
        """Show the record sale screen"""
        self.record_sale.record_sale()
    
    def show_sales_records(self):
        """Show the sales records screen"""
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
        self.show_login()
    
    def switch_language(self, language):
        """Switch the application language"""
        if language in self.LANGUAGES:
            self.current_language = language
            self.show_main_menu()

if __name__ == "__main__":
    root = ctk.CTk()
    app = HookahShopApp(root)
    root.mainloop()