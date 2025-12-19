import customtkinter as ctk
from tkinter import ttk, messagebox
from database import *

class DoctorViews:
    def show_doctors(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Doctors Management", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        add_button = ctk.CTkButton(
            title_frame,
            text="Add New Doctor",
            command=self.doctor_form,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_button.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
        info_frame = ctk.CTkFrame(self.main_content)
        info_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Manage doctors, their availability, and specialties",
            font=ctk.CTkFont(size=16)
        )
        info_label.grid(row=0, column=0, padx=15, pady=10)
        
        tree_frame = ctk.CTkFrame(self.main_content)
        tree_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)
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
        
        cols = ("id", "name", "specialty", "contact", "status", "appointments")
        self.doctors_tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=12
        )
        self.doctors_tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll_y.config(command=self.doctors_tree.yview)
        tree_scroll_x.config(command=self.doctors_tree.xview)
        
        column_widths = {
            "id": 60,
            "name": 220,
            "specialty": 180,
            "contact": 180,
            "status": 140,
            "appointments": 120
        }
        
        for c in cols:
            self.doctors_tree.heading(c, text=c.title())
            self.doctors_tree.column(c, width=column_widths.get(c, 140))
        
        self._refresh_doctors_tree()
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)
        
        left_button_frame = ctk.CTkFrame(button_frame)
        left_button_frame.grid(row=0, column=0, sticky="w")
        
        right_button_frame = ctk.CTkFrame(button_frame)
        right_button_frame.grid(row=0, column=1, sticky="e")
        
        def edit_doctor():
            sel = self.doctors_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a doctor first")
                return
            did = int(sel[0])
            self.doctor_form(did)
        
        def delete_doctor():
            sel = self.doctors_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a doctor first")
                return
            did = int(sel[0])
            
            doctor = db_fetchone("SELECT * FROM doctors WHERE id=?", (did,))
            if not doctor:
                return
            
            appointment_count = get_doctor_appointment_count(did)
            
            confirm_msg = f"Delete Dr. {doctor['name']} ({doctor['specialty']})?"
            if appointment_count > 0:
                confirm_msg += f"\n\nThis doctor has {appointment_count} appointment(s). Deleting will also remove all appointments."
            
            if messagebox.askyesno("Confirm Delete", confirm_msg):
                if remove_doctor(did):
                    messagebox.showinfo("Success", f"Doctor {doctor['name']} deleted successfully")
                    self._refresh_doctors_tree()
                else:
                    messagebox.showinfo("Cancelled", "Delete operation cancelled")
        
        def toggle_availability():
            sel = self.doctors_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a doctor first")
                return
            did = int(sel[0])
            
            doctor = db_fetchone("SELECT * FROM doctors WHERE id=?", (did,))
            if doctor:
                current_status = doctor["is_available"]
                new_status = 0 if current_status == 1 else 1
                status_text = "Available" if new_status == 1 else "Not Available"
                
                toggle_doctor_availability(did, new_status)
                messagebox.showinfo("Status Updated", f"Doctor is now {status_text}")
                self._refresh_doctors_tree()
        
        edit_button = ctk.CTkButton(
            left_button_frame,
            text="Edit Doctor",
            command=edit_doctor,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        edit_button.grid(row=0, column=0, padx=5, pady=5)
        
        toggle_button = ctk.CTkButton(
            left_button_frame,
            text="Toggle Availability",
            command=toggle_availability,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        toggle_button.grid(row=0, column=1, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            left_button_frame,
            text="Delete Doctor",
            command=delete_doctor,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.grid(row=0, column=2, padx=5, pady=5)
        
        refresh_button = ctk.CTkButton(
            right_button_frame,
            text="Refresh",
            command=self._refresh_doctors_tree,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        refresh_button.grid(row=0, column=0, padx=5, pady=5)

    def _refresh_doctors_tree(self):
        for i in self.doctors_tree.get_children():
            self.doctors_tree.delete(i)
        
        doctors = get_doctors()
        for d in doctors:
            status = "✅ Available" if d["is_available"] == 1 else "❌ Not Available"
            appointment_count = get_doctor_appointment_count(d["id"])
            
            self.doctors_tree.insert("", "end", iid=d["id"],
                                  values=(d["id"], d["name"], d["specialty"],
                                          d["contact"], status, appointment_count))
        
        self.doctors_tree.update()

    def doctor_form(self, doctor_id=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add Doctor" if doctor_id is None else "Edit Doctor")
        form_window.geometry("600x500")
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

        title_text = "Add New Doctor" if doctor_id is None else "Edit Doctor"
        title_label = ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Name field
        name_label = ctk.CTkLabel(fields_frame, text="Full Name:", font=ctk.CTkFont(size=14))
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))
        name_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        name_entry.grid(row=0, column=1, padx=10, pady=(15, 5))

        # Specialty field
        specialty_label = ctk.CTkLabel(fields_frame, text="Specialty:", font=ctk.CTkFont(size=14))
        specialty_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        specialties = [
            "General Dentistry",
            "Pediatric Dentistry",
            "Orthodontics",
            "Oral Surgery",
            "Periodontics",
            "Endodontics",
            "Prosthodontics",
            "Cosmetic Dentistry"
        ]
        
        specialty_var = ctk.StringVar(value=specialties[0])  
        specialty_combobox = ctk.CTkComboBox(fields_frame, values=specialties, 
                                             variable=specialty_var, width=350, height=40)
        specialty_combobox.grid(row=1, column=1, padx=10, pady=5)

        
        contact_label = ctk.CTkLabel(fields_frame, text="Contact Number:", font=ctk.CTkFont(size=14))
        contact_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        contact_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        contact_entry.grid(row=2, column=1, padx=10, pady=5)
        
        availability_label = ctk.CTkLabel(fields_frame, text="Availability:", font=ctk.CTkFont(size=14))
        availability_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        availability_var = ctk.BooleanVar(value=True)
        availability_checkbox = ctk.CTkCheckBox(fields_frame, text="Available for appointments",
                                                variable=availability_var, font=ctk.CTkFont(size=14))
        availability_checkbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        
        if doctor_id:
            doctor = db_fetchone("SELECT * FROM doctors WHERE id=?", (doctor_id,))
            if doctor:
                name_entry.insert(0, doctor["name"])
                specialty_var.set(doctor["specialty"])  
                contact_entry.insert(0, doctor["contact"])
                availability_var.set(doctor["is_available"] == 1)

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)

        def save_doctor():
            name = name_entry.get().strip()
            specialty = specialty_var.get().strip()  
            contact = contact_entry.get().strip()
            is_available = 1 if availability_var.get() else 0

            if not name:
                messagebox.showerror("Missing", "Doctor name is required")
                name_entry.focus()
                return
            if not specialty:
                messagebox.showerror("Missing", "Specialty is required")
                return
            if not contact:
                messagebox.showerror("Missing", "Contact number is required")
                contact_entry.focus()
                return

            try:
                if doctor_id:
                    update_doctor(doctor_id, name, specialty, contact, is_available)
                    messagebox.showinfo("Saved", "Doctor updated successfully")
                else:
                    add_doctor(name, specialty, contact, is_available)
                    messagebox.showinfo("Saved", "Doctor added successfully")
                
                form_window.destroy()
                self._refresh_doctors_tree()  # Refresh the doctors list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save doctor: {str(e)}")

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_doctor,
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
