# gui_views_services.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import *

class ServiceViews:
    def show_services(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Services & Prices", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        add_button = ctk.CTkButton(
            title_frame,
            text="Add Service",
            command=self.service_form,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_button.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
        tree_frame = ctk.CTkFrame(self.main_content)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        tree_container = ctk.CTkFrame(tree_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        tree_scroll_y = ttk.Scrollbar(tree_container)
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        
        tree_scroll_x = ttk.Scrollbar(tree_container, orient="horizontal")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.services_tree = ttk.Treeview(
            tree_container, 
            columns=("id","name","desc","price"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=12
        )
        self.services_tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll_y.config(command=self.services_tree.yview)
        tree_scroll_x.config(command=self.services_tree.xview)
        
        for c in ("id","name","desc","price"):
            self.services_tree.heading(c, text=c.title())
            if c == "price":
                self.services_tree.column(c, width=120)
            else:
                self.services_tree.column(c, width=180)
        
        for s in get_services():
            self.services_tree.insert("", "end", iid=s["id"],
                                  values=(s["id"], s["name"], s["description"], f"₱{s['price']:.2f}"))
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def edit_service():
            sel = self.services_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select service")
                return
            sid = int(sel[0])
            self.service_form(sid)
        
        def del_service():
            sel = self.services_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select service")
                return
            sid = int(sel[0])
            if messagebox.askyesno("Confirm", "Delete service?"):
                delete_service(sid)
                self.show_services()
        
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Service",
            command=edit_service,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        edit_button.grid(row=0, column=0, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            command=del_service,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.grid(row=0, column=1, padx=5, pady=5)
        
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.show_services,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        refresh_button.grid(row=0, column=2, padx=5, pady=5)

    def service_form(self, service_id=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add Service" if service_id is None else "Edit Service")
        form_window.geometry("600x450")
        form_window.transient(self)
        form_window.grab_set()
        
        form_window.update_idletasks()
        width = form_window.winfo_width()
        height = form_window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        form_window.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ctk.CTkFrame(form_window)
        main_frame.pack(padx=25, pady=25, fill="both", expand=True)
        
        title_text = "Add New Service" if service_id is None else "Edit Service"
        title_label = ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        name_label = ctk.CTkLabel(fields_frame, text="Service Name:", font=ctk.CTkFont(size=14))
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))
        name_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        name_entry.grid(row=0, column=1, padx=10, pady=(15, 5))
        
        desc_label = ctk.CTkLabel(fields_frame, text="Description:", font=ctk.CTkFont(size=14))
        desc_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        desc_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        desc_entry.grid(row=1, column=1, padx=10, pady=5)
        
        price_label = ctk.CTkLabel(fields_frame, text="Price (₱):", font=ctk.CTkFont(size=14))
        price_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        price_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        price_entry.grid(row=2, column=1, padx=10, pady=5)
        
        if service_id:
            service = db_fetchone("SELECT * FROM services WHERE id=?", (service_id,))
            if service:
                name_entry.insert(0, service["name"])
                desc_entry.insert(0, service["description"])
                price_entry.insert(0, str(service["price"]))
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def save_service():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            price_str = price_entry.get().strip()
            
            if not name:
                messagebox.showerror("Missing", "Service name is required")
                return
            
            try:
                price = float(price_str)
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except ValueError:
                messagebox.showerror("Invalid", "Price must be a valid number")
                return
            
            if service_id:
                update_service(service_id, name, desc, price)
                messagebox.showinfo("Saved", "Service updated successfully")
            else:
                add_service(name, desc, price)
                messagebox.showinfo("Saved", "Service added successfully")
            
            form_window.destroy()
            self.show_services()
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_service,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=form_window.destroy,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.pack(side="left", padx=10)