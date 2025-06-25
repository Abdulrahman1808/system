import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, COLORS, FONTS
# Import data handling functions
from data_handler import load_data#, save_data
from collections import defaultdict # Import defaultdict
from datetime import datetime # Import datetime for date parsing
import statistics

class ReportingAnalytics:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback

        # Initialize data
        self.frame = None
        try:
            self.sales_data = load_data('sales_records.json') or []
            self.inventory_data = load_data('inventory.json') or []
            self.customer_data = load_data('customers.json') or []
        except Exception:
            self.sales_data = []
            self.inventory_data = []
            self.customer_data = []

        # Calculate dynamic thresholds based on data
        self.calculate_thresholds()

    def calculate_thresholds(self):
        """Calculate dynamic thresholds based on inventory data"""
        quantities = [int(item.get('quantity', 0)) for item in self.inventory_data if item.get('quantity')]
        if quantities:
            # Set low stock threshold to 25% of the median quantity
            self.low_stock_threshold = max(1, int(statistics.median(quantities) * 0.25))
        else:
            self.low_stock_threshold = 10  # Default fallback

    def create_reporting_analytics_interface(self):
        """Create the reporting and analytics interface"""
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
            text=self.LANGUAGES[self.current_language].get("reporting_analytics", "Reporting and Analytics"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # Area for reports
        self.reports_area_frame = ctk.CTkScrollableFrame(self.frame, orientation='vertical')
        self.reports_area_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Sales Summary Report
        generate_sales_button = create_styled_button(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("generate_sales_summary", "Generate Sales Summary"),
            style='primary',
            command=self.generate_sales_summary_report
        )
        generate_sales_button.pack(pady=10)

        self.sales_report_results_label = create_styled_label(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("click_generate_sales", "Click 'Generate Sales Summary' to see the report."),
            style='body'
        )
        self.sales_report_results_label.pack(pady=5)

        # Inventory Summary Report
        generate_inventory_button = create_styled_button(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("generate_inventory_summary", "Generate Inventory Summary"),
            style='primary',
            command=self.generate_inventory_summary_report
        )
        generate_inventory_button.pack(pady=10)

        self.inventory_report_results_label = create_styled_label(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("click_generate_inventory", "Click 'Generate Inventory Summary' to see the report."),
            style='body'
        )
        self.inventory_report_results_label.pack(pady=5)

        # Customer Summary Report
        generate_customer_button = create_styled_button(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("generate_customer_summary", "Generate Customer Summary"),
            style='primary',
            command=self.generate_customer_summary_report
        )
        generate_customer_button.pack(pady=10)

        self.customer_report_results_label = create_styled_label(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("click_generate_customer", "Click 'Generate Customer Summary' to see the report."),
            style='body'
        )
        self.customer_report_results_label.pack(pady=5)

        # Sales Over Time Report
        generate_sales_over_time_button = create_styled_button(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("generate_sales_over_time", "Generate Sales Over Time Report"),
            style='primary',
            command=self.generate_sales_over_time_report
        )
        generate_sales_over_time_button.pack(pady=10)

        self.sales_over_time_report_text = ctk.CTkTextbox(
            self.reports_area_frame,
            wrap='word',
            state='disabled',
            height=200
        )
        self.sales_over_time_report_text.pack(pady=5, fill='both', expand=True)

        # Top Selling Products Report
        generate_top_selling_button = create_styled_button(
            self.reports_area_frame,
            text=self.LANGUAGES[self.current_language].get("generate_top_selling", "Generate Top Selling Products Report"),
            style='primary',
            command=self.generate_top_selling_products_report
        )
        generate_top_selling_button.pack(pady=10)

        self.top_selling_report_text = ctk.CTkTextbox(
            self.reports_area_frame,
            wrap='word',
            state='disabled',
            height=200
        )
        self.top_selling_report_text.pack(pady=5, fill='both', expand=True)

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def generate_sales_summary_report(self):
        """Generates and displays a comprehensive sales summary report."""
        total_sales = 0
        total_items_sold = 0
        sales_by_category = defaultdict(float)
        sales_by_employee = defaultdict(float)

        for sale in self.sales_data:
            if 'items' in sale:
                for item in sale['items']:
                    try:
                        price = float(item.get('price', 0))
                        quantity = int(item.get('quantity', 0))
                        category = item.get('category', 'Uncategorized')
                        employee = sale.get('employee', 'Unknown')
                        
                        total_sales += price * quantity
                        total_items_sold += quantity
                        sales_by_category[category] += price * quantity
                        sales_by_employee[employee] += price * quantity
                    except (ValueError, TypeError):
                        continue

        # Calculate average sale value
        avg_sale = total_sales / len(self.sales_data) if self.sales_data else 0

        report_text = f"{self.get_bilingual('total_sales', 'Total Sales', 'المبيعات الكلية')}: ${total_sales:.2f}\n"
        report_text += f"{self.get_bilingual('total_items_sold', 'Total Items Sold', 'عدد الصنف المباع')}: {total_items_sold}\n"
        report_text += f"{self.get_bilingual('average_sale', 'Average Sale Value', 'متوسط قيمة المبيعات')}: ${avg_sale:.2f}\n\n"
        
        report_text += f"{self.get_bilingual('sales_by_category', 'Sales by Category', 'المبيعات بالفئة')}:\n"
        for category, amount in sorted(sales_by_category.items(), key=lambda x: x[1], reverse=True):
            report_text += f"{category}: ${amount:.2f}\n"

        report_text += f"\n{self.get_bilingual('sales_by_employee', 'Sales by Employee', 'المبيعات بالموظف')}:\n"
        for employee, amount in sorted(sales_by_employee.items(), key=lambda x: x[1], reverse=True):
            report_text += f"{employee}: ${amount:.2f}\n"

        self.sales_report_results_label.configure(text=report_text)

    def generate_inventory_summary_report(self):
        """Generates and displays a comprehensive inventory summary report."""
        total_items = 0
        total_value = 0
        low_stock_items = []
        out_of_stock_items = []
        category_summary = defaultdict(lambda: {'count': 0, 'value': 0})

        for item in self.inventory_data:
            try:
                quantity = int(item.get('quantity', 0))
                price = float(item.get('price', 0))
                category = item.get('category', 'Uncategorized')
                
                total_items += quantity
                total_value += quantity * price
                
                category_summary[category]['count'] += quantity
                category_summary[category]['value'] += quantity * price

                if quantity < self.low_stock_threshold:
                    low_stock_items.append(f"{item.get('name', 'Unnamed Item')} ({quantity})")
                if quantity == 0:
                    out_of_stock_items.append(item.get('name', 'Unnamed Item'))

            except (ValueError, TypeError):
                continue

        report_text = f"{self.get_bilingual('total_items', 'Total Items in Inventory', 'عدد الصنف في المخزن')}: {total_items}\n"
        report_text += f"{self.get_bilingual('total_value', 'Total Inventory Value', 'قيمة المخزن الكلية')}: ${total_value:.2f}\n\n"
        
        report_text += f"{self.get_bilingual('inventory_by_category', 'Inventory by Category', 'المخزن بالفئة')}:\n"
        for category, data in sorted(category_summary.items()):
            report_text += f"{category}: {data['count']} items (${data['value']:.2f})\n"

        if low_stock_items:
            report_text += f"\n{self.get_bilingual('low_stock_items', 'Low Stock Items', 'الصنف أقل من المخزن')}: {', '.join(low_stock_items)}"
        else:
            report_text += f"\n{self.get_bilingual('no_low_stock', 'No items below the low stock threshold of', 'لا توجد أصناف أقل من المخزن')}: {self.low_stock_threshold}."

        if out_of_stock_items:
            report_text += f"\n\n{self.get_bilingual('out_of_stock_items', 'Out of Stock Items', 'أصناف خارج المخزن')}: {', '.join(out_of_stock_items)}"

        self.inventory_report_results_label.configure(text=report_text)

    def generate_customer_summary_report(self):
        """Generates and displays a comprehensive customer summary report."""
        total_customers = len(self.customer_data)
        customers_by_category = defaultdict(int)
        total_purchases = 0
        customer_purchases = defaultdict(int)

        # Count purchases per customer
        for sale in self.sales_data:
            customer = sale.get('customer', 'Unknown')
            if 'items' in sale:
                for item in sale['items']:
                    try:
                        quantity = int(item.get('quantity', 0))
                        customer_purchases[customer] += quantity
                        total_purchases += quantity
                    except (ValueError, TypeError):
                        continue

        # Categorize customers based on purchase frequency
        for customer, purchases in customer_purchases.items():
            if purchases > 10:
                customers_by_category['frequent'] += 1
            elif purchases > 5:
                customers_by_category['regular'] += 1
            else:
                customers_by_category['occasional'] += 1

        report_text = f"{self.get_bilingual('total_customers', 'Total Number of Customers', 'عدد الزبائن الكلي')}: {total_customers}\n"
        report_text += f"{self.get_bilingual('total_purchases', 'Total Purchases', 'عدد المشتريات الكلية')}: {total_purchases}\n\n"
        
        report_text += f"{self.get_bilingual('customer_categories', 'Customer Categories', 'فئات الزبائن')}:\n"
        report_text += f"{self.get_bilingual('frequent_customers', 'Frequent Customers', 'الزبائن المستمرين')}: {customers_by_category['frequent']}\n"
        report_text += f"{self.get_bilingual('regular_customers', 'Regular Customers', 'الزبائن المنتظمين')}: {customers_by_category['regular']}\n"
        report_text += f"{self.get_bilingual('occasional_customers', 'Occasional Customers', 'الزبائن المنتظمين')}: {customers_by_category['occasional']}\n"

        self.customer_report_results_label.configure(text=report_text)

    def generate_sales_over_time_report(self):
        """Generates and displays sales aggregated by date with trends."""
        sales_by_date = defaultdict(float)
        daily_items = defaultdict(int)

        for sale in self.sales_data:
            sale_date_str = sale.get('date')
            if not sale_date_str:
                continue

            try:
                sale_date = datetime.fromisoformat(sale_date_str).strftime('%Y-%m-%d')
            except ValueError:
                continue

            if 'items' in sale:
                for item in sale['items']:
                    try:
                        price = float(item.get('price', 0))
                        quantity = int(item.get('quantity', 0))
                        sales_by_date[sale_date] += price * quantity
                        daily_items[sale_date] += quantity
                    except (ValueError, TypeError):
                        continue

        # Calculate trends
        dates = sorted(sales_by_date.keys())
        if len(dates) >= 2:
            first_date = dates[0]
            last_date = dates[-1]
            first_sales = sales_by_date[first_date]
            last_sales = sales_by_date[last_date]
            days_diff = (datetime.strptime(last_date, '%Y-%m-%d') - datetime.strptime(first_date, '%Y-%m-%d')).days
            if days_diff > 0:
                daily_growth = (last_sales - first_sales) / days_diff
            else:
                daily_growth = 0
        else:
            daily_growth = 0

        report_lines = [f"{self.get_bilingual('sales_by_date', 'Sales by Date', 'المبيعات بالتاريخ')}:"]
        for date in dates:
            report_lines.append(f"{date}: ${sales_by_date[date]:.2f} ({daily_items[date]} items)")

        if daily_growth != 0:
            report_lines.append(f"\n{self.get_bilingual('daily_growth', 'Average Daily Growth', 'متوسط النمو اليومي')}: ${daily_growth:.2f}")

        report_text = "\n".join(report_lines)

        self.sales_over_time_report_text.configure(state='normal')
        self.sales_over_time_report_text.delete('1.0', 'end')
        self.sales_over_time_report_text.insert('1.0', report_text)
        self.sales_over_time_report_text.configure(state='disabled')

    def generate_top_selling_products_report(self):
        """Generates and displays a report of top selling products with trends."""
        product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'dates': set()})
        
        for sale in self.sales_data:
            if 'items' in sale:
                for item in sale['items']:
                    try:
                        name = item.get('name', 'Unnamed Item')
                        price = float(item.get('price', 0))
                        quantity = int(item.get('quantity', 0))
                        date = sale.get('date', '')
                        
                        product_sales[name]['quantity'] += quantity
                        product_sales[name]['revenue'] += price * quantity
                        if date:
                            product_sales[name]['dates'].add(date.split()[0])  # Get just the date part
                    except (ValueError, TypeError):
                        continue

        # Sort products by quantity sold
        sorted_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['quantity'],
            reverse=True
        )

        report_lines = [f"{self.get_bilingual('top_selling_products', 'Top Selling Products', 'المبيعات الأعلى')}:"]
        
        for name, data in sorted_products:
            days_sold = len(data['dates'])
            avg_daily_sales = data['quantity'] / days_sold if days_sold > 0 else 0
            
            report_lines.append(f"\n{name}:")
            report_lines.append(f"  {self.get_bilingual('total_quantity', 'Total Quantity', 'الكمية الكلية')}: {data['quantity']}")
            report_lines.append(f"  {self.get_bilingual('total_revenue', 'Total Revenue', 'الإيرادات الكلية')}: ${data['revenue']:.2f}")
            report_lines.append(f"  {self.get_bilingual('days_sold', 'Days Sold', 'عدد الأيام')}: {days_sold}")
            report_lines.append(f"  {self.get_bilingual('avg_daily_sales', 'Average Daily Sales', 'متوسط المبيعات اليومية')}: {avg_daily_sales:.1f}")

        report_text = "\n".join(report_lines)

        self.top_selling_report_text.configure(state='normal')
        self.top_selling_report_text.delete('1.0', 'end')
        self.top_selling_report_text.insert('1.0', report_text)
        self.top_selling_report_text.configure(state='disabled')

    # We will add methods for generating other specific reports later
    # def generate_employee_report(self): pass