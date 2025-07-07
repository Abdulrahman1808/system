import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, create_styled_entry, COLORS, FONTS

# Import data handling functions
from data_handler import load_data # Import load_data
from ui_elements import show_success, show_error
from datetime import datetime, timedelta # Import for date calculations
import statistics # For dynamic low stock threshold

class NotificationsManager:
    def __init__(self, root, current_language, languages, back_callback, callbacks):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.callbacks = callbacks # Store callbacks for navigation

        self.frame = None # Main frame for this section
        self.notifications_scroll_frame = None # Scrollable frame for the list

        # Initialize data and alerts list
        self.inventory_data = []
        self.bills_data = []
        self.active_alerts = []

        # Calculate initial low stock threshold (can be made configurable later)
        self.low_stock_threshold = 10 # Default value
        self._calculate_low_stock_threshold()

    def _calculate_low_stock_threshold(self):
        """Calculate a dynamic low stock threshold based on inventory median quantity"""
        self.inventory_data = load_data('inventory') or []
        quantities = [int(item.get('quantity', 0)) for item in self.inventory_data if item.get('quantity')]
        if quantities:
            self.low_stock_threshold = max(1, int(statistics.median(quantities) * 0.25))
            print(f"[DEBUG] Calculated dynamic low stock threshold: {self.low_stock_threshold}")
        else:
            self.low_stock_threshold = 10 # Fallback to default
            print(f"[DEBUG] No inventory data, using default low stock threshold: {self.low_stock_threshold}")

    def check_low_stock(self):
        """Check inventory for items below the low stock threshold"""
        low_stock_alerts = []
        self.inventory_data = load_data('inventory') or [] # Reload data to be current

        for item in self.inventory_data:
            try:
                quantity = int(item.get('quantity', 0))
                retail_quantity = int(item.get('retail_quantity', 0))
                item_name = item.get('name', self.LANGUAGES[self.current_language].get("unnamed_item", "Unnamed Item"))
                
                # Check wholesale quantity
                if quantity <= self.low_stock_threshold:
                    alert_message = self.LANGUAGES[self.current_language].get(
                        "low_stock_alert",
                        f"Low stock for {item_name}. Only {quantity} left. (Threshold: {self.low_stock_threshold})"
                    ).format(item_name=item_name, quantity=quantity, threshold=self.low_stock_threshold)
                    low_stock_alerts.append({
                        'type': 'low_stock',
                        'message': alert_message,
                        'item_id': item.get('id'),
                        'severity': 'warning',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Check retail quantity (different threshold)
                retail_threshold = max(1, self.low_stock_threshold * 2)  # Higher threshold for retail
                if retail_quantity <= retail_threshold:
                    alert_message = self.LANGUAGES[self.current_language].get(
                        "low_retail_stock_alert",
                        f"Low retail stock for {item_name}. Only {retail_quantity} retail units left."
                    ).format(item_name=item_name, quantity=retail_quantity)
                    low_stock_alerts.append({
                        'type': 'low_retail_stock',
                        'message': alert_message,
                        'item_id': item.get('id'),
                        'severity': 'info',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                # Check out of stock
                if quantity <= 0 and retail_quantity <= 0:
                    alert_message = self.LANGUAGES[self.current_language].get(
                        "out_of_stock_alert",
                        f"OUT OF STOCK: {item_name} is completely out of stock!"
                    ).format(item_name=item_name)
                    low_stock_alerts.append({
                        'type': 'out_of_stock',
                        'message': alert_message,
                        'item_id': item.get('id'),
                        'severity': 'critical',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
            except (ValueError, TypeError):
                continue # Skip items with invalid quantity data

        return low_stock_alerts

    def check_upcoming_bills(self, days_threshold=7):
        """Check for bills due within the next specified number of days"""
        upcoming_bills_alerts = []
        self.bills_data = load_data('bills') or [] # Reload data to be current
        today = datetime.now().date()

        for bill in self.bills_data:
            due_date_str = bill.get('date') # Assuming 'date' field stores the due date
            description = bill.get('description', self.LANGUAGES[self.current_language].get("unspecified_bill", "Unspecified Bill"))
            amount = bill.get('amount', 0)

            if not due_date_str:
                continue # Skip bills without a due date

            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                days_until_due = (due_date - today).days

                if 0 <= days_until_due <= days_threshold:
                     alert_message = self.LANGUAGES[self.current_language].get(
                         "upcoming_bill_alert",
                         f"Bill for {description} (${amount:.2f}) is due in {days_until_due} days."
                     ).format(description=description, amount=float(amount), days_until_due=days_until_due)
                     upcoming_bills_alerts.append({
                         'type': 'upcoming_bill',
                         'message': alert_message,
                         'bill_id': bill.get('id'), # Include relevant IDs
                         'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                     })
            except ValueError:
                continue # Skip bills with invalid date format
            except TypeError:
                continue # Skip bills with invalid amount or other type issues

        return upcoming_bills_alerts

    def check_high_sales_products(self):
        """Check for products with high sales or trending items"""
        high_sales_alerts = []
        sales_data = load_data('sales_journal') or []
        
        if not sales_data:
            return high_sales_alerts
        
        # Group sales by product
        product_sales = {}
        for sale in sales_data:
            items = sale.get('items', [])
            for item in items:
                product_name = item.get('product_name', 'Unknown Product')
                quantity = int(item.get('quantity', 0))
                if product_name in product_sales:
                    product_sales[product_name] += quantity
                else:
                    product_sales[product_name] = quantity
        
        # Find top selling products
        if product_sales:
            sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
            top_products = sorted_products[:3]  # Top 3 products
            
            for product_name, total_sold in top_products:
                alert_message = self.LANGUAGES[self.current_language].get(
                    "high_sales_alert",
                    f"High sales alert: {product_name} has sold {total_sold} units"
                ).format(product_name=product_name, total_sold=total_sold)
                
                high_sales_alerts.append({
                    'type': 'high_sales',
                    'message': alert_message,
                    'product_name': product_name,
                    'severity': 'info',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return high_sales_alerts

    def check_expired_products(self):
        """Check for products that might be expired or near expiry"""
        expired_alerts = []
        inventory_data = load_data('inventory') or []
        
        for item in inventory_data:
            expiry_date_str = item.get('expiry_date')
            if expiry_date_str:
                try:
                    expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    days_until_expiry = (expiry_date - today).days
                    
                    if days_until_expiry <= 0:
                        alert_message = self.LANGUAGES[self.current_language].get(
                            "expired_product_alert",
                            f"EXPIRED: {item.get('name', 'Unknown Product')} has expired!"
                        ).format(product_name=item.get('name', 'Unknown Product'))
                        
                        expired_alerts.append({
                            'type': 'expired_product',
                            'message': alert_message,
                            'item_id': item.get('id'),
                            'severity': 'critical',
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    elif days_until_expiry <= 30:  # Warning for products expiring within 30 days
                        alert_message = self.LANGUAGES[self.current_language].get(
                            "expiring_soon_alert",
                            f"Expiring soon: {item.get('name', 'Unknown Product')} expires in {days_until_expiry} days"
                        ).format(product_name=item.get('name', 'Unknown Product'), days=days_until_expiry)
                        
                        expired_alerts.append({
                            'type': 'expiring_soon',
                            'message': alert_message,
                            'item_id': item.get('id'),
                            'severity': 'warning',
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except ValueError:
                    continue  # Skip items with invalid date format
        
        return expired_alerts

    def generate_alerts(self):
        """Generate a combined list of all active alerts"""
        print("[DEBUG] Generating alerts...")
        low_stock = self.check_low_stock()
        upcoming_bills = self.check_upcoming_bills() # Check bills due in next 7 days
        high_sales = self.check_high_sales_products() # Check high sales products
        expired_products = self.check_expired_products() # Check expired products

        self.active_alerts = low_stock + upcoming_bills + high_sales + expired_products
        
        # Sort alerts by severity (critical first, then warning, then info)
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        self.active_alerts.sort(key=lambda x: (
            severity_order.get(x.get('severity', 'info'), 2),
            x.get('timestamp', ''), 
        ), reverse=True)
        
        print(f"[DEBUG] Generated {len(self.active_alerts)} active alerts")
        return self.active_alerts

    def create_notifications_interface(self):
        """Create the notifications interface"""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create the main frame for this section using styled frame
        self.frame = create_styled_frame(self.root, style='section')
        self.frame.pack(fill='both', expand=True)

        # Header frame
        header_frame = create_styled_frame(self.frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)

        # Back button
        back_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("back", "Back"),
            style='outline',
            command=self.back_callback
        )
        back_button.pack(side='left', padx=20, pady=20)

        # Title Label
        title_label = create_styled_label(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("notifications_alerts", "Notifications and Alerts"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Add refresh button
        refresh_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("refresh", "Refresh"),
            style='outline',
            command=self.refresh_notifications
        )
        refresh_button.pack(side='right', padx=20, pady=20)

        # Add settings button
        settings_button = create_styled_button(
            header_frame,
            text=self.LANGUAGES[self.current_language].get("settings", "Settings"),
            style='outline',
            command=self.show_notification_settings
        )
        settings_button.pack(side='right', padx=20, pady=20)

        # Area for displaying notifications
        # Use a scrollable frame for the notifications list
        self.notifications_scroll_frame = ctk.CTkScrollableFrame(self.frame, orientation='vertical')
        self.notifications_scroll_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Placeholder or initial message
        self.generate_alerts() # Generate alerts when interface is created
        self.display_notifications(self.active_alerts) # Display the generated alerts

    def display_notifications(self, alerts):
        """Display a list of alerts in the scrollable frame"""
        # Clear existing widgets in the scrollable frame
        for widget in self.notifications_scroll_frame.winfo_children():
            widget.destroy()

        if not alerts:
            no_alerts_label = create_styled_label(
                self.notifications_scroll_frame,
                text=self.LANGUAGES[self.current_language].get("no_new_notifications", "No new notifications."),
                style='body'
            )
            no_alerts_label.pack(pady=20)
            return

        # Display each alert
        for i, alert in enumerate(alerts):
            alert_frame = create_styled_frame(self.notifications_scroll_frame, style='card')
            alert_frame.pack(fill='x', padx=10, pady=5)

            # Get severity color and icon
            severity = alert.get('severity', 'info')
            severity_colors = {
                'critical': '#D32F2F',  # Red
                'warning': '#F57C00',   # Orange
                'info': '#1976D2'       # Blue
            }
            severity_icons = {
                'critical': '🚨',
                'warning': '⚠️',
                'info': 'ℹ️'
            }
            
            # Create header frame with icon and severity
            header_frame = create_styled_frame(alert_frame, style='card')
            header_frame.pack(fill='x', padx=5, pady=5)
            
            # Icon and severity
            icon_label = create_styled_label(
                header_frame,
                text=severity_icons.get(severity, 'ℹ️'),
                style='heading'
            )
            icon_label.pack(side='left', padx=5)
            
            severity_label = create_styled_label(
                header_frame,
                text=severity.upper(),
                style='small'
            )
            severity_label.configure(text_color=severity_colors.get(severity, COLORS['text']))
            severity_label.pack(side='right', padx=5)

            # Alert message
            alert_label = create_styled_label(
                alert_frame,
                text=alert.get('message', self.LANGUAGES[self.current_language].get("unknown_alert", "Unknown alert.")),
                style='body'
            )
            alert_label.pack(side='left', fill='x', expand=True, padx=10, pady=5)
            # Bind click event to the label
            alert_label.bind('<Button-1>', lambda e, a=alert: self.handle_alert_click(a))
            alert_label.configure(cursor="hand2") # Change cursor to indicate it's clickable

            # Timestamp
            timestamp_label = create_styled_label(
                alert_frame,
                text=alert.get('timestamp', ''),
                style='small'
            )
            timestamp_label.pack(side='right', padx=10, pady=5)

            # Add a separator between alerts
            if i < len(alerts) - 1:
                separator = ctk.CTkFrame(self.notifications_scroll_frame, height=1, fg_color=COLORS['border'])
                separator.pack(fill='x', padx=10, pady=2)

        # Ensure the scrollable frame updates
        self.notifications_scroll_frame.update_idletasks()

    def handle_alert_click(self, alert):
        """Handle click event on an alert"""
        print(f"[DEBUG] Alert clicked: {alert.get('type')}")
        alert_type = alert.get('type', '').lower()

        if alert_type == 'low_stock':
            # Navigate to Inventory Manager
            if 'manage_inventory' in self.callbacks:
                self.callbacks['manage_inventory']()
            else:
                print("[ERROR] Inventory Manager callback not available.")
        elif alert_type == 'upcoming_bill':
            # Navigate to Expenses and Bills
            if 'expenses_bills' in self.callbacks:
                self.callbacks['expenses_bills']()
            else:
                print("[ERROR] Expenses and Bills callback not available.")
        # Add handling for other alert types here in the future 

    def refresh_notifications(self):
        """Refresh notifications by regenerating alerts"""
        self.generate_alerts()
        self.display_notifications(self.active_alerts)

    def show_notification_settings(self):
        """Show notification settings dialog"""
        # Create settings dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.LANGUAGES[self.current_language].get("notification_settings", "Notification Settings"))
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = create_styled_frame(dialog, style='card')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = create_styled_label(
            main_frame,
            text=self.LANGUAGES[self.current_language].get("notification_settings", "Notification Settings"),
            style='heading'
        )
        title_label.pack(pady=(20, 30))
        
        # Low stock threshold setting
        threshold_frame = create_styled_frame(main_frame, style='card')
        threshold_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        threshold_label = create_styled_label(
            threshold_frame,
            text=self.LANGUAGES[self.current_language].get("low_stock_threshold", "Low Stock Threshold"),
            style='subheading'
        )
        threshold_label.pack(pady=(10, 5))
        
        threshold_entry = create_styled_entry(
            threshold_frame,
            placeholder_text=str(self.low_stock_threshold)
        )
        threshold_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        def save_threshold():
            try:
                new_threshold = int(threshold_entry.get())
                if new_threshold > 0:
                    self.low_stock_threshold = new_threshold
                    show_success(self.LANGUAGES[self.current_language].get("settings_saved", "Settings saved successfully"), self.current_language)
                    dialog.destroy()
                else:
                    show_error(self.LANGUAGES[self.current_language].get("invalid_threshold", "Please enter a valid threshold"), self.current_language)
            except ValueError:
                show_error(self.LANGUAGES[self.current_language].get("invalid_threshold", "Please enter a valid number"), self.current_language)
        
        save_button = create_styled_button(
            threshold_frame,
            text=self.LANGUAGES[self.current_language].get("save", "Save"),
            style='primary',
            command=save_threshold
        )
        save_button.pack(pady=(0, 10))
        
        # Close button
        close_button = create_styled_button(
            main_frame,
            text=self.LANGUAGES[self.current_language].get("close", "Close"),
            style='outline',
            command=dialog.destroy
        )
        close_button.pack(pady=20) 