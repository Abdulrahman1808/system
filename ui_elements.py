import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def show_error(message, title="Error"):
    """Show an error message box"""
    messagebox.showerror(title, message)

def apply_rtl(widget, is_rtl):
    """
    Apply RTL layout adjustments to a widget and its children.
    For example, adjust text alignment and packing/grid directions.
    """
    if is_rtl:
        # For labels and buttons, set anchor and justify to right
        if isinstance(widget, (tk.Label, ttk.Label, tk.Button, ttk.Button)):
            widget.configure(anchor="e", justify="right")
        # For frames, reverse packing of children if packed side left/right
        for child in widget.winfo_children():
            apply_rtl(child, is_rtl)
            # Adjust packing side if applicable
            pack_info = child.pack_info() if child.winfo_manager() == 'pack' else None
            if pack_info and 'side' in pack_info:
                side = pack_info['side']
                if side == 'left':
                    child.pack_configure(side='right')
                elif side == 'right':
                    child.pack_configure(side='left')
            # Adjust grid column if applicable
            grid_info = child.grid_info() if child.winfo_manager() == 'grid' else None
            if grid_info and 'column' in grid_info:
                # Reverse column index if parent has multiple columns
                # This requires knowledge of total columns, so skip here or handle in caller
                pass
    else:
        # Reset to default LTR alignment if needed
        if isinstance(widget, (tk.Label, ttk.Label, tk.Button, ttk.Button)):
            widget.configure(anchor="w", justify="left")
        for child in widget.winfo_children():
            apply_rtl(child, is_rtl)

def show_success(message, title="Success"):
    """Show a success message box"""
    messagebox.showinfo(title, message)

class AuthScreens:
    def __init__(self, root, languages, login_callback):
        self.root = root
        self.LANGUAGES = languages
        self.login = login_callback

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def create_login_screen(self):
        """Create the login screen"""
        self.clear_frame()
        self.login_frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(self.login_frame, 
                text=self.get_bilingual("hookah_heaven", "Hookah Heaven", "جنة الشيشة"), 
                bg='white', fg='red', font=("Arial", 24, "bold")
                ).grid(row=0, column=0, columnspan=2, pady=20)
                
        tk.Label(self.login_frame, 
                text=self.get_bilingual("username", "Username", "اسم المستخدم"), 
                bg='white', fg='red', font=("Arial", 14)
                ).grid(row=1, column=0, padx=10, pady=10, sticky='e')
                
        self.username_entry = tk.Entry(self.login_frame, font=("Arial", 14), 
                                     highlightbackground='red', highlightthickness=2)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self.login_frame, 
                text=self.get_bilingual("password", "Password", "كلمة المرور"), 
                bg='white', fg='red', font=("Arial", 14)
                ).grid(row=2, column=0, padx=10, pady=10, sticky='e')
                
        self.password_entry = tk.Entry(self.login_frame, show='*', font=("Arial", 14),
                                     highlightbackground='red', highlightthickness=2)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        
        login_btn = ttk.Button(self.login_frame, 
                             text=self.get_bilingual("login", "Login", "تسجيل الدخول"), 
                             command=self.process_login)
        login_btn.grid(row=3, columnspan=2, pady=20)
    
    def process_login(self):
        """Process login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        self.login(username, password)
        
    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()
