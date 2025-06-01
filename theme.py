import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Color schemes
DARK_COLORS = {
    'primary': '#2196F3',  # Blue
    'primary_dark': '#1976D2',
    'primary_light': '#64B5F6',
    'secondary': '#757575',  # Gray
    'background': '#121212',
    'surface': '#1E1E1E',
    'text': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'error': '#D32F2F',
    'success': '#388E3C',
    'warning': '#F57C00',
    'info': '#1976D2',
    'card': '#1E1E1E',
    'border': '#333333',
    'sidebar': '#1A1A1A',
    'sidebar_text': '#FFFFFF',
    'sidebar_hover': '#2196F3',
    'card_gradient_start': '#1E1E1E',
    'card_gradient_end': '#2D2D2D',
    'sidebar_gradient_start': '#1A1A1A',
    'sidebar_gradient_end': '#2A2A2A',
    'login_card_gradient_start': '#1E1E1E',
    'login_card_gradient_end': '#2D2D2D',
    'shadow_color': '#000000'
}

LIGHT_COLORS = {
    'primary': '#2196F3',  # Blue
    'primary_dark': '#1976D2',
    'primary_light': '#64B5F6',
    'secondary': '#757575',  # Gray
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'text': '#000000',
    'text_secondary': '#666666',
    'error': '#D32F2F',
    'success': '#388E3C',
    'warning': '#F57C00',
    'info': '#1976D2',
    'card': '#FFFFFF',
    'border': '#E0E0E0',
    'sidebar': '#FFFFFF',
    'sidebar_text': '#000000',
    'sidebar_hover': '#E3F2FD',
    'card_gradient_start': '#FFFFFF',
    'card_gradient_end': '#F5F5F5',
    'sidebar_gradient_start': '#FFFFFF',
    'sidebar_gradient_end': '#F5F5F5',
    'login_card_gradient_start': '#FFFFFF',
    'login_card_gradient_end': '#F5F5F5',
    'shadow_color': '#CCCCCC'
}

# Font configurations
FONTS = {
    'heading': ('Helvetica', 24, 'bold'),
    'subheading': ('Helvetica', 18, 'bold'),
    'body': ('Helvetica', 12),
    'button': ('Helvetica', 12, 'bold'),
    'small': ('Helvetica', 10)
}

# Global variable to track current theme
current_theme = 'dark'
COLORS = DARK_COLORS

def toggle_theme():
    """Toggle between light and dark themes"""
    global current_theme, COLORS
    if current_theme == 'dark':
        current_theme = 'light'
        COLORS = LIGHT_COLORS
        ctk.set_appearance_mode("light")
    else:
        current_theme = 'dark'
        COLORS = DARK_COLORS
        ctk.set_appearance_mode("dark")
    return current_theme

def create_styled_frame(parent, style='card', **kwargs):
    """Create a styled frame with consistent padding and appearance"""
    frame = ctk.CTkFrame(parent, **kwargs)
    
    if style == 'card':
        frame.configure(
            fg_color=COLORS['card'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'section':
        frame.configure(
            fg_color=COLORS['background'],
            corner_radius=0
        )
    elif style == 'sidebar':
        frame.configure(
            fg_color=COLORS['sidebar'],
            corner_radius=0
        )
    elif style == 'quick_action_card':
        frame.configure(
            fg_color=COLORS['card'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'login_card':
        frame.configure(
            fg_color=COLORS['card'],
            corner_radius=20,
            border_width=1,
            border_color=COLORS['border']
        )
    
    return frame

def create_styled_button(parent, text, style='primary', **kwargs):
    """Create a styled button with consistent appearance"""
    button = ctk.CTkButton(parent, text=text, **kwargs)
    
    if style == 'primary':
        button.configure(
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=10
        )
    elif style == 'secondary':
        button.configure(
            fg_color=COLORS['secondary'],
            hover_color=COLORS['primary_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=10
        )
    elif style == 'outline':
        button.configure(
            fg_color='transparent',
            border_color=COLORS['primary'],
            border_width=2,
            text_color=COLORS['text'],
            hover_color=COLORS['primary'],
            font=FONTS['button'],
            corner_radius=10
        )
    elif style == 'error':
        button.configure(
            fg_color=COLORS['error'],
            hover_color=COLORS['error'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=10
        )
    elif style == 'sidebar':
        button.configure(
            fg_color='transparent',
            hover_color=COLORS['sidebar_hover'],
            text_color=COLORS['sidebar_text'],
            font=FONTS['button'],
            anchor='w',
            corner_radius=10
        )
    elif style == 'quick_action':
        button.configure(
            fg_color=COLORS['card'],
            hover_color=COLORS['primary'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
    
    return button

def create_styled_entry(parent, **kwargs):
    """Create a styled entry field with consistent appearance"""
    entry = ctk.CTkEntry(parent, **kwargs)
    entry.configure(
        fg_color=COLORS['surface'],
        border_color=COLORS['border'],
        text_color=COLORS['text'],
        font=FONTS['body']
    )
    return entry

def create_styled_label(parent, text, style='body', **kwargs):
    """Create a styled label with consistent appearance"""
    label = ctk.CTkLabel(parent, text=text, **kwargs)
    label.configure(
        text_color=COLORS['text'],
        font=FONTS[style]
    )
    return label

def create_styled_option_menu(parent, values, command=None, **kwargs):
    """Create a styled option menu with consistent appearance"""
    menu = ctk.CTkOptionMenu(parent, values=values, command=command, **kwargs)
    menu.configure(
        fg_color=COLORS['surface'],
        button_color=COLORS['primary'],
        button_hover_color=COLORS['primary_dark'],
        text_color=COLORS['text'],
        font=FONTS['body']
    )
    return menu

def create_styled_checkbox(parent, text, command=None, width=None, height=None):
    """Create a styled checkbox"""
    checkbox = ctk.CTkCheckBox(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        fg_color=COLORS['primary'],
        hover_color=COLORS['primary_dark'],
        text_color=COLORS['text'],
        font=FONTS['body']
    )
    return checkbox

def create_styled_switch(parent, text, command=None, width=None, height=None):
    """Create a styled switch"""
    switch = ctk.CTkSwitch(
        parent,
        text=text,
        command=command,
        width=width,
        height=height,
        fg_color=COLORS['primary'],
        progress_color=COLORS['primary_light'],
        text_color=COLORS['text'],
        font=FONTS['body']
    )
    return switch

def apply_theme(root):
    """Apply the theme to the entire application"""
    # Configure customtkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    # Configure ttk styles
    style = ttk.Style()
    style.configure(
        'TFrame',
        background=COLORS['background']
    )
    style.configure(
        'TLabel',
        background=COLORS['background'],
        foreground=COLORS['text'],
        font=FONTS['body']
    )
    style.configure(
        'TButton',
        background=COLORS['primary'],
        foreground=COLORS['text'],
        font=FONTS['button']
    )
    style.configure(
        'TEntry',
        fieldbackground=COLORS['surface'],
        foreground=COLORS['text'],
        font=FONTS['body']
    )
    
    # Configure root window
    if isinstance(root, ctk.CTk):
        root.configure(fg_color=COLORS['background'])
    else:
        root.configure(bg=COLORS['background']) 