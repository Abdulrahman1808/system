import customtkinter as ctk
import tkinter.ttk as ttk
import tempfile
import os
import platform
from ui_elements import show_error, show_success

class BillHandler:
    def __init__(self, root, current_language, languages, create_main_menu_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.create_main_menu = create_main_menu_callback
        self.sales = []  # Will be updated when creating bill section

    def create_bill_section(self, sales_data):
        """Create the bill viewing section of the app"""
        self.sales = sales_data  # Update with current sales data

        self.clear_frame()
        self.bill_frame = ctk.CTkFrame(self.root, fg_color="#1f1f1f", corner_radius=10)
        self.bill_frame.pack(expand=True, fill='both', padx=20, pady=20)

        title_label = ctk.CTkLabel(self.bill_frame, text=self.LANGUAGES[self.current_language]["bill_section"],
                                   font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        title_label.pack(pady=10)

        # Apply RTL layout adjustments
        from ui_elements import apply_rtl
        is_rtl = self.current_language in ['ar', 'he', 'fa', 'ur']
        apply_rtl(self.bill_frame, is_rtl)

        self.bill_tree = ttk.Treeview(self.bill_frame, columns=("Product", "Quantity", "Price", "Total"), show="headings")
        self.bill_tree.heading("Product", text="Product")
        self.bill_tree.heading("Quantity", text="Quantity")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(fill='both', expand=True, pady=10)

        total_amount = 0
        for sale in self.sales:
            product = sale["Product"]
            quantity = sale["Quantity"]
            price = sale["Price"] / quantity if quantity != 0 else 0
            total = sale["Price"]
            total_amount += total
            self.bill_tree.insert("", "end", values=(product, quantity, f"${price:.2f}", f"${total:.2f}"))

        self.total_label = ctk.CTkLabel(self.bill_frame, text=f"Total Amount: ${total_amount:.2f}",
                                        font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.total_label.pack(pady=10)

        print_btn = ctk.CTkButton(self.bill_frame, text=self.LANGUAGES[self.current_language]["print"], command=self.print_bill)
        print_btn.pack(pady=10)

        back_btn = ctk.CTkButton(self.bill_frame, text=self.LANGUAGES[self.current_language]["back"], command=self.create_main_menu)
        back_btn.pack(pady=10)

    def print_bill(self):
        """Generate and print a bill"""
        bill_text = "Hookah Shop Bill\n\n"
        bill_text += f"{'Product':20} {'Qty':>5} {'Price':>10} {'Total':>10}\n"
        bill_text += "-" * 50 + "\n"
        total_amount = 0
        for sale in self.sales:
            product = sale["Product"]
            quantity = sale["Quantity"]
            price = sale["Price"] / quantity if quantity != 0 else 0
            total = sale["Price"]
            total_amount += total
            bill_text += f"{product:20} {quantity:>5} ${price:>9.2f} ${total:>9.2f}\n"
        bill_text += "-" * 50 + "\n"
        bill_text += f"{'Total Amount':>37} ${total_amount:>9.2f}\n"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
            f.write(bill_text)
            temp_file = f.name

        try:
            if platform.system() == "Windows":
                os.startfile(temp_file, "print")
            else:
                os.system(f"open {temp_file}")
        except Exception as e:
            show_error(f"Error printing bill: {str(e)}", self.current_language)

    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()
