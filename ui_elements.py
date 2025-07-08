import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from theme import (
    COLORS, FONTS, create_styled_button, create_styled_entry,
    create_styled_frame, create_styled_label, create_glass_frame,
    create_modern_card, create_gradient_label, create_animated_button
)

def show_error(message, title="Error"):
    """Show an error message box with modern styling"""
    messagebox.showerror(title, message)

def show_success(message, title="Success"):
    """Show a success message box with modern styling"""
    messagebox.showinfo(title, message)

def show_warning(message, title="Warning"):
    """Show a warning message box with modern styling"""
    messagebox.showwarning(title, message)

def show_info(message, title="Information"):
    """Show an info message box with modern styling"""
    messagebox.showinfo(title, message)

def create_modern_dialog(parent, title, message, buttons=None, callback=None):
    """Create a modern custom dialog"""
    if buttons is None:
        buttons = ["OK"]
    
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    
    # Create glass frame
    main_frame = create_glass_frame(dialog)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Title
    title_label = create_gradient_label(
        main_frame,
        text=title,
        gradient_colors=[COLORS['primary'], COLORS['secondary']]
    )
    title_label.pack(pady=(20, 10))
    
    # Message
    message_label = create_styled_label(
        main_frame,
        text=message,
        style='body'
    )
    message_label.pack(pady=10, padx=20)
    
    # Buttons frame
    buttons_frame = create_styled_frame(main_frame, style='section')
    buttons_frame.pack(side='bottom', fill='x', pady=20)
    
    # Create buttons
    for i, button_text in enumerate(buttons):
        button = create_animated_button(
            buttons_frame,
            text=button_text,
            style='primary' if i == 0 else 'outline',
            command=lambda b=button_text: handle_dialog_button(dialog, b, callback)
        )
        button.pack(side='right' if i == 0 else 'left', padx=10)
    
    return dialog

def handle_dialog_button(dialog, button_text, callback):
    """Handle dialog button clicks"""
    dialog.destroy()
    if callback:
        callback(button_text)

def create_loading_screen(parent, message="Loading..."):
    """Create a modern loading screen"""
    loading_window = ctk.CTkToplevel(parent)
    loading_window.title("Loading")
    loading_window.geometry("300x150")
    loading_window.resizable(False, False)
    loading_window.transient(parent)
    loading_window.grab_set()
    
    # Center the window
    loading_window.update_idletasks()
    x = (loading_window.winfo_screenwidth() // 2) - (300 // 2)
    y = (loading_window.winfo_screenheight() // 2) - (150 // 2)
    loading_window.geometry(f"300x150+{x}+{y}")
    
    # Create glass frame
    main_frame = create_glass_frame(loading_window)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Loading message
    message_label = create_styled_label(
        main_frame,
        text=message,
        style='title'
    )
    message_label.pack(pady=20)
    
    # Progress bar
    progress_bar = ctk.CTkProgressBar(main_frame)
    progress_bar.pack(pady=20)
    progress_bar.set(0)
    progress_bar.start()
    
    return loading_window

def create_modern_tooltip(widget, text):
    """Create a modern tooltip for a widget"""
    tooltip = None
    
    def show_tooltip(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        tooltip = ctk.CTkToplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        label = create_styled_label(
            tooltip,
            text=text,
            style='small'
        )
        label.pack(padx=10, pady=5)
        
        # Add glass effect
        tooltip.configure(fg_color=COLORS['glass'])
    
    def hide_tooltip(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind('<Enter>', show_tooltip)
    widget.bind('<Leave>', hide_tooltip)

def create_modern_notification(parent, title, message, notification_type="info", duration=3000):
    """Create a modern notification toast"""
    notification = ctk.CTkToplevel(parent)
    notification.title("")
    notification.geometry("350x80")
    notification.resizable(False, False)
    notification.overrideredirect(True)
    notification.attributes('-topmost', True)
    
    # Position in top-right corner
    x = parent.winfo_screenwidth() - 370
    y = 20
    notification.geometry(f"350x80+{x}+{y}")
    
    # Set notification color based on type
    colors = {
        "info": COLORS['info'],
        "success": COLORS['success'],
        "warning": COLORS['warning'],
        "error": COLORS['error']
    }
    
    # Create notification frame
    notification_frame = create_styled_frame(notification, style='card')
    notification_frame.pack(fill='both', expand=True, padx=10, pady=10)
    notification_frame.configure(fg_color=colors.get(notification_type, COLORS['info']))
    
    # Title
    title_label = create_styled_label(
        notification_frame,
        text=title,
        style='body_bold'
    )
    title_label.pack(anchor='w', padx=15, pady=(10, 5))
    
    # Message
    message_label = create_styled_label(
        notification_frame,
        text=message,
        style='small'
    )
    message_label.pack(anchor='w', padx=15, pady=(0, 10))
    
    # Auto-close after duration
    parent.after(duration, notification.destroy)
    
    return notification

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

class ModernAuthScreens:
    def __init__(self, root, languages, login_callback):
        self.root = root
        self.LANGUAGES = languages
        self.login = login_callback

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def create_login_screen(self):
        """Create a modern login screen with glass morphism"""
        self.clear_frame()
        
        # Create main container with gradient background
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)
        
        # Create glass login card
        login_card = create_glass_frame(main_frame)
        login_card.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo/Title with gradient
        title_label = create_gradient_label(
            login_card,
            text=self.get_bilingual("hookah_heaven", "Hookah Heaven", "جنة الشيشة"),
            gradient_colors=[COLORS['primary'], COLORS['secondary']]
        )
        title_label.pack(pady=(30, 20))
        
        # Subtitle
        subtitle_label = create_styled_label(
            login_card,
            text=self.get_bilingual("login_subtitle", "Sign in to your account", "سجل دخولك إلى حسابك"),
            style='body'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username field
        username_frame = create_styled_frame(login_card, style='section')
        username_frame.pack(fill='x', padx=30, pady=10)
        
        username_label = create_styled_label(
            username_frame,
            text=self.get_bilingual("username", "Username", "اسم المستخدم"),
            style='body_bold'
        )
        username_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = create_styled_entry(
            username_frame,
            placeholder_text=self.get_bilingual("enter_username", "Enter username", "أدخل اسم المستخدم")
        )
        self.username_entry.pack(fill='x', pady=(0, 10))
        
        # Password field
        password_frame = create_styled_frame(login_card, style='section')
        password_frame.pack(fill='x', padx=30, pady=10)
        
        password_label = create_styled_label(
            password_frame,
            text=self.get_bilingual("password", "Password", "كلمة المرور"),
            style='body_bold'
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = create_styled_entry(
            password_frame,
            placeholder_text=self.get_bilingual("enter_password", "Enter password", "أدخل كلمة المرور"),
            show='*'
        )
        self.password_entry.pack(fill='x', pady=(0, 20))
        
        # Login button
        login_button = create_animated_button(
            login_card,
            text=self.get_bilingual("login", "Login", "تسجيل الدخول"),
            style='primary',
            command=self.process_login,
            height=45
        )
        login_button.pack(fill='x', padx=30, pady=(0, 30))
        
        # Add tooltips
        create_modern_tooltip(self.username_entry, self.get_bilingual("username_tooltip", "Enter your username", "أدخل اسم المستخدم"))
        create_modern_tooltip(self.password_entry, self.get_bilingual("password_tooltip", "Enter your password", "أدخل كلمة المرور"))
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.process_login())
        
    def process_login(self):
        """Process login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            create_modern_notification(
                self.root,
                self.get_bilingual("error", "Error", "خطأ"),
                self.get_bilingual("fill_fields", "Please fill all fields", "يرجى ملء جميع الحقول"),
                "error"
            )
            return
        
        self.login(username, password)
        
    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()

class ModernFormBuilder:
    """Helper class for building modern forms"""
    
    def __init__(self, parent):
        self.parent = parent
        self.fields = {}
    
    def add_text_field(self, label, key, placeholder="", required=False):
        """Add a text field to the form"""
        frame = create_styled_frame(self.parent, style='section')
        frame.pack(fill='x', pady=10)
        
        label_widget = create_styled_label(
            frame,
            text=label,
            style='body_bold'
        )
        label_widget.pack(anchor='w', pady=(0, 5))
        
        entry = create_styled_entry(
            frame,
            placeholder_text=placeholder
        )
        entry.pack(fill='x')
        
        self.fields[key] = entry
        return entry
    
    def add_dropdown(self, label, key, options, placeholder="Select option"):
        """Add a dropdown field to the form"""
        frame = create_styled_frame(self.parent, style='section')
        frame.pack(fill='x', pady=10)
        
        label_widget = create_styled_label(
            frame,
            text=label,
            style='body_bold'
        )
        label_widget.pack(anchor='w', pady=(0, 5))
        
        dropdown = ctk.CTkOptionMenu(
            frame,
            values=options,
            placeholder_text=placeholder
        )
        dropdown.pack(fill='x')
        
        self.fields[key] = dropdown
        return dropdown
    
    def add_checkbox(self, label, key, text):
        """Add a checkbox field to the form"""
        frame = create_styled_frame(self.parent, style='section')
        frame.pack(fill='x', pady=10)
        
        checkbox = ctk.CTkCheckBox(
            frame,
            text=text,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark']
        )
        checkbox.pack(anchor='w')
        
        self.fields[key] = checkbox
        return checkbox
    
    def get_values(self):
        """Get all form values"""
        values = {}
        for key, widget in self.fields.items():
            if isinstance(widget, ctk.CTkEntry):
                values[key] = widget.get()
            elif isinstance(widget, ctk.CTkOptionMenu):
                values[key] = widget.get()
            elif isinstance(widget, ctk.CTkCheckBox):
                values[key] = widget.get()
        return values
    
    def clear_form(self):
        """Clear all form fields"""
        for widget in self.fields.values():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, 'end')
            elif isinstance(widget, ctk.CTkOptionMenu):
                widget.set("")
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.deselect()
