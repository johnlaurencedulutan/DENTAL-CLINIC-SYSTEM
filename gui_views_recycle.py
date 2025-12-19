# gui_views_recycle.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import get_recycle_items, restore_recycle_item, permanently_delete_recycle_item
import json

class RecycleViews:
    def show_recycle_bin(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Recycle Bin - Restore Deleted Records",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        items = get_recycle_items()
        
        if not items:
            no_items_label = ctk.CTkLabel(
                self.main_content,
                text="Recycle bin is empty",
                font=ctk.CTkFont(size=16)
            )
            no_items_label.grid(row=1, column=0, padx=15, pady=50)
            return
        
        tree_frame = ctk.CTkFrame(self.main_content)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        
        columns = ("id", "table_name", "deleted_at", "data_preview")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        tree.heading("id", text="ID")
        tree.heading("table_name", text="Type")
        tree.heading("deleted_at", text="Deleted At")
        tree.heading("data_preview", text="Preview")
        
        tree.column("id", width=50)
        tree.column("table_name", width=100)
        tree.column("deleted_at", width=150)
        tree.column("data_preview", width=300)
        
        for item in items:
            rid = item["id"]
            table = item["table_name"]
            deleted_at = item["deleted_at"][:19]  # trim timestamp
            
            # Parse and display data preview
            try:
                data = json.loads(item["data_json"])
                if table == "patients":
                    preview = f"{data.get('first_name', '')} {data.get('last_name', '')} (Age: {data.get('age', '')})"
                elif table == "doctors":
                    preview = f"{data.get('name', '')} - {data.get('specialty', '')}"
                elif table == "services":
                    preview = f"{data.get('name', '')} (${data.get('price', '')})"
                elif table == "appointments":
                    preview = f"Patient ID: {data.get('patient_id', '')}, Service ID: {data.get('service_id', '')}"
                else:
                    preview = str(data)[:50]
            except:
                preview = "(unable to parse)"
            
            tree.insert("", "end", iid=rid, values=(rid, table, deleted_at, preview))
        
        tree.pack(fill="both", expand=True)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=15)
        
        def restore_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Select", "Select a record to restore")
                return
            
            rid = int(selected[0])
            success, message = restore_recycle_item(rid)
            
            if success:
                messagebox.showinfo("Restored", message)
                self.show_recycle_bin()  # refresh
            else:
                messagebox.showerror("Restore Failed", message)
        
        def delete_permanently():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Select", "Select a record to permanently delete")
                return
            
            rid = int(selected[0])
            response = messagebox.askyesno(
                "Confirm Permanent Delete",
                "This will permanently delete the record.\nThis action cannot be undone."
            )
            
            if response:
                permanently_delete_recycle_item(rid)
                messagebox.showinfo("Deleted", "Record permanently deleted")
                self.show_recycle_bin()
        
        restore_button = ctk.CTkButton(
            button_frame,
            text="Restore Selected",
            command=restore_selected,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="green"
        )
        restore_button.pack(side="left", padx=10)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Permanently Delete",
            command=delete_permanently,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red"
        )
        delete_button.pack(side="left", padx=10)