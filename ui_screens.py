import customtkinter as ctk
from PIL import Image, ImageTk
import os
from theme import (
    COLORS, FONTS, create_styled_button,
    create_styled_entry, create_styled_frame,
    create_styled_label
)

class AuthScreens:
    def __init__(self, root, current_language, languages, login_callback, switch_language_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.login_callback = login_callback
        self.switch_language = switch_language_callback
        
    def create_login_screen(self):
        """Creates the login screen interface with the original preferred design."""
        # Clear current frame
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container (using background color from theme)
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['background'])
        main_frame.pack(fill='both', expand=True)

        # Login card (centered, updated to match quick action card style)
        login_card_frame = create_styled_frame(main_frame, style='quick_action_card')
        # Set updated dimensions and center it
        card_width = 380
        card_height = 500
        login_card_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, width=card_width, height=card_height)

        # Add an enhanced shadow effect for modern look
        login_card_frame.configure(border_width=1)
        shadow_frame = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS['shadow_color'],
            corner_radius=15,
            width=card_width+4,
            height=card_height+4
        )
        shadow_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        shadow_frame.lower()  # Place shadow behind the card

        # Title inside the card
        title_label = create_styled_label(
            login_card_frame,
            text=self.LANGUAGES[self.current_language].get("app_title", "Hookah Shop Manager"),
            style='subheading'
        )
        title_label.pack(pady=(30, 10))

        # Subtitle (updated for modern look)
        subtitle_label = create_styled_label(
            login_card_frame,
            text=self.LANGUAGES[self.current_language].get("login_subtitle", "Please login to continue"),
            style='body'
        )
        subtitle_label.pack(pady=(0, 30))

        # Username Label and Entry
        username_label = create_styled_label(
            login_card_frame,
            text=self.LANGUAGES[self.current_language].get("username", "Username"),
            style='subheading'
        )
        username_label.pack(pady=(10, 5), padx=40, anchor='w')

        self.username_entry = create_styled_entry(
            login_card_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("username_placeholder", "Enter your username"),
            width=card_width - 80,
            height=45
        )
        self.username_entry.pack(pady=(0, 20), padx=40)

        # Password Label and Entry
        password_label = create_styled_label(
            login_card_frame,
            text=self.LANGUAGES[self.current_language].get("password", "Password"),
            style='subheading'
        )
        password_label.pack(pady=(10, 5), padx=40, anchor='w')

        self.password_entry = create_styled_entry(
            login_card_frame,
            placeholder_text=self.LANGUAGES[self.current_language].get("password_placeholder", "Enter your password"),
            show="*",
            width=card_width - 80,
            height=45
        )
        self.password_entry.pack(pady=(0, 40), padx=40)

        # Login Button
        login_button = create_styled_button(
            login_card_frame,
            text=self.LANGUAGES[self.current_language].get("login", "Login"),
            style='primary',
            width=card_width - 80,
            height=50,
            command=self.login_callback
        )
        login_button.pack(pady=(0, 40), padx=40)

        # Language Switcher (positioned below the card)
        language_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        language_frame.pack(pady=20)

        en_button = create_styled_button(
            language_frame,
            text="English",
            style='outline',
            width=100,
            height=30,
            command=lambda: self.switch_language('en')
        )
        en_button.pack(side='left', padx=5)

        ar_button = create_styled_button(
            language_frame,
            text="العربية",
            style='outline',
            width=100,
            height=30,
            command=lambda: self.switch_language('ar')
        )
        ar_button.pack(side='left', padx=5)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event=None: self.login_callback())

    def process_login(self):
        """Process login attempt"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            self.login_callback(username, password)
        else:
            from ui_elements import show_error
            show_error(
                self.LANGUAGES[self.current_language].get("login_error", "Please enter both username and password"),
                self.current_language
            )

    def switch_language(self, language):
        """Switch the application language"""
        self.current_language = language
        self.create_login_screen()