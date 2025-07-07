import customtkinter as ctk
# Import necessary styled functions from theme
from theme import create_styled_frame, create_styled_label, create_styled_button, COLORS, FONTS
# Import data handling functions
from data_handler import load_data#, save_data
from collections import defaultdict # Import defaultdict
from datetime import datetime, timedelta # Import datetime for date parsing
import statistics
import json

# Try to import matplotlib, if not available, use text-based charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Using text-based charts instead.")

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
        
        # Initialize dashboard data
        self.dashboard_data = {}
        self.update_dashboard_data()

    def calculate_thresholds(self):
        """Calculate dynamic thresholds based on inventory data"""
        quantities = [int(item.get('quantity', 0)) for item in self.inventory_data if item.get('quantity')]
        if quantities:
            # Set low stock threshold to 25% of the median quantity
            self.low_stock_threshold = max(1, int(statistics.median(quantities) * 0.25))
        else:
            self.low_stock_threshold = 10  # Default fallback

    def update_dashboard_data(self):
        """Update dashboard KPIs and metrics"""
        # Sales KPIs
        total_sales = sum(
            sum(float(item.get('price', 0)) * int(item.get('quantity', 0)) 
            for item in sale.get('items', [])
        ) for sale in self.sales_data
        )
        
        # Calculate daily sales for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        daily_sales = defaultdict(float)
        
        for sale in self.sales_data:
            try:
                sale_date = datetime.fromisoformat(sale.get('date', ''))
                if start_date <= sale_date <= end_date:
                    date_str = sale_date.strftime('%Y-%m-%d')
                    daily_sales[date_str] += sum(
                        float(item.get('price', 0)) * int(item.get('quantity', 0))
                        for item in sale.get('items', [])
                    )
            except (ValueError, TypeError):
                continue
        
        # Inventory KPIs
        total_inventory_value = sum(
            float(item.get('price', 0)) * int(item.get('quantity', 0))
            for item in self.inventory_data
        )
        
        low_stock_count = sum(
            1 for item in self.inventory_data
            if int(item.get('quantity', 0)) < self.low_stock_threshold
        )
        
        out_of_stock_count = sum(
            1 for item in self.inventory_data
            if int(item.get('quantity', 0)) == 0
        )
        
        # Customer KPIs
        total_customers = len(self.customer_data)
        active_customers = len(set(
            sale.get('customer', '') for sale in self.sales_data
            if sale.get('customer')
        ))
        
        # Additional KPIs
        total_products = len(self.inventory_data)
        avg_order_value = total_sales / len(self.sales_data) if self.sales_data else 0
        
        # Calculate profit margin (simplified - assuming 30% margin)
        estimated_profit = total_sales * 0.3
        
        # Store dashboard data
        self.dashboard_data = {
            'total_sales': total_sales,
            'daily_sales': dict(daily_sales),
            'total_inventory_value': total_inventory_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_customers': total_customers,
            'active_customers': active_customers,
            'avg_daily_sales': sum(daily_sales.values()) / 30 if daily_sales else 0,
            'total_products': total_products,
            'avg_order_value': avg_order_value,
            'estimated_profit': estimated_profit
        }

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

        # Refresh button
        refresh_button = create_styled_button(
            header_frame,
            text="🔄 Refresh",
            style='primary',
            command=self.refresh_dashboard
        )
        refresh_button.pack(side='right', padx=20, pady=20)

        # Create tab view for different sections
        self.tab_view = ctk.CTkTabview(self.frame)
        self.tab_view.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Dashboard Tab
        dashboard_tab = self.tab_view.add("📊 Dashboard")
        self.create_dashboard_tab(dashboard_tab)

        # Reports Tab
        reports_tab = self.tab_view.add("📋 Reports")
        self.create_reports_tab(reports_tab)

        # Analytics Tab
        analytics_tab = self.tab_view.add("📈 Analytics")
        self.create_analytics_tab(analytics_tab)

    def create_dashboard_tab(self, parent):
        """Create the main dashboard with KPIs and charts"""
        # Update dashboard data
        self.update_dashboard_data()
        
        # KPI Cards Frame
        kpi_frame = create_styled_frame(parent, style='card')
        kpi_frame.pack(fill='x', padx=20, pady=20)
        
        # KPI Cards
        kpi_cards = [
            {
                'title': 'Total Sales',
                'value': f"${self.dashboard_data['total_sales']:.2f}",
                'icon': '💰',
                'color': '#4CAF50'
            },
            {
                'title': 'Inventory Value',
                'value': f"${self.dashboard_data['total_inventory_value']:.2f}",
                'icon': '📦',
                'color': '#2196F3'
            },
            {
                'title': 'Low Stock Items',
                'value': f"{self.dashboard_data['low_stock_count']}",
                'icon': '⚠️',
                'color': '#FF9800'
            },
            {
                'title': 'Active Customers',
                'value': f"{self.dashboard_data['active_customers']}",
                'icon': '👥',
                'color': '#9C27B0'
            }
        ]
        
        # Create KPI cards in a grid
        for i, kpi in enumerate(kpi_cards):
            card_frame = create_styled_frame(kpi_frame, style='card')
            card_frame.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            # Icon and title
            icon_label = create_styled_label(
                card_frame,
                text=kpi['icon'],
                style='heading'
            )
            icon_label.pack(pady=(10, 5))
            
            title_label = create_styled_label(
                card_frame,
                text=kpi['title'],
                style='body'
            )
            title_label.pack()
            
            # Value with color
            value_label = create_styled_label(
                card_frame,
                text=kpi['value'],
                style='heading'
            )
            value_label.pack(pady=(5, 10))
            
            # Configure grid weights
            kpi_frame.grid_columnconfigure(i, weight=1)
        
        # Additional KPI Cards (Second Row)
        additional_kpi_cards = [
            {
                'title': 'Total Products',
                'value': f"{self.dashboard_data['total_products']}",
                'icon': '🏷️',
                'color': '#607D8B'
            },
            {
                'title': 'Avg Order Value',
                'value': f"${self.dashboard_data['avg_order_value']:.2f}",
                'icon': '📊',
                'color': '#E91E63'
            },
            {
                'title': 'Estimated Profit',
                'value': f"${self.dashboard_data['estimated_profit']:.2f}",
                'icon': '💎',
                'color': '#00BCD4'
            },
            {
                'title': 'Out of Stock',
                'value': f"{self.dashboard_data['out_of_stock_count']}",
                'icon': '❌',
                'color': '#F44336'
            }
        ]
        
        # Create additional KPI cards in second row
        for i, kpi in enumerate(additional_kpi_cards):
            card_frame = create_styled_frame(kpi_frame, style='card')
            card_frame.grid(row=1, column=i, padx=10, pady=10, sticky='ew')
            
            # Icon and title
            icon_label = create_styled_label(
                card_frame,
                text=kpi['icon'],
                style='heading'
            )
            icon_label.pack(pady=(10, 5))
            
            title_label = create_styled_label(
                card_frame,
                text=kpi['title'],
                style='body'
            )
            title_label.pack()
            
            # Value with color
            value_label = create_styled_label(
                card_frame,
                text=kpi['value'],
                style='heading'
            )
            value_label.pack(pady=(5, 10))
        
        # Charts Frame
        charts_frame = create_styled_frame(parent, style='card')
        charts_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create charts
        self.create_sales_chart(charts_frame)
        self.create_inventory_chart(charts_frame)

    def create_sales_chart(self, parent):
        """Create sales trend chart"""
        # Chart title
        chart_title = create_styled_label(
            parent,
            text="Sales Trend (Last 30 Days)",
            style='heading'
        )
        chart_title.pack(pady=(20, 10))
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            # Prepare data
            dates = list(self.dashboard_data['daily_sales'].keys())
            sales = list(self.dashboard_data['daily_sales'].values())
            
            if dates and sales:
                # Convert dates to datetime objects
                date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
                
                # Plot data
                ax.plot(date_objects, sales, marker='o', linewidth=2, markersize=6, color='#4CAF50')
                ax.fill_between(date_objects, sales, alpha=0.3, color='#4CAF50')
                
                # Formatting
                ax.set_title('Daily Sales', color='white', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date', color='white')
                ax.set_ylabel('Sales ($)', color='white')
                ax.tick_params(colors='white')
                ax.grid(True, alpha=0.3)
                
                # Format x-axis dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
                
                # Rotate x-axis labels
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            else:
                ax.text(0.5, 0.5, 'No sales data available', 
                       ha='center', va='center', transform=ax.transAxes, 
                       color='white', fontsize=12)
            
            # Create canvas and add to frame
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
        else:
            # Text-based chart alternative
            self.create_text_sales_chart(parent)

    def create_text_sales_chart(self, parent):
        """Create text-based sales chart when matplotlib is not available"""
        chart_frame = create_styled_frame(parent, style='card')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create text widget for chart
        chart_text = ctk.CTkTextbox(chart_frame, wrap='word', height=200)
        chart_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Generate text-based chart
        daily_sales = self.dashboard_data['daily_sales']
        if daily_sales:
            chart_content = "📊 SALES TREND (Last 30 Days)\n"
            chart_content += "=" * 50 + "\n\n"
            
            # Sort by date
            sorted_dates = sorted(daily_sales.keys())
            max_sales = max(daily_sales.values()) if daily_sales.values() else 1
            
            for date in sorted_dates:
                sales = daily_sales[date]
                # Create simple bar chart using text
                bar_length = int((sales / max_sales) * 30) if max_sales > 0 else 0
                bar = "█" * bar_length
                chart_content += f"{date}: ${sales:.2f} {bar}\n"
            
            chart_content += f"\n📈 Total Sales: ${sum(daily_sales.values()):.2f}\n"
            chart_content += f"📊 Average Daily Sales: ${sum(daily_sales.values())/len(daily_sales):.2f}\n"
        else:
            chart_content = "No sales data available for chart display."
        
        chart_text.insert('1.0', chart_content)
        chart_text.configure(state='disabled')

    def create_inventory_chart(self, parent):
        """Create inventory status chart"""
        # Chart title
        chart_title = create_styled_label(
            parent,
            text="Inventory Status",
            style='heading'
        )
        chart_title.pack(pady=(20, 10))
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            
            # Prepare data for pie chart
            categories = ['In Stock', 'Low Stock', 'Out of Stock']
            counts = [
                len([item for item in self.inventory_data if int(item.get('quantity', 0)) >= self.low_stock_threshold]),
                self.dashboard_data['low_stock_count'],
                self.dashboard_data['out_of_stock_count']
            ]
            colors = ['#4CAF50', '#FF9800', '#F44336']
            
            if sum(counts) > 0:
                # Create pie chart
                wedges, texts, autotexts = ax.pie(counts, labels=categories, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90)
                
                # Style the text
                for text in texts:
                    text.set_color('white')
                    text.set_fontsize(10)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(9)
            else:
                ax.text(0.5, 0.5, 'No inventory data available', 
                       ha='center', va='center', transform=ax.transAxes, 
                       color='white', fontsize=12)
            
            # Create canvas and add to frame
            canvas = FigureCanvasTkAgg(fig, parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)
        else:
            # Text-based chart alternative
            self.create_text_inventory_chart(parent)

    def create_text_inventory_chart(self, parent):
        """Create text-based inventory chart when matplotlib is not available"""
        chart_frame = create_styled_frame(parent, style='card')
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create text widget for chart
        chart_text = ctk.CTkTextbox(chart_frame, wrap='word', height=200)
        chart_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Generate text-based chart
        in_stock = len([item for item in self.inventory_data if int(item.get('quantity', 0)) >= self.low_stock_threshold])
        low_stock = self.dashboard_data['low_stock_count']
        out_of_stock = self.dashboard_data['out_of_stock_count']
        total = in_stock + low_stock + out_of_stock
        
        if total > 0:
            chart_content = "📦 INVENTORY STATUS\n"
            chart_content += "=" * 30 + "\n\n"
            
            # Calculate percentages
            in_stock_pct = (in_stock / total) * 100
            low_stock_pct = (low_stock / total) * 100
            out_of_stock_pct = (out_of_stock / total) * 100
            
            # Create text-based pie chart
            chart_content += f"🟢 In Stock: {in_stock} items ({in_stock_pct:.1f}%)\n"
            chart_content += "█" * int(in_stock_pct / 2) + "\n\n"
            
            chart_content += f"🟡 Low Stock: {low_stock} items ({low_stock_pct:.1f}%)\n"
            chart_content += "█" * int(low_stock_pct / 2) + "\n\n"
            
            chart_content += f"🔴 Out of Stock: {out_of_stock} items ({out_of_stock_pct:.1f}%)\n"
            chart_content += "█" * int(out_of_stock_pct / 2) + "\n\n"
            
            chart_content += f"📊 Total Items: {total}\n"
        else:
            chart_content = "No inventory data available for chart display."
        
        chart_text.insert('1.0', chart_content)
        chart_text.configure(state='disabled')

    def create_reports_tab(self, parent):
        """Create the reports tab with existing report functionality"""
        # Area for reports
        self.reports_area_frame = ctk.CTkScrollableFrame(parent, orientation='vertical')
        self.reports_area_frame.pack(fill='both', expand=True, padx=20, pady=20)

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

    def create_analytics_tab(self, parent):
        """Create advanced analytics tab with predictive insights"""
        # Analytics controls frame
        controls_frame = create_styled_frame(parent, style='card')
        controls_frame.pack(fill='x', padx=20, pady=20)
        
        # Analytics title
        analytics_title = create_styled_label(
            controls_frame,
            text="Advanced Analytics & Insights",
            style='heading'
        )
        analytics_title.pack(pady=10)
        
        # Analytics buttons
        buttons_frame = create_styled_frame(controls_frame, style='card')
        buttons_frame.pack(pady=10)
        
        # Trend Analysis button
        trend_button = create_styled_button(
            buttons_frame,
            text="📈 Sales Trend Analysis",
            style='primary',
            command=self.generate_trend_analysis
        )
        trend_button.pack(side='left', padx=10, pady=10)
        
        # Inventory Forecast button
        forecast_button = create_styled_button(
            buttons_frame,
            text="🔮 Inventory Forecast",
            style='primary',
            command=self.generate_inventory_forecast
        )
        forecast_button.pack(side='left', padx=10, pady=10)
        
        # Customer Insights button
        insights_button = create_styled_button(
            buttons_frame,
            text="👥 Customer Insights",
            style='primary',
            command=self.generate_customer_insights
        )
        insights_button.pack(side='left', padx=10, pady=10)
        
        # Analytics results area
        self.analytics_results_frame = create_styled_frame(parent, style='card')
        self.analytics_results_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Results text area
        self.analytics_results_text = ctk.CTkTextbox(
            self.analytics_results_frame,
            wrap='word',
            state='disabled',
            height=300
        )
        self.analytics_results_text.pack(fill='both', expand=True, padx=20, pady=20)

    def refresh_dashboard(self):
        """Refresh dashboard data and update display"""
        self.update_dashboard_data()
        # Recreate the dashboard tab
        dashboard_tab = self.tab_view.get("📊 Dashboard")
        for widget in dashboard_tab.winfo_children():
            widget.destroy()
        self.create_dashboard_tab(dashboard_tab)

    def generate_trend_analysis(self):
        """Generate advanced sales trend analysis"""
        # Calculate trends
        daily_sales = self.dashboard_data['daily_sales']
        if not daily_sales:
            self.show_analytics_result("No sales data available for trend analysis.")
            return
        
        # Calculate moving average
        dates = sorted(daily_sales.keys())
        sales_values = [daily_sales[date] for date in dates]
        
        # Simple moving average (7-day)
        moving_avg = []
        for i in range(len(sales_values)):
            start_idx = max(0, i - 6)
            avg = sum(sales_values[start_idx:i+1]) / (i - start_idx + 1)
            moving_avg.append(avg)
        
        # Calculate growth rate
        if len(sales_values) >= 2:
            growth_rate = ((sales_values[-1] - sales_values[0]) / sales_values[0]) * 100
        else:
            growth_rate = 0
        
        # Calculate volatility
        if len(sales_values) > 1:
            volatility = statistics.stdev(sales_values)
            avg_sales = sum(sales_values) / len(sales_values)
            volatility_percentage = (volatility / avg_sales) * 100 if avg_sales > 0 else 0
        else:
            volatility_percentage = 0
        
        # Generate insights
        analysis = f"📈 SALES TREND ANALYSIS\n{'='*50}\n\n"
        analysis += f"📊 Period: {len(dates)} days\n"
        analysis += f"💰 Total Sales: ${sum(sales_values):.2f}\n"
        analysis += f"📈 Growth Rate: {growth_rate:.1f}%\n"
        analysis += f"📊 Average Daily Sales: ${sum(sales_values)/len(sales_values):.2f}\n"
        analysis += f"📈 Volatility: {volatility_percentage:.1f}%\n\n"
        
        # Trend interpretation
        if growth_rate > 5:
            analysis += "🟢 POSITIVE TREND: Sales are growing steadily\n"
        elif growth_rate > -5:
            analysis += "🟡 STABLE TREND: Sales are relatively stable\n"
        else:
            analysis += "🔴 DECLINING TREND: Sales are decreasing\n"
        
        # Volatility interpretation
        if volatility_percentage < 20:
            analysis += "📊 LOW VOLATILITY: Consistent sales performance\n"
        elif volatility_percentage < 50:
            analysis += "📊 MODERATE VOLATILITY: Some sales fluctuations\n"
        else:
            analysis += "📊 HIGH VOLATILITY: Significant sales fluctuations\n"
        
        # Predictions
        if len(sales_values) >= 7:
            recent_avg = sum(sales_values[-7:]) / 7
            analysis += f"\n🔮 PREDICTIONS:\n"
            analysis += f"• Next 7 days estimated sales: ${recent_avg * 7:.2f}\n"
            if growth_rate > 0:
                analysis += f"• Projected monthly growth: {growth_rate * 0.3:.1f}%\n"
        
        # Recommendations
        analysis += f"\n💡 RECOMMENDATIONS:\n"
        if growth_rate < 0:
            analysis += "• Consider promotional campaigns\n"
            analysis += "• Review pricing strategy\n"
            analysis += "• Analyze customer feedback\n"
        elif growth_rate > 10:
            analysis += "• Excellent performance!\n"
            analysis += "• Consider expanding inventory\n"
            analysis += "• Plan for increased demand\n"
        
        if volatility_percentage > 50:
            analysis += "• Implement demand forecasting\n"
            analysis += "• Optimize inventory management\n"
        
        self.show_analytics_result(analysis)

    def generate_inventory_forecast(self):
        """Generate inventory forecasting insights"""
        # Analyze inventory patterns
        low_stock_items = [item for item in self.inventory_data 
                          if int(item.get('quantity', 0)) < self.low_stock_threshold]
        out_of_stock_items = [item for item in self.inventory_data 
                             if int(item.get('quantity', 0)) == 0]
        
        # Calculate inventory turnover (simplified)
        total_inventory_value = self.dashboard_data['total_inventory_value']
        total_sales = self.dashboard_data['total_sales']
        
        if total_inventory_value > 0:
            turnover_ratio = total_sales / total_inventory_value
        else:
            turnover_ratio = 0
        
        # Calculate inventory efficiency metrics
        total_items = sum(int(item.get('quantity', 0)) for item in self.inventory_data)
        avg_item_value = total_inventory_value / len(self.inventory_data) if self.inventory_data else 0
        
        # Analyze product categories
        category_analysis = defaultdict(lambda: {'count': 0, 'value': 0, 'quantity': 0})
        for item in self.inventory_data:
            category = item.get('category', 'Uncategorized')
            quantity = int(item.get('quantity', 0))
            price = float(item.get('price', 0))
            
            category_analysis[category]['count'] += 1
            category_analysis[category]['value'] += quantity * price
            category_analysis[category]['quantity'] += quantity
        
        # Generate forecast
        forecast = f"🔮 INVENTORY FORECAST\n{'='*50}\n\n"
        forecast += f"📦 Current Inventory Value: ${total_inventory_value:.2f}\n"
        forecast += f"🔄 Inventory Turnover Ratio: {turnover_ratio:.2f}\n"
        forecast += f"📊 Total Items: {total_items}\n"
        forecast += f"💰 Average Item Value: ${avg_item_value:.2f}\n"
        forecast += f"⚠️ Low Stock Items: {len(low_stock_items)}\n"
        forecast += f"❌ Out of Stock Items: {len(out_of_stock_items)}\n\n"
        
        # Category analysis
        forecast += f"📈 CATEGORY ANALYSIS:\n"
        for category, data in sorted(category_analysis.items(), key=lambda x: x[1]['value'], reverse=True):
            avg_category_value = data['value'] / data['count'] if data['count'] > 0 else 0
            forecast += f"• {category}: {data['count']} items, ${data['value']:.2f} value\n"
            forecast += f"  Avg value: ${avg_category_value:.2f}\n"
        
        # Forecast insights
        if turnover_ratio > 2:
            forecast += "\n🟢 HIGH TURNOVER: Inventory is moving quickly\n"
        elif turnover_ratio > 1:
            forecast += "\n🟡 MODERATE TURNOVER: Normal inventory flow\n"
        else:
            forecast += "\n🔴 LOW TURNOVER: Inventory may be overstocked\n"
        
        # Demand forecasting
        if len(self.sales_data) > 0:
            # Calculate demand based on sales history
            total_items_sold = sum(
                sum(int(item.get('quantity', 0)) for item in sale.get('items', []))
                for sale in self.sales_data
            )
            avg_daily_demand = total_items_sold / 30 if self.sales_data else 0
            
            forecast += f"\n🔮 DEMAND FORECASTING:\n"
            forecast += f"• Average daily demand: {avg_daily_demand:.1f} items\n"
            forecast += f"• Weekly demand projection: {avg_daily_demand * 7:.1f} items\n"
            forecast += f"• Monthly demand projection: {avg_daily_demand * 30:.1f} items\n"
            
            # Stock-out risk assessment
            if total_items > 0:
                days_of_inventory = total_items / avg_daily_demand if avg_daily_demand > 0 else 0
                forecast += f"• Days of inventory remaining: {days_of_inventory:.1f} days\n"
                
                if days_of_inventory < 7:
                    forecast += "⚠️ CRITICAL: Low inventory levels detected!\n"
                elif days_of_inventory < 14:
                    forecast += "🟡 WARNING: Inventory levels are moderate\n"
                else:
                    forecast += "🟢 GOOD: Adequate inventory levels\n"
        
        # Recommendations
        forecast += f"\n💡 RECOMMENDATIONS:\n"
        if len(out_of_stock_items) > 0:
            forecast += f"• Restock {len(out_of_stock_items)} out-of-stock items\n"
        if len(low_stock_items) > 0:
            forecast += f"• Monitor {len(low_stock_items)} low-stock items\n"
        if turnover_ratio < 1:
            forecast += "• Consider reducing inventory levels\n"
        if turnover_ratio > 3:
            forecast += "• Consider increasing inventory levels\n"
        
        # Category-specific recommendations
        for category, data in category_analysis.items():
            if data['quantity'] == 0:
                forecast += f"• Restock {category} category\n"
            elif data['quantity'] < 10:
                forecast += f"• Monitor {category} category stock levels\n"
        
        self.show_analytics_result(forecast)

    def generate_customer_insights(self):
        """Generate customer behavior insights"""
        # Analyze customer data
        total_customers = self.dashboard_data['total_customers']
        active_customers = self.dashboard_data['active_customers']
        
        # Calculate customer retention rate
        if total_customers > 0:
            retention_rate = (active_customers / total_customers) * 100
        else:
            retention_rate = 0
        
        # Analyze customer purchase patterns
        customer_purchases = defaultdict(int)
        customer_spending = defaultdict(float)
        customer_visits = defaultdict(int)
        
        for sale in self.sales_data:
            customer = sale.get('customer', 'Unknown')
            if 'items' in sale:
                sale_total = 0
                for item in sale['items']:
                    quantity = int(item.get('quantity', 0))
                    price = float(item.get('price', 0))
                    customer_purchases[customer] += quantity
                    sale_total += quantity * price
                customer_spending[customer] += sale_total
                customer_visits[customer] += 1
        
        # Categorize customers
        frequent_customers = sum(1 for purchases in customer_purchases.values() if purchases > 10)
        regular_customers = sum(1 for purchases in customer_purchases.values() if 5 <= purchases <= 10)
        occasional_customers = sum(1 for purchases in customer_purchases.values() if purchases < 5)
        
        # Calculate customer value metrics
        if customer_spending:
            avg_customer_value = sum(customer_spending.values()) / len(customer_spending)
            max_customer_value = max(customer_spending.values())
            min_customer_value = min(customer_spending.values())
        else:
            avg_customer_value = max_customer_value = min_customer_value = 0
        
        # Customer lifetime value analysis
        high_value_customers = sum(1 for spending in customer_spending.values() if spending > avg_customer_value * 2)
        medium_value_customers = sum(1 for spending in customer_spending.values() 
                                   if avg_customer_value * 0.5 <= spending <= avg_customer_value * 2)
        low_value_customers = sum(1 for spending in customer_spending.values() if spending < avg_customer_value * 0.5)
        
        # Generate insights
        insights = f"👥 CUSTOMER INSIGHTS\n{'='*50}\n\n"
        insights += f"👤 Total Customers: {total_customers}\n"
        insights += f"🔄 Active Customers: {active_customers}\n"
        insights += f"📊 Retention Rate: {retention_rate:.1f}%\n"
        insights += f"💰 Average Customer Value: ${avg_customer_value:.2f}\n"
        insights += f"📈 Highest Customer Value: ${max_customer_value:.2f}\n\n"
        
        insights += f"📈 CUSTOMER SEGMENTS:\n"
        insights += f"• Frequent Customers: {frequent_customers}\n"
        insights += f"• Regular Customers: {regular_customers}\n"
        insights += f"• Occasional Customers: {occasional_customers}\n\n"
        
        insights += f"💎 CUSTOMER VALUE SEGMENTS:\n"
        insights += f"• High Value Customers: {high_value_customers}\n"
        insights += f"• Medium Value Customers: {medium_value_customers}\n"
        insights += f"• Low Value Customers: {low_value_customers}\n\n"
        
        # Customer behavior insights
        if retention_rate > 70:
            insights += "🟢 EXCELLENT RETENTION: Strong customer loyalty\n"
        elif retention_rate > 50:
            insights += "🟡 GOOD RETENTION: Moderate customer loyalty\n"
        else:
            insights += "🔴 LOW RETENTION: Need to improve customer retention\n"
        
        # Purchase frequency analysis
        avg_visits = 0  # Initialize with default value
        if customer_visits:
            avg_visits = sum(customer_visits.values()) / len(customer_visits)
            insights += f"📊 Average Visits per Customer: {avg_visits:.1f}\n"
            
            if avg_visits > 3:
                insights += "🟢 HIGH ENGAGEMENT: Customers visit frequently\n"
            elif avg_visits > 1.5:
                insights += "🟡 MODERATE ENGAGEMENT: Regular customer visits\n"
            else:
                insights += "🔴 LOW ENGAGEMENT: Need to increase customer visits\n"
        
        # Customer acquisition analysis
        new_customers = total_customers - active_customers
        if total_customers > 0:
            acquisition_rate = (new_customers / total_customers) * 100
            insights += f"📈 Customer Acquisition Rate: {acquisition_rate:.1f}%\n"
        
        # Predictions
        if len(customer_spending) > 0:
            insights += f"\n🔮 CUSTOMER PREDICTIONS:\n"
            insights += f"• Projected monthly revenue: ${avg_customer_value * active_customers:.2f}\n"
            if retention_rate > 60:
                insights += f"• Strong customer base - stable revenue expected\n"
            else:
                insights += f"• Focus on retention to stabilize revenue\n"
        
        # Recommendations
        insights += f"\n💡 RECOMMENDATIONS:\n"
        if retention_rate < 50:
            insights += "• Implement loyalty program\n"
            insights += "• Improve customer service\n"
            insights += "• Offer personalized promotions\n"
        if frequent_customers < total_customers * 0.2:
            insights += "• Focus on customer engagement\n"
            insights += "• Develop VIP customer program\n"
        if high_value_customers < len(customer_spending) * 0.1:
            insights += "• Target high-value customer acquisition\n"
            insights += "• Premium service offerings\n"
        if customer_visits and avg_visits < 2:
            insights += "• Implement customer retention strategies\n"
            insights += "• Regular follow-up communications\n"
        
        self.show_analytics_result(insights)

    def show_analytics_result(self, text):
        """Display analytics results in the text area"""
        self.analytics_results_text.configure(state='normal')
        self.analytics_results_text.delete('1.0', 'end')
        self.analytics_results_text.insert('1.0', text)
        self.analytics_results_text.configure(state='disabled')

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