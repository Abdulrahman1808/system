import tkinter as tk
import customtkinter as ctk
from ai_model import AIModel

class AIInteractionScreen:
    def __init__(self, root, current_language, languages, back_callback):
        self.root = root
        self.current_language = current_language
        self.LANGUAGES = languages
        self.back_callback = back_callback
        self.ai_model = AIModel()

    def create_ai_screen(self):
        self.clear_frame()
        self.frame = ctk.CTkFrame(self.root, fg_color="#1f1f1f", corner_radius=10)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        title_label = ctk.CTkLabel(self.frame, text="AI Assistant",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="red")
        title_label.pack(pady=10)

        self.chat_text = tk.Text(self.frame, height=20, state="disabled", bg="#2e2e2e", fg="white", font=("Arial", 12))
        self.chat_text.pack(padx=10, pady=10, fill="both", expand=True)

        self.entry_var = tk.StringVar()
        self.entry = ctk.CTkEntry(self.frame, textvariable=self.entry_var, font=ctk.CTkFont(size=14))
        self.entry.pack(padx=10, pady=10, fill="x")
        self.entry.bind("<Return>", self.process_user_input)

        button_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        button_frame.pack(pady=5)

        send_button = ctk.CTkButton(button_frame, text="Send", command=self.process_user_input)
        send_button.pack(side="left", padx=5)

        back_button = ctk.CTkButton(button_frame, text="Back", command=self.back_callback)
        back_button.pack(side="left", padx=5)

    def process_user_input(self, event=None):
        user_input = self.entry_var.get().strip()
        if not user_input:
            return
        self.append_chat("You: " + user_input)
        self.entry_var.set("")
        response = self.ai_model.respond_to_query(user_input)
        self.append_chat("AI: " + response)

    def append_chat(self, message):
        self.chat_text.configure(state="normal")
        self.chat_text.insert("end", message + "\n\n")
        self.chat_text.configure(state="disabled")
        self.chat_text.see("end")

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
