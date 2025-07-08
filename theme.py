import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math

# Enhanced Color schemes with modern gradients
DARK_COLORS = {
    'primary': '#6366F1',  # Modern Indigo
    'primary_dark': '#4F46E5',
    'primary_light': '#818CF8',
    'secondary': '#8B5CF6',  # Purple
    'secondary_dark': '#7C3AED',
    'secondary_light': '#A78BFA',
    'accent': '#06B6D4',  # Cyan
    'accent_dark': '#0891B2',
    'accent_light': '#22D3EE',
    'background': '#0F172A',  # Slate 900
    'surface': '#1E293B',  # Slate 800
    'surface_light': '#334155',  # Slate 700
    'text': '#F8FAFC',  # Slate 50
    'text_secondary': '#CBD5E1',  # Slate 300
    'text_muted': '#64748B',  # Slate 500
    'error': '#EF4444',  # Red 500
    'error_dark': '#DC2626',
    'success': '#10B981',  # Emerald 500
    'success_dark': '#059669',
    'warning': '#F59E0B',  # Amber 500
    'warning_dark': '#D97706',
    'info': '#3B82F6',  # Blue 500
    'info_dark': '#2563EB',
    'card': '#1E293B',  # Slate 800
    'card_hover': '#334155',  # Slate 700
    'border': '#475569',  # Slate 600
    'border_light': '#64748B',  # Slate 500
    'sidebar': '#0F172A',  # Slate 900
    'sidebar_hover': '#1E293B',  # Slate 800
    'sidebar_text': '#F8FAFC',  # Slate 50
    'gradient_start': '#0F172A',  # Slate 900
    'gradient_end': '#1E293B',  # Slate 800
    'card_gradient_start': '#1E293B',
    'card_gradient_end': '#334155',
    'sidebar_gradient_start': '#0F172A',
    'sidebar_gradient_end': '#1E293B',
    'login_card_gradient_start': '#1E293B',
    'login_card_gradient_end': '#334155',
    'shadow_color': '#000000',
    'glow': '#6366F1',
    'glass': '#1E293B',
    'glass_border': '#475569'
}

LIGHT_COLORS = {
    'primary': '#6366F1',  # Modern Indigo
    'primary_dark': '#4F46E5',
    'primary_light': '#818CF8',
    'secondary': '#8B5CF6',  # Purple
    'secondary_dark': '#7C3AED',
    'secondary_light': '#A78BFA',
    'accent': '#06B6D4',  # Cyan
    'accent_dark': '#0891B2',
    'accent_light': '#22D3EE',
    'background': '#F8FAFC',  # Slate 50
    'surface': '#FFFFFF',  # White
    'surface_light': '#F1F5F9',  # Slate 100
    'text': '#0F172A',  # Slate 900
    'text_secondary': '#475569',  # Slate 600
    'text_muted': '#64748B',  # Slate 500
    'error': '#EF4444',  # Red 500
    'error_dark': '#DC2626',
    'success': '#10B981',  # Emerald 500
    'success_dark': '#059669',
    'warning': '#F59E0B',  # Amber 500
    'warning_dark': '#D97706',
    'info': '#3B82F6',  # Blue 500
    'info_dark': '#2563EB',
    'card': '#FFFFFF',  # White
    'card_hover': '#F8FAFC',  # Slate 50
    'border': '#E2E8F0',  # Slate 200
    'border_light': '#CBD5E1',  # Slate 300
    'sidebar': '#FFFFFF',  # White
    'sidebar_hover': '#F1F5F9',  # Slate 100
    'sidebar_text': '#0F172A',  # Slate 900
    'gradient_start': '#F8FAFC',  # Slate 50
    'gradient_end': '#F1F5F9',  # Slate 100
    'card_gradient_start': '#FFFFFF',
    'card_gradient_end': '#F8FAFC',
    'sidebar_gradient_start': '#FFFFFF',
    'sidebar_gradient_end': '#F1F5F9',
    'login_card_gradient_start': '#FFFFFF',
    'login_card_gradient_end': '#F8FAFC',
    'shadow_color': '#E2E8F0',
    'glow': '#6366F1',
    'glass': '#FFFFFF',
    'glass_border': '#E2E8F0'
}

# Enhanced Font configurations with modern fonts
FONTS = {
    'heading': ('Segoe UI', 32, 'bold'),
    'subheading': ('Segoe UI', 24, 'bold'),
    'title': ('Segoe UI', 20, 'bold'),
    'body': ('Segoe UI', 14),
    'body_bold': ('Segoe UI', 14, 'bold'),
    'button': ('Segoe UI', 14, 'bold'),
    'button_small': ('Segoe UI', 12, 'bold'),
    'small': ('Segoe UI', 12),
    'caption': ('Segoe UI', 10),
    'code': ('Consolas', 12),
    'display': ('Segoe UI', 48, 'bold'),
    'display_small': ('Segoe UI', 36, 'bold')
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

def create_glass_frame(parent, **kwargs):
    """Create a glass-morphism frame with blur effect"""
    frame = ctk.CTkFrame(parent, **kwargs)
    frame.configure(
        fg_color=COLORS['glass'],
        corner_radius=20,
        border_width=1,
        border_color=COLORS['glass_border']
    )
    return frame

def create_styled_frame(parent, style='card', **kwargs):
    """Create a styled frame with consistent padding and appearance"""
    frame = ctk.CTkFrame(parent, **kwargs)
    
    if style == 'card':
        frame.configure(
            fg_color=COLORS['card'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'card_hover':
        frame.configure(
            fg_color=COLORS['card_hover'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'glass':
        frame.configure(
            fg_color=COLORS['glass'],
            corner_radius=20,
            border_width=1,
            border_color=COLORS['glass_border']
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
            corner_radius=20,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'login_card':
        frame.configure(
            fg_color=COLORS['card'],
            corner_radius=24,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'gradient_card':
        frame.configure(
            fg_color=COLORS['card_gradient_start'],
            corner_radius=20,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'success_card':
        frame.configure(
            fg_color=COLORS['success'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['success_dark']
        )
    elif style == 'warning_card':
        frame.configure(
            fg_color=COLORS['warning'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['warning_dark']
        )
    elif style == 'error_card':
        frame.configure(
            fg_color=COLORS['error'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['error_dark']
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
            corner_radius=12,
            border_width=0
        )
    elif style == 'secondary':
        button.configure(
            fg_color=COLORS['secondary'],
            hover_color=COLORS['secondary_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'accent':
        button.configure(
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'outline':
        button.configure(
            fg_color='transparent',
            border_color=COLORS['primary'],
            border_width=2,
            text_color=COLORS['primary'],
            hover_color=COLORS['primary'],
            font=FONTS['button'],
            corner_radius=12
        )
    elif style == 'ghost':
        button.configure(
            fg_color='transparent',
            hover_color=COLORS['surface_light'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'error':
        button.configure(
            fg_color=COLORS['error'],
            hover_color=COLORS['error_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'success':
        button.configure(
            fg_color=COLORS['success'],
            hover_color=COLORS['success_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'warning':
        button.configure(
            fg_color=COLORS['warning'],
            hover_color=COLORS['warning_dark'],
            text_color=COLORS['text'],
            font=FONTS['button'],
            corner_radius=12,
            border_width=0
        )
    elif style == 'sidebar':
        button.configure(
            fg_color='transparent',
            hover_color=COLORS['sidebar_hover'],
            text_color=COLORS['sidebar_text'],
            font=FONTS['button'],
            anchor='w',
            corner_radius=12,
            border_width=0
        )
    elif style == 'quick_action':
        button.configure(
            fg_color=COLORS['card'],
            hover_color=COLORS['primary'],
            text_color=COLORS['text'],
            font=FONTS['button_small'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['border']
        )
    elif style == 'icon_button':
        button.configure(
            fg_color='transparent',
            hover_color=COLORS['surface_light'],
            text_color=COLORS['text'],
            font=FONTS['button_small'],
            corner_radius=8,
            border_width=0
        )
    
    return button

def create_styled_entry(parent, **kwargs):
    """Create a styled entry field with consistent appearance"""
    entry = ctk.CTkEntry(parent, **kwargs)
    entry.configure(
        fg_color=COLORS['surface'],
        border_color=COLORS['border'],
        text_color=COLORS['text'],
        font=FONTS['body'],
        corner_radius=8,
        border_width=1
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

def create_gradient_label(parent, text, gradient_colors=None, **kwargs):
    """Create a label with gradient text effect"""
    if gradient_colors is None:
        gradient_colors = [COLORS['primary'], COLORS['secondary']]
    
    label = ctk.CTkLabel(parent, text=text, **kwargs)
    label.configure(
        text_color=gradient_colors[0],
        font=FONTS['heading']
    )
    return label

def create_styled_option_menu(parent, values, command=None, **kwargs):
    """Create a styled option menu with consistent appearance and scrollwheel support"""
    menu = ctk.CTkOptionMenu(parent, values=values, command=command, **kwargs)
    menu.configure(
        fg_color=COLORS['surface'],
        button_color=COLORS['primary'],
        button_hover_color=COLORS['primary_dark'],
        text_color=COLORS['text'],
        font=FONTS['body'],
        corner_radius=8
    )
    # Add scrollwheel support
    def on_mousewheel(event):
        current = menu.get()
        vals = menu.cget('values')
        if current not in vals:
            idx = 0
        else:
            idx = vals.index(current)
        if event.delta > 0:
            idx = (idx - 1) % len(vals)
        else:
            idx = (idx + 1) % len(vals)
        menu.set(vals[idx])
        if command:
            command(vals[idx])
    menu.bind('<MouseWheel>', on_mousewheel)
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
        font=FONTS['body'],
        corner_radius=4
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
        font=FONTS['body'],
        corner_radius=12
    )
    return switch

def create_progress_bar(parent, **kwargs):
    """Create a styled progress bar"""
    progress = ctk.CTkProgressBar(parent, **kwargs)
    progress.configure(
        fg_color=COLORS['surface'],
        progress_color=COLORS['primary'],
        corner_radius=8
    )
    return progress

def create_styled_slider(parent, **kwargs):
    """Create a styled slider"""
    slider = ctk.CTkSlider(parent, **kwargs)
    slider.configure(
        fg_color=COLORS['surface'],
        button_color=COLORS['primary'],
        button_hover_color=COLORS['primary_dark'],
        progress_color=COLORS['primary_light'],
        corner_radius=8
    )
    return slider

def create_styled_textbox(parent, **kwargs):
    """Create a styled text box"""
    textbox = ctk.CTkTextbox(parent, **kwargs)
    textbox.configure(
        fg_color=COLORS['surface'],
        text_color=COLORS['text'],
        font=FONTS['body'],
        corner_radius=8,
        border_width=1,
        border_color=COLORS['border']
    )
    return textbox

def create_styled_tabview(parent, **kwargs):
    """Create a styled tab view"""
    tabview = ctk.CTkTabview(parent, **kwargs)
    tabview.configure(
        fg_color=COLORS['card'],
        segmented_button_fg_color=COLORS['surface'],
        segmented_button_selected_color=COLORS['primary'],
        segmented_button_selected_hover_color=COLORS['primary_dark'],
        segmented_button_unselected_color=COLORS['surface'],
        segmented_button_unselected_hover_color=COLORS['surface_light'],
        text_color=COLORS['text'],
        font=FONTS['button']
    )
    return tabview

def create_animated_button(parent, text, command=None, animation_duration=200, **kwargs):
    """Create a button with hover animation"""
    button = create_styled_button(parent, text, **kwargs)
    
    if command:
        button.configure(command=command)
    
    # Add hover animation
    def on_enter(event):
        button.configure(corner_radius=16)
    
    def on_leave(event):
        button.configure(corner_radius=12)
    
    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)
    
    return button

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

def create_modern_card(parent, title=None, content=None, icon=None, **kwargs):
    """Create a modern card with title, content, and optional icon"""
    card = create_styled_frame(parent, style='card', **kwargs)
    
    if title:
        title_label = create_styled_label(card, title, style='title')
        title_label.pack(pady=(16, 8), padx=16)
    
    if content:
        content_label = create_styled_label(card, content, style='body')
        content_label.pack(pady=(0, 16), padx=16)
    
    return card

def create_status_indicator(parent, status='info', text=None, **kwargs):
    """Create a status indicator with different colors"""
    colors = {
        'info': COLORS['info'],
        'success': COLORS['success'],
        'warning': COLORS['warning'],
        'error': COLORS['error']
    }
    
    indicator = create_styled_frame(parent, style='card', **kwargs)
    indicator.configure(fg_color=colors.get(status, COLORS['info']))
    
    if text:
        text_label = create_styled_label(indicator, text, style='body')
        text_label.pack(pady=8, padx=12)
    
    return indicator 