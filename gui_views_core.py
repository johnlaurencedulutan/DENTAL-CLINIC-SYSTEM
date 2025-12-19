# gui_views_core.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from database import *
from models import *

class PatientViews:
    def show_patients(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Patients", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        add_button = ctk.CTkButton(
            title_frame,
            text="Add Patient",
            command=self.patient_form,
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
        
        cols = ("id","name","age","type","contact","teeth_count")
        self.patients_tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=15
        )
        self.patients_tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll_y.config(command=self.patients_tree.yview)
        tree_scroll_x.config(command=self.patients_tree.xview)
        
        for c in cols:
            self.patients_tree.heading(c, text=c.title().replace("_", " "))
            if c == "teeth_count":
                self.patients_tree.column(c, width=120)
            else:
                self.patients_tree.column(c, width=140)
        
        # Ensure numeric-id ordering to avoid unexpected display order
        rows = list(get_patients())
        try:
            rows = sorted(rows, key=lambda r: int(r['id']))
        except Exception:
            pass

        for row in rows:
            name = f"{row['last_name']}, {row['first_name']}"

           
            expected_count = get_tooth_count_for_age(row["age"])
            tooth_count = expected_count

            if row["tooth_records"]:
                try:
                    records = json.loads(row["tooth_records"])
                   
                    if len(records) == expected_count:
                        tooth_count = len(records)
                except:
                    tooth_count = expected_count

            self.patients_tree.insert("", "end", iid=row["id"],
                                  values=(row["id"], name, row["age"], row["type"], row["contact"], tooth_count))
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)
        
        def on_view():
            sel = self.patients_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a patient first")
                return
            pid = int(sel[0])
            self.patient_form(pid)
        
        def on_delete():
            sel = self.patients_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a patient first")
                return
            pid = int(sel[0])
            if messagebox.askyesno("Confirm", "Delete patient?"):
                delete_patient(pid)
                self.show_patients()
        
        def on_view_appointments():
            sel = self.patients_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a patient first")
                return
            pid = int(sel[0])
            self.show_patient_appointments(pid)
        
        def on_finish_patient():
            sel = self.patients_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select a patient first")
                return
            pid = int(sel[0])
            self.mark_patient_complete(pid)
        
        view_button = ctk.CTkButton(
            button_frame,
            text="View / Edit",
            command=on_view,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        view_button.grid(row=0, column=0, padx=5, pady=5)
        
        appointments_button = ctk.CTkButton(
            button_frame,
            text="View Appointments",
            command=on_view_appointments,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        appointments_button.grid(row=0, column=1, padx=5, pady=5)
        
        finish_button = ctk.CTkButton(
            button_frame,
            text="Finish Treatment",
            command=on_finish_patient,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="green",
            hover_color="darkgreen"
        )
        finish_button.grid(row=0, column=2, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Patient",
            command=on_delete,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.grid(row=0, column=3, padx=5, pady=5)
        
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.show_patients,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        refresh_button.grid(row=0, column=4, padx=5, pady=5)

    def mark_patient_complete(self, patient_id):
        """Mark a patient's treatment as complete"""
        patient = get_patient(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        appointments = get_appointments_by_patient(patient_id)
        pending_appointments = [apt for apt in appointments if apt["is_completed"] == 0]
        
        if pending_appointments:
            response = messagebox.askyesno(
                "Pending Appointments",
                f"Patient has {len(pending_appointments)} pending appointment(s).\n\n"
                "Do you want to mark all appointments as completed and finish treatment?"
            )
            
            if response:
                for apt in pending_appointments:
                    mark_appointment_completed(apt["id"], "paid", apt["total_amount"])
                
                messagebox.showinfo(
                    "Success", 
                    f"Treatment completed for {patient['first_name']} {patient['last_name']}.\n"
                    f"{len(pending_appointments)} appointment(s) marked as completed."
                )
                return
        
        response = messagebox.askyesno(
            "Finish Treatment",
            f"Mark treatment as complete for {patient['first_name']} {patient['last_name']}?\n\n"
            "Note: This will not affect appointments."
        )
        
        if response:
            current_notes = patient["notes"] or ""
            completion_note = f"\n\n[TREATMENT COMPLETED on {datetime.now().strftime('%Y-%m-%d')}]"
            new_notes = current_notes + completion_note
            
            db_execute(
                "UPDATE patients SET notes=? WHERE id=?",
                (new_notes, patient_id)
            )
            
            messagebox.showinfo(
                "Success", 
                f"Treatment marked as complete for {patient['first_name']} {patient['last_name']}"
            )

    def show_patient_appointments(self, patient_id):
        patient = get_patient(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        window = ctk.CTkToplevel(self)
        window.title(f"Appointments for {patient['first_name']} {patient['last_name']}")
        window.geometry("1200x600")
        window.transient(self)
        window.grab_set()
        
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ctk.CTkFrame(window)
        main_frame.pack(padx=25, pady=25, fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Appointments for {patient['first_name']} {patient['last_name']}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        tree_container = ctk.CTkFrame(tree_frame)
        tree_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        tree_scroll_y = ttk.Scrollbar(tree_container)
        tree_scroll_y.pack(side="right", fill="y")
        
        cols = ("id","date","doctor","service","price","status","completed","payment")
        appointments_tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            height=12
        )
        appointments_tree.pack(side="left", fill="both", expand=True)
        
        tree_scroll_y.config(command=appointments_tree.yview)
        
        column_widths = {
            "id": 60,
            "date": 180,
            "doctor": 180,
            "service": 180,
            "price": 120,
            "status": 120,
            "completed": 120,
            "payment": 150
        }
        
        for c in cols:
            appointments_tree.heading(c, text=c.title())
            appointments_tree.column(c, width=column_widths.get(c, 120))
        
        appointments = get_appointments_by_patient(patient_id)

        def refresh_appointments_tree():
            for i in appointments_tree.get_children():
                appointments_tree.delete(i)
            rows = get_appointments_by_patient(patient_id)
            for apt in rows:
                try:
                    apt_date = datetime.strptime(apt["start_datetime"], "%Y-%m-%d %H:%M:%S")
                    date_str = apt_date.strftime("%Y-%m-%d %H:%M")
                except:
                    date_str = apt["start_datetime"]

                completed = "Yes" if apt["is_completed"] == 1 else "No"
                payment = f"{apt['payment_status']} (₱{apt['amount_paid']:.2f})"

                appointments_tree.insert("", "end", iid=apt["id"],
                                    values=(apt["id"], date_str, apt["doctor_name"],
                                            apt["service_name"], f"₱{apt['total_amount']:.2f}",
                                           apt["status"], completed, payment))

        refresh_appointments_tree()

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)

        def edit_selected_appointment():
            sel = appointments_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select an appointment first")
                return
            aid = int(sel[0])
            appointment = get_appointment(aid)
            if not appointment:
                messagebox.showerror("Error", "Appointment not found")
                return

            # Open appointment editor; after it closes, refresh the tree
            self.appointment_form(aid)
            refresh_appointments_tree()

        def close_window():
            window.destroy()

        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Appointment",
            command=edit_selected_appointment,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        edit_button.pack(side="left", padx=5)

        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=close_window,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        close_button.pack(side="left", padx=5)

    def patient_form(self, patient_id=None):
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add Patient" if patient_id is None else "Edit Patient")
        form_window.geometry("600x600")
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
            text="Add Patient" if patient_id is None else "Edit Patient",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        first_name_label = ctk.CTkLabel(form_frame, text="First Name:", font=ctk.CTkFont(size=14))
        first_name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        first_name_entry = ctk.CTkEntry(form_frame, width=350, height=40)
        first_name_entry.grid(row=0, column=1, padx=10, pady=(10, 5))
        
        last_name_label = ctk.CTkLabel(form_frame, text="Last Name:", font=ctk.CTkFont(size=14))
        last_name_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        last_name_entry = ctk.CTkEntry(form_frame, width=350, height=40)
        last_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        age_label = ctk.CTkLabel(form_frame, text="Age:", font=ctk.CTkFont(size=14))
        age_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        age_entry = ctk.CTkEntry(form_frame, width=350, height=40)
        age_entry.grid(row=2, column=1, padx=10, pady=5)
        
        type_label = ctk.CTkLabel(form_frame, text="Type:", font=ctk.CTkFont(size=14))
        type_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        type_var = ctk.StringVar(value="pediatric")
        type_combobox = ctk.CTkComboBox(form_frame, values=["pediatric", "adult"],
                                         variable=type_var, width=350, height=40)
        type_combobox.grid(row=3, column=1, padx=10, pady=5)
        
        contact_label = ctk.CTkLabel(form_frame, text="Contact:", font=ctk.CTkFont(size=14))
        contact_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        contact_entry = ctk.CTkEntry(form_frame, width=350, height=40)
        contact_entry.grid(row=4, column=1, padx=10, pady=5)
        
        notes_label = ctk.CTkLabel(form_frame, text="Notes:", font=ctk.CTkFont(size=14))
        notes_label.grid(row=5, column=0, sticky="nw", padx=10, pady=5)
        notes_text = ctk.CTkTextbox(form_frame, width=350, height=120)
        notes_text.grid(row=5, column=1, padx=10, pady=5)
        
        if patient_id:
            patient = get_patient(patient_id)
            if patient:
                first_name_entry.insert(0, patient["first_name"])
                last_name_entry.insert(0, patient["last_name"])
                age_entry.insert(0, str(patient["age"]))
                type_var.set(patient["type"])
                contact_entry.insert(0, patient["contact"])
                notes_text.insert("1.0", patient["notes"])
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def save_patient():
            first = first_name_entry.get().strip()
            last = last_name_entry.get().strip()
            age = age_entry.get().strip()
            ptype = type_var.get().strip()
            contact = contact_entry.get().strip()
            notes = notes_text.get("1.0", "end").strip()
            
            if not first or not last:
                messagebox.showerror("Missing", "First and last name required")
                return
            if not age or not age.isdigit():
                messagebox.showerror("Invalid", "Age must be a number")
                return
            
            if patient_id:
                update_patient(patient_id, first, last, age, ptype, contact, notes)
                messagebox.showinfo("Saved", "Patient updated")
            else:
                pid = add_patient(first, last, age, ptype, contact, notes)
                messagebox.showinfo("Saved", f"Patient added (ID {pid})")
            
            form_window.destroy()
            self.show_patients()
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_patient,
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
        
        if patient_id:
            def open_teeth():
                form_window.destroy()
                self.show_tooth_editor(patient_id)
            
            teeth_button = ctk.CTkButton(
                button_frame,
                text="Edit Tooth Records",
                command=open_teeth,
                width=160,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            teeth_button.pack(side="left", padx=10)