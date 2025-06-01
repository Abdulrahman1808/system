import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from ui_elements import show_error, show_success
from data_handler import insert_document, load_data

class AddWorker:
    def __init__(self, root, current_language, languages, create_main_menu_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.create_main_menu = create_main_menu_callback

    def add_worker(self):
        """Display the add worker interface"""
        self.clear_frame()
        self.worker_frame = ctk.CTkFrame(self.root, fg_color="#1f1f1f", corner_radius=10)
        self.worker_frame.pack(expand=True, fill='both', padx=20, pady=20)

        title_label = ctk.CTkLabel(self.worker_frame, text=self.LANGUAGES[self.current_language]["add_worker"],
                                   font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        title_label.pack(pady=10)

        form_frame = ctk.CTkFrame(self.worker_frame, fg_color="#1f1f1f")
        form_frame.pack(pady=10, fill='x')

        form_frame.grid_columnconfigure(0, weight=0, uniform="a")
        form_frame.grid_columnconfigure(1, weight=1, uniform="a")

        # Name
        name_label = ctk.CTkLabel(form_frame, text=self.LANGUAGES[self.current_language]["worker_name"] + " *",
                                  font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        name_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.name_entry = ctk.CTkEntry(form_frame, width=200, font=ctk.CTkFont(size=14), justify='left')
        self.name_entry.grid(row=0, column=1, sticky='w', padx=10, pady=10)

        # Position
        position_label = ctk.CTkLabel(form_frame, text=self.LANGUAGES[self.current_language]["position"] + " *",
                                     font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        position_label.grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.position_entry = ctk.CTkEntry(form_frame, width=200, font=ctk.CTkFont(size=14), justify='left')
        self.position_entry.grid(row=1, column=1, sticky='w', padx=10, pady=10)

        # Hire Date
        hire_date_label = ctk.CTkLabel(form_frame, text=self.LANGUAGES[self.current_language]["hire_date"] + " *",
                                       font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        hire_date_label.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.hire_date_entry = DateEntry(form_frame, width=12, background='red', foreground='white', borderwidth=2)
        self.hire_date_entry.grid(row=2, column=1, sticky='w', padx=10, pady=10)

        # Buttons
        buttons_frame = ctk.CTkFrame(self.worker_frame, fg_color="#1f1f1f")
        buttons_frame.pack(pady=10, fill='x')

        add_btn = ctk.CTkButton(buttons_frame, text=self.LANGUAGES[self.current_language]["add_worker"], command=self.save_worker,
                                font=ctk.CTkFont(size=16, weight="bold"))
        add_btn.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        back_btn = ctk.CTkButton(buttons_frame, text=self.LANGUAGES[self.current_language]["back"], command=self.create_main_menu,
                                 font=ctk.CTkFont(size=16, weight="bold"))
        back_btn.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    def save_worker(self):
        """Save the worker record"""
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        hire_date = self.hire_date_entry.get()

        if not all([name, position, hire_date]):
            show_error(self.LANGUAGES[self.current_language]["please_fill"], self.current_language)
            return

        worker_record = {
            "Name": name,
            "Position": position,
            "Hire Date": hire_date
        }

        inserted_id = insert_document("employees", worker_record)
        if inserted_id:
            show_success(self.LANGUAGES[self.current_language]["worker_added"].format(name), self.current_language)
            self.create_main_menu()
        else:
            show_error(self.LANGUAGES[self.current_language]["error"], self.current_language)

    def clear_frame(self):
        """Clear the current frame"""
        for widget in self.root.winfo_children():
            widget.destroy()
