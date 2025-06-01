import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, COLORS, FONTS

# Import data handling functions
from data_handler import load_data # Import load_data
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
                item_name = item.get('name', self.LANGUAGES[self.current_language].get("unnamed_item", "Unnamed Item"))
                if quantity <= self.low_stock_threshold:
                    alert_message = self.LANGUAGES[self.current_language].get(
                        "low_stock_alert",
                        f"Low stock for {item_name}. Only {quantity} left. (Threshold: {self.low_stock_threshold})"
                    ).format(item_name=item_name, quantity=quantity, threshold=self.low_stock_threshold)
                    low_stock_alerts.append({
                        'type': 'low_stock',
                        'message': alert_message,
                        'item_id': item.get('id'), # Include relevant IDs
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

    def generate_alerts(self):
        """Generate a combined list of all active alerts"""
        print("[DEBUG] Generating alerts...")
        low_stock = self.check_low_stock()
        upcoming_bills = self.check_upcoming_bills() # Check bills due in next 7 days

        self.active_alerts = low_stock + upcoming_bills
        # Sort alerts by timestamp if desired (optional)
        self.active_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
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

            # Alert message
            alert_label = create_styled_label(
                alert_frame,
                text=alert.get('message', self.LANGUAGES[self.current_language].get("unknown_alert", "Unknown alert.")),
                style='body'
            )
            alert_label.pack(side='left', fill='x', expand=True, padx=10, pady=10)
            # Bind click event to the label
            alert_label.bind('<Button-1>', lambda e, a=alert: self.handle_alert_click(a))
            alert_label.configure(cursor="hand2") # Change cursor to indicate it's clickable

            # Timestamp (optional)
            timestamp_label = create_styled_label(
                alert_frame,
                text=alert.get('timestamp', ''),
                style='caption'
            )
            timestamp_label.pack(side='right', padx=10, pady=10)

            # Add a separator between alerts (optional)
            if i < len(alerts) - 1:
                separator = ctk.CTkFrame(self.notifications_scroll_frame, height=1, fg_color=COLORS['border'])
                separator.pack(fill='x', padx=10, pady=0)

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