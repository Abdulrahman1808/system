import customtkinter as ctk
import os
import json
from theme import create_styled_button, create_styled_entry, create_styled_frame, create_styled_label

class ManageStores:
    def __init__(self, root, LANGUAGES, back_callback):
        self.root = root
        self.LANGUAGES = LANGUAGES
        self.back_callback = back_callback
        self.stores_file = os.path.join("excel_data", "stores.json")
        self.stores = self.load_stores()

    def get_bilingual(self, key, default_en, default_ar):
        en = self.LANGUAGES['en'].get(key, default_en)
        ar = self.LANGUAGES['ar'].get(key, default_ar)
        return f"{en} / {ar}"

    def load_stores(self):
        if not os.path.exists(self.stores_file):
            return []
        with open(self.stores_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_stores(self):
        with open(self.stores_file, 'w', encoding='utf-8') as f:
            json.dump(self.stores, f, ensure_ascii=False, indent=2)

    def manage_stores(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        main_frame = create_styled_frame(self.root, style='section')
        main_frame.pack(fill='both', expand=True)

        header_frame = create_styled_frame(main_frame, style='card')
        header_frame.pack(fill='x', padx=20, pady=20)
        back_button = create_styled_button(
            header_frame,
            text=self.get_bilingual("back", "Back", "رجوع"),
            style='outline',
            command=self.back_callback
        )
        back_button.pack(side='left', padx=20, pady=20)
        title_label = create_styled_label(
            header_frame,
            text=self.get_bilingual("manage_stores", "Manage Stores", "إدارة المخازن"),
            style='heading'
        )
        title_label.pack(side='left', padx=20, pady=20)

        # قائمة المخازن
        stores_frame = create_styled_frame(main_frame, style='card')
        stores_frame.pack(fill='both', expand=True, padx=40, pady=20)
        for i, store in enumerate(self.stores):
            row = ctk.CTkFrame(stores_frame)
            row.pack(fill='x', pady=5, padx=10)
            name_label = create_styled_label(row, text=store['name'], style='body')
            name_label.pack(side='left', padx=10)
            edit_btn = create_styled_button(row, text=self.get_bilingual("edit", "Edit", "تعديل"), style='outline', width=80, command=lambda idx=i: self.edit_store_dialog(idx))
            edit_btn.pack(side='right', padx=5)
            del_btn = create_styled_button(row, text=self.get_bilingual("delete", "Delete", "حذف"), style='error', width=80, command=lambda idx=i: self.delete_store(idx))
            del_btn.pack(side='right', padx=5)

        # إضافة مخزن جديد
        add_frame = create_styled_frame(main_frame, style='card')
        add_frame.pack(fill='x', padx=40, pady=10)
        self.new_store_entry = create_styled_entry(add_frame)
        self.new_store_entry.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        add_btn = create_styled_button(add_frame, text=self.get_bilingual("add_store", "Add Store", "إضافة مخزن"), style='primary', command=self.add_store)
        add_btn.pack(side='right', padx=10, pady=10)

    def add_store(self):
        name = self.new_store_entry.get().strip()
        if not name:
            return
        new_id = max([s['id'] for s in self.stores], default=0) + 1
        self.stores.append({"id": new_id, "name": name})
        self.save_stores()
        self.manage_stores()

    def delete_store(self, idx):
        del self.stores[idx]
        self.save_stores()
        self.manage_stores()

    def edit_store_dialog(self, idx):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(self.get_bilingual("edit_store", "Edit Store", "تعديل المخزن"))
        dialog.geometry("350x150")
        entry = create_styled_entry(dialog)
        entry.insert(0, self.stores[idx]['name'])
        entry.pack(fill='x', padx=20, pady=20)
        save_btn = create_styled_button(dialog, text=self.get_bilingual("save", "Save", "حفظ"), style='primary', command=lambda: self.save_edit_store(idx, entry.get(), dialog))
        save_btn.pack(pady=10)

    def save_edit_store(self, idx, name, dialog):
        if not name.strip():
            return
        self.stores[idx]['name'] = name.strip()
        self.save_stores()
        dialog.destroy()
        self.manage_stores() 