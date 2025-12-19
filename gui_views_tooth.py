# gui_views_tooth.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import json
from database import *
from models import *

class ToothViews:
    # ---------- Tooth Reference ----------
    def show_tooth_reference(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Tooth Name Reference", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        notebook = ttk.Notebook(self.main_content)
        notebook.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        
        primary_frame = ctk.CTkFrame(notebook)
        notebook.add(primary_frame, text="Primary (20 teeth)")
        
        primary_tree = ttk.Treeview(primary_frame, columns=("id","name"), show="headings", height=15)
        primary_tree.pack(fill="both", expand=True, padx=10, pady=10)
        primary_tree.heading("id", text="ID")
        primary_tree.heading("name", text="Name")
        primary_tree.column("id", width=100)
        primary_tree.column("name", width=300)
        
        for t in PRIMARY_TEETH:
            primary_tree.insert("", "end", values=(t["id"], t["name"]))
        
        permanent_frame = ctk.CTkFrame(notebook)
        notebook.add(permanent_frame, text="Permanent (32 teeth)")
        
        permanent_tree = ttk.Treeview(permanent_frame, columns=("id","name"), show="headings", height=15)
        permanent_tree.pack(fill="both", expand=True, padx=10, pady=10)
        permanent_tree.heading("id", text="ID")
        permanent_tree.heading("name", text="Name")
        permanent_tree.column("id", width=100)
        permanent_tree.column("name", width=300)
        
        for t in PERMANENT_TEETH:
            permanent_tree.insert("", "end", values=(t["id"], t["name"]))

    # ---------- Tooth records ----------
    def show_tooth_records_main(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Tooth Records (select patient)", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        select_frame = ctk.CTkFrame(self.main_content)
        select_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
        
        patients = get_patients()
        pmap = {f"{r['id']}: {r['last_name']}, {r['first_name']} (Age: {r['age']})": r["id"] for r in patients}
        
        self.patient_var = ctk.StringVar()
        patient_combobox = ctk.CTkComboBox(
            select_frame, 
            values=list(pmap.keys()),
            variable=self.patient_var,
            width=450,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        patient_combobox.grid(row=0, column=0, padx=15, pady=15)
        
        def open_selected():
            v = self.patient_var.get()
            if not v:
                messagebox.showinfo("Select", "Select a patient")
                return
            pid = pmap.get(v)
            self.show_tooth_editor(pid)
        
        open_button = ctk.CTkButton(
            select_frame,
            text="Open Tooth Records",
            command=open_selected,
            width=220,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        open_button.grid(row=0, column=1, padx=15, pady=15)

    def show_tooth_editor(self, patient_id):
        p = get_patient(patient_id)
        if not p:
            messagebox.showerror("Not found", "Patient not found")
            return
        
        form_window = ctk.CTkToplevel(self)
        form_window.title(f"Tooth Records - {p['first_name']} {p['last_name']} (Age: {p['age']})")
        form_window.geometry("1000x650")
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
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Tooth Records for {p['first_name']} {p['last_name']} (Age: {p['age']})",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        records = {}
        if p["tooth_records"]:
            try:
                records = json.loads(p["tooth_records"])
            except:
                records = {}
        
        age_appropriate_set = get_appropriate_tooth_set_for_age(p["age"])
        expected_count = get_tooth_count_for_age(p["age"])
        
        info_label = ctk.CTkLabel(
            main_frame,
            text=f"Expected teeth for age {p['age']}: {expected_count} teeth",
            font=ctk.CTkFont(size=16)
        )
        info_label.pack(pady=(0, 15))
        
        grid_frame = ctk.CTkFrame(main_frame)
        grid_frame.pack(fill="both", expand=True, pady=10)
        
        for i in range(8):
            grid_frame.grid_columnconfigure(i, weight=1)
        
        tooth_buttons = {}
        row = 0
        col = 0
        
        sorted_teeth = sorted(age_appropriate_set.keys())
        
        for tooth_id in sorted_teeth:
            tooth_info = records.get(tooth_id, {"status": "healthy", "notes": "", "present": True})
            status = tooth_info.get("status", "healthy")
            
            if status == "cavity":
                button_color = "yellow"
            elif status == "filling":
                button_color = "blue"
            elif status == "extracted":
                button_color = "red"
            else:
                button_color = "green"  

            
            btn = ctk.CTkButton(
                grid_frame,
                text=f"Tooth {tooth_id}\n{status}",
                command=lambda tid=tooth_id: self.edit_tooth_details(tid, patient_id, form_window),
                width=90,
                height=90,
                font=ctk.CTkFont(size=12),
                fg_color=button_color
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            tooth_buttons[tooth_id] = btn
            col += 1
            if col >= 8:
                col = 0
                row += 1
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def close_window():
            form_window.destroy()
            self.show_tooth_records_main()
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=close_window,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        close_button.pack()

    def edit_tooth_details(self, tooth_id, patient_id, parent_window):
        """Edit details for a specific tooth"""
        p = get_patient(patient_id)
        if not p:
            messagebox.showerror("Not found", "Patient not found")
            return
        
        # Get current tooth records
        records = {}
        if p["tooth_records"]:
            try:
                records = json.loads(p["tooth_records"])
            except:
                records = {}
        
        # Get tooth info or create default
        tooth_info = records.get(tooth_id, {"status": "healthy", "notes": "", "present": True})
        
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title(f"Edit Tooth {tooth_id}")
        dialog.geometry("400x450")
        dialog.transient(parent_window)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (parent_window.winfo_screenwidth() // 2) - (width // 2)
        y = (parent_window.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(padx=25, pady=25, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Edit Tooth {tooth_id}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Tooth status
        status_label = ctk.CTkLabel(main_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.pack(pady=(10, 5))
        
        # Limit status options to the supported set
        status_options = ["healthy", "cavity", "filling", "extracted"]
        status_var = ctk.StringVar(value=tooth_info.get("status", "healthy"))
        status_combo = ctk.CTkComboBox(main_frame, values=status_options, variable=status_var, width=300, height=35)
        status_combo.pack(pady=(0, 15))
        
        # Present checkbox
        present_var = ctk.BooleanVar(value=tooth_info.get("present", True))
        present_checkbox = ctk.CTkCheckBox(main_frame, text="Tooth is present", variable=present_var, font=ctk.CTkFont(size=14))
        present_checkbox.pack(pady=(0, 15))
        
        # Notes
        notes_label = ctk.CTkLabel(main_frame, text="Notes:", font=ctk.CTkFont(size=14))
        notes_label.pack(pady=(10, 5))
        
        # Slightly smaller notes box so buttons fit comfortably in the dialog
        notes_text = ctk.CTkTextbox(main_frame, width=260, height=80)
        notes_text.pack(pady=(0, 15))
        notes_text.insert("1.0", tooth_info.get("notes", ""))
        
        # Color preview
        color_frame = ctk.CTkFrame(main_frame, height=40)
        color_frame.pack(pady=(0, 20))
        
        def update_color_preview():
            status = status_var.get()
            color_map = {
                "healthy": "green",
                "cavity": "yellow",
                "filling": "blue",
                "extracted": "red",
            }
            preview_color = color_map.get(status, "green")
            preview_button.configure(fg_color=preview_color, text=f"Preview: {status}")
        
        preview_button = ctk.CTkButton(
            color_frame,
            text="Preview",
            command=update_color_preview,
            width=200,
            height=30
        )
        preview_button.pack()
        update_color_preview()  # Initial update
        
        def save_tooth_details():
            # Update tooth info
            tooth_info["status"] = status_var.get()
            tooth_info["present"] = present_var.get()
            tooth_info["notes"] = notes_text.get("1.0", "end").strip()
            
            # Update records
            records[tooth_id] = tooth_info
            
            # Save to database
            try:
                update_tooth_records(patient_id, json.dumps(records))
                messagebox.showinfo("Success", f"Tooth {tooth_id} updated successfully")
                dialog.destroy()
                
                # Refresh the tooth editor window
                parent_window.destroy()
                self.show_tooth_editor(patient_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_tooth_details,
            width=100,
            height=32,
            fg_color="#2a9d8f"
        )
        save_button.pack(side="left", padx=6)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=32,
            fg_color="#d00000"
        )
        cancel_button.pack(side="left", padx=6)
        
        # Update preview when status changes
        status_combo.configure(command=lambda e: update_color_preview())