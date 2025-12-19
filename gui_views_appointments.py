# gui_views_appointments.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from database import *

class AppointmentViews:
    def show_appointments(self):
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="Appointments", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        add_button = ctk.CTkButton(
            title_frame,
            text="New Appointment",
            command=self.appointment_form,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_button.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
        filter_frame = ctk.CTkFrame(self.main_content)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        
        date_label = ctk.CTkLabel(filter_frame, text="View date (YYYY-MM-DD):", font=ctk.CTkFont(size=14))
        date_label.grid(row=0, column=0, padx=(15, 5), pady=10)
        
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ctk.CTkEntry(filter_frame, textvariable=self.date_var, width=180, height=40)
        date_entry.grid(row=0, column=1, padx=5, pady=10)
        
        status_label = ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.grid(row=0, column=2, padx=(25, 5), pady=10)
        
        self.status_var = ctk.StringVar(value="all")
        status_combobox = ctk.CTkComboBox(filter_frame, values=["all", "scheduled", "completed", "cancelled", "overdue"],
                                          variable=self.status_var, width=180, height=40)
        status_combobox.grid(row=0, column=3, padx=5, pady=10)
        
        # Add filter for all appointments
        
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
        
        cols = ("id","date","patient","doctor","service","price","status","completed","payment")
        self.appointments_tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=12
        )
        self.appointments_tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll_y.config(command=self.appointments_tree.yview)
        tree_scroll_x.config(command=self.appointments_tree.xview)
        
        column_widths = {
            "id": 60,
            "date": 180,
            "patient": 180,
            "doctor": 180,
            "service": 180,
            "price": 120,
            "status": 120,
            "completed": 100,
            "payment": 140
        }
        
        for c in cols:
            self.appointments_tree.heading(c, text=c.title())
            self.appointments_tree.column(c, width=column_widths.get(c, 140))
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def refresh_appointments():
            d = self.date_var.get().strip()
            status_filter = self.status_var.get()
            
            try:
                date_obj = datetime.strptime(d, "%Y-%m-%d")
            except:
                messagebox.showerror("Date", "Invalid date format")
                return
            
            start = date_obj.strftime("%Y-%m-%d 00:00:00")
            end = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
            
            print(f"Fetching appointments from {start} to {end}")  # Debug
            
            rows = get_appointments(start, end)
            print(f"Found {len(rows)} appointments")  # Debug
            
            for i in self.appointments_tree.get_children():
                self.appointments_tree.delete(i)
            
            if not rows:
                # Show message if no appointments
                self.appointments_tree.insert("", "end", values=("", "No appointments found", "", "", "", "", "", "", ""))
            else:
                for r in rows:
                    if status_filter != "all" and r["status"] != status_filter:
                        continue
                    
                    try:
                        apt_date = datetime.strptime(r["start_datetime"], "%Y-%m-%d %H:%M:%S")
                        date_str = apt_date.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = r["start_datetime"]
                    
                    completed = "Yes" if r["is_completed"] == 1 else "No"
                    payment = f"{r['payment_status']} (₱{r['amount_paid']:.2f})"
                    
                    self.appointments_tree.insert("", "end", iid=r["id"],
                                              values=(r["id"], date_str, r["patient_name"],
                                                      r["doctor_name"], r["service_name"],
                                                      f"₱{r['service_price']:.2f}",
                                                     r["status"], completed, payment))
        
        def edit_appointment():
            sel = self.appointments_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select appointment")
                return
            aid = int(sel[0])
            
            appointment = get_appointment(aid)
            if not appointment:
                messagebox.showerror("Error", "Appointment not found")
                return
            
            # Check if appointment is cancelled
            if appointment["status"] == "cancelled":
                messagebox.showerror("Cannot Edit", "This appointment has been cancelled and cannot be edited.")
                return
            
            if appointment["is_completed"] == 1:
                if not messagebox.askyesno("Edit Completed Appointment", 
                                          "This appointment is marked as completed. Edit anyway?"):
                    return
            
            self.appointment_form(aid)
        
        def mark_completed():
            sel = self.appointments_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select appointment")
                return
            aid = int(sel[0])
            
            appointment = get_appointment(aid)
            if not appointment:
                messagebox.showerror("Error", "Appointment not found")
                return
            
            if appointment["is_completed"] == 1:
                messagebox.showinfo("Already Completed", "This appointment is already marked as completed.")
                return
            
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Mark Appointment #{aid} as Completed")
            dialog.geometry("500x350")
            dialog.transient(self)
            dialog.grab_set()
            
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            main_frame = ctk.CTkFrame(dialog)
            main_frame.pack(padx=25, pady=25, fill="both", expand=True)
            
            service_price = appointment["total_amount"]
            
            info_label = ctk.CTkLabel(
                main_frame,
                text=f"Service Total: ₱{service_price:.2f}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            info_label.pack(pady=(0, 25))
            
            status_label = ctk.CTkLabel(main_frame, text="Payment Status:", font=ctk.CTkFont(size=14))
            status_label.pack(pady=(10, 5))
            
            status_var = ctk.StringVar(value="paid")
            status_combobox = ctk.CTkComboBox(main_frame, values=["paid", "partial", "pending"],
                                              variable=status_var, width=250, height=40)
            status_combobox.pack(pady=(0, 15))
            
            amount_label = ctk.CTkLabel(main_frame, text="Amount Paid (₱):", font=ctk.CTkFont(size=14))
            amount_label.pack(pady=(15, 5))
            
            amount_var = ctk.DoubleVar(value=service_price)
            amount_entry = ctk.CTkEntry(main_frame, textvariable=amount_var, width=250, height=40)
            amount_entry.pack(pady=(0, 25))
            
            def save_completion():
                payment_status = status_var.get()
                amount_paid = amount_var.get()
                
                if amount_paid < 0:
                    messagebox.showerror("Invalid", "Amount cannot be negative")
                    return
                
                if amount_paid > service_price:
                    messagebox.showwarning("Warning", f"Amount paid (₱{amount_paid:.2f}) exceeds total (₱{service_price:.2f})")
                
                mark_appointment_completed(aid, payment_status, amount_paid)
                messagebox.showinfo("Success", f"Appointment #{aid} marked as completed")
                dialog.destroy()
                refresh_appointments()
            
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(pady=10)
            
            save_button = ctk.CTkButton(
                button_frame,
                text="Mark Completed",
                command=save_completion,
                width=180,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            save_button.pack(side="left", padx=5)
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=180,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            cancel_button.pack(side="left", padx=5)
        
        def delete_appt():
            sel = self.appointments_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select appointment")
                return
            aid = int(sel[0])
            
            if messagebox.askyesno("Confirm Delete", f"Delete appointment #{aid}?"):
                delete_appointment(aid)
                messagebox.showinfo("Success", f"Appointment #{aid} deleted")
                refresh_appointments()
        
        def update_payment():
            sel = self.appointments_tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Select appointment")
                return
            
            aid = int(sel[0])
            
            appointment = get_appointment(aid)
            if not appointment:
                messagebox.showerror("Error", "Appointment not found")
                return
            
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Update Payment for Appointment #{aid}")
            dialog.geometry("500x400")
            dialog.transient(self)
            dialog.grab_set()
            
            dialog.lift()
            dialog.focus_force()
            dialog.attributes('-topmost', True)
            
            dialog.update_idletasks()
            width = 500
            height = 400
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            main_frame = ctk.CTkFrame(dialog)
            main_frame.pack(padx=20, pady=20, fill="both", expand=True)
            
            title_label = ctk.CTkLabel(
                main_frame,
                text=f"Update Payment for Appointment #{aid}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.pack(pady=(0, 20))
            
            info_label = ctk.CTkLabel(
                main_frame,
                text=f"Total Amount: ₱{appointment['total_amount']:.2f}",
                font=ctk.CTkFont(size=16)
            )
            info_label.pack(pady=(0, 20))
            
            status_frame = ctk.CTkFrame(main_frame)
            status_frame.pack(fill="x", padx=20, pady=10)
            
            status_label = ctk.CTkLabel(status_frame, text="Payment Status:", 
                                       font=ctk.CTkFont(size=14))
            status_label.pack(side="left", padx=(0, 10))
            
            status_var = ctk.StringVar(value=appointment["payment_status"])
            status_combobox = ctk.CTkComboBox(status_frame, values=["paid", "partial", "pending"],
                                              variable=status_var, width=200, height=35)
            status_combobox.pack(side="left")
            
            amount_frame = ctk.CTkFrame(main_frame)
            amount_frame.pack(fill="x", padx=20, pady=10)
            
            amount_label = ctk.CTkLabel(amount_frame, text="Amount Paid (₱):", 
                                       font=ctk.CTkFont(size=14))
            amount_label.pack(side="left", padx=(0, 10))
            
            amount_var = ctk.StringVar(value=str(appointment["amount_paid"]))
            amount_entry = ctk.CTkEntry(amount_frame, textvariable=amount_var, 
                                       width=200, height=35)
            amount_entry.pack(side="left")
            
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(pady=30)
            
            def save_payment():
                payment_status = status_var.get()
                
                try:
                    amount_paid = float(amount_var.get())
                except ValueError:
                    messagebox.showerror("Invalid", "Amount must be a valid number")
                    return
                
                if amount_paid < 0:
                    messagebox.showerror("Invalid", "Amount cannot be negative")
                    return
                
                if amount_paid > appointment["total_amount"]:
                    if not messagebox.askyesno("Warning", 
                                              f"Amount paid (₱{amount_paid:.2f}) exceeds total (₱{appointment['total_amount']:.2f}).\n\nContinue anyway?"):
                        return
                
                update_appointment_payment(aid, payment_status, amount_paid)
                messagebox.showinfo("Success", f"Payment updated for appointment #{aid}")
                dialog.destroy()
                refresh_appointments()
            
            def cancel_payment():
                dialog.destroy()
            
            save_button = ctk.CTkButton(
                button_frame,
                text="SAVE PAYMENT",
                command=save_payment,
                width=180,
                height=45,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="green",
                hover_color="darkgreen"
            )
            save_button.pack(side="left", padx=10, pady=10)
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=cancel_payment,
                width=100,
                height=35,
                font=ctk.CTkFont(size=14)
            )
            cancel_button.pack(side="left", padx=10, pady=10)
            
            amount_entry.focus_set()
            amount_entry.select_range(0, 'end')
            
            dialog.bind('<Return>', lambda event: save_payment())
            
            dialog.after(100, lambda: dialog.attributes('-topmost', False))
        
        show_button = ctk.CTkButton(
            filter_frame,
            text="Show",
            command=refresh_appointments,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        show_button.grid(row=0, column=4, padx=5, pady=10)
        
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Appointment",
            command=edit_appointment,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        edit_button.grid(row=0, column=0, padx=5, pady=5)
        
        complete_button = ctk.CTkButton(
            button_frame,
            text="Mark Completed",
            command=mark_completed,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        complete_button.grid(row=0, column=1, padx=5, pady=5)
        
        payment_button = ctk.CTkButton(
            button_frame,
            text="Update Payment",
            command=update_payment,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        payment_button.grid(row=0, column=2, padx=5, pady=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            command=delete_appt,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.grid(row=0, column=3, padx=5, pady=5)
        
        refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=refresh_appointments,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        refresh_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Load appointments for today by default
        refresh_appointments()
        
        # Also add a function to show all appointments without date filter
    def show_all_appointments(self):
        """Show all appointments without date filter"""
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="All Appointments", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        back_button = ctk.CTkButton(
            title_frame,
            text="Back to Today",
            command=self.show_appointments,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        back_button.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
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
        
        cols = ("id","date","patient","doctor","service","price","status","completed","payment")
        tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            height=15
        )
        tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.config(command=tree.yview)
        
        column_widths = {
            "id": 60,
            "date": 180,
            "patient": 180,
            "doctor": 180,
            "service": 180,
            "price": 120,
            "status": 120,
            "completed": 100,
            "payment": 140
        }
        
        for c in cols:
            tree.heading(c, text=c.title())
            tree.column(c, width=column_widths.get(c, 140))
        
        # Get all appointments without date filter
        rows = get_appointments()
        print(f"Found {len(rows)} total appointments")  # Debug
        
        if not rows:
            tree.insert("", "end", values=("", "No appointments found", "", "", "", "", "", "", ""))
        else:
            for r in rows:
                try:
                    apt_date = datetime.strptime(r["start_datetime"], "%Y-%m-%d %H:%M:%S")
                    date_str = apt_date.strftime("%Y-%m-%d %H:%M")
                except:
                    date_str = r["start_datetime"]
                
                completed = "Yes" if r["is_completed"] == 1 else "No"
                payment = f"{r['payment_status']} (₱{r['amount_paid']:.2f})"
                
                tree.insert("", "end", iid=r["id"],
                          values=(r["id"], date_str, r["patient_name"],
                                  r["doctor_name"], r["service_name"],
                                  f"₱{r['service_price']:.2f}",
                                 r["status"], completed, payment))

    def appointment_form(self, appointment_id=None):
        form_window = ctk.CTkToplevel(self)
        if appointment_id:
            form_window.title("Edit Appointment")
            is_edit = True
            
            # Check if appointment is cancelled
            appointment = get_appointment(appointment_id)
            if appointment and appointment["status"] == "cancelled":
                messagebox.showerror("Cannot Edit", "This appointment has been cancelled and cannot be edited.")
                form_window.destroy()
                return
        else:
            form_window.title("New Appointment")
            is_edit = False
        form_window.geometry("650x700")
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
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable content frame with grid layout
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        if not is_edit:
            def auto_assign():
                service_str = service_var.get()
                if not service_str:
                    messagebox.showinfo("Select Service", "Please select a service first")
                    return
                
                # Extract service name from the combobox text
                service_name = service_str.split(":")[1].strip().split("(")[0].strip()
                
                doctor = auto_assign_doctor(service_name)
                if doctor:
                    # Find and set the matching doctor in the combobox
                    for doc_option in doctor_options:
                        if str(doctor["id"]) in doc_option:
                            doctor_var.set(doc_option)
                            messagebox.showinfo("Auto Assignment",
                                               f"Auto-assigned: Dr. {doctor['name']} ({doctor['specialty']})")
                            return
                    
                    # If exact match not found, just show info
                    messagebox.showinfo("Auto Assignment", 
                                       f"Auto-assigned: Dr. {doctor['name']} ({doctor['specialty']})")
                else:
                    messagebox.showinfo("No Doctor", "No suitable doctor available for this service")
            
            auto_button = ctk.CTkButton(
                content_frame,
                text="Auto Assign Doctor",
                command=auto_assign,
                width=220,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="green",
                hover_color="darkgreen"
            )
            auto_button.grid(row=0, column=0, columnspan=2, pady=(0, 25), padx=10)
        
        row = 1 if not is_edit else 0
        
        patient_label = ctk.CTkLabel(content_frame, text="Patient:", font=ctk.CTkFont(size=14))
        patient_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        
        patients = get_patients()
        patient_options = [f"{p['id']}: {p['last_name']}, {p['first_name']}" for p in patients]
        patient_var = ctk.StringVar()
        patient_combobox = ctk.CTkComboBox(content_frame, values=patient_options,
                                           variable=patient_var, width=350, height=40)
        patient_combobox.grid(row=row, column=1, padx=10, pady=(10, 5))
        row += 1
        
        doctor_label = ctk.CTkLabel(content_frame, text="Doctor:", font=ctk.CTkFont(size=14))
        doctor_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        
        all_doctors = get_doctors()
        doctor_options = []
        for d in all_doctors:
            status = "✅" if d["is_available"] == 1 else "❌"
            doctor_options.append(f"{d['id']}: {d['name']} ({d['specialty']}) {status}")
        
        doctor_var = ctk.StringVar()
        doctor_combobox = ctk.CTkComboBox(content_frame, values=doctor_options,
                                          variable=doctor_var, width=350, height=40)
        doctor_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        service_label = ctk.CTkLabel(content_frame, text="Service:", font=ctk.CTkFont(size=14))
        service_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        
        services = get_services()
        service_options = [f"{s['id']}: {s['name']} (₱{s['price']:.2f})" for s in services]
        service_var = ctk.StringVar()
        service_combobox = ctk.CTkComboBox(content_frame, values=service_options,
                                           variable=service_var, width=350, height=40)
        service_combobox.grid(row=row, column=1, padx=10, pady=10)
        
        service_combobox.bind("<FocusOut>", lambda e: None)
        service_var.trace("w", lambda *args: None)
        row += 1
        
        date_label = ctk.CTkLabel(content_frame, text="Date (YYYY-MM-DD):", font=ctk.CTkFont(size=14))
        date_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        date_entry = ctk.CTkEntry(content_frame, width=350, height=40)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        time_label = ctk.CTkLabel(content_frame, text="Time (HH:MM):", font=ctk.CTkFont(size=14))
        time_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        time_slots = []
        for h in range(8, 17):
            for m in (0, 30):
                if h == 16 and m > 0:
                    continue
                time_slots.append(f"{h:02d}:{m:02d}")

        time_var = ctk.StringVar()
        time_combobox = ctk.CTkComboBox(content_frame, values=time_slots,
                                        variable=time_var, width=350, height=40)
        time_var.set("09:00")
        time_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        duration_label = ctk.CTkLabel(content_frame, text="Duration (minutes):", font=ctk.CTkFont(size=14))
        duration_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        duration_var = ctk.IntVar(value=30)
        duration_entry = ctk.CTkEntry(content_frame, textvariable=duration_var, width=350, height=40)
        duration_entry.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        # STATUS SECTION - CHANGED BASED ON EDIT/NEW
        status_label = ctk.CTkLabel(content_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.grid(row=row, column=0, sticky="w", padx=10, pady=10)
        
        if appointment_id:
            # Edit mode: show all status options
            status_options = ["scheduled", "cancelled", "completed"]
        else:
            # New appointment: only "scheduled"
            status_options = ["scheduled"]
        
        status_var = ctk.StringVar(value="scheduled")
        status_combobox = ctk.CTkComboBox(content_frame, values=status_options,
                                          variable=status_var, width=350, height=40)
        status_combobox.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        notes_label = ctk.CTkLabel(content_frame, text="Notes:", font=ctk.CTkFont(size=14))
        notes_label.grid(row=row, column=0, sticky="nw", padx=10, pady=10)
        notes_text = ctk.CTkTextbox(content_frame, width=350, height=80)
        notes_text.grid(row=row, column=1, padx=10, pady=10)
        row += 1
        
        # (Diagnosis/Medicine fields removed)
        
        if appointment_id:
            appointment = get_appointment(appointment_id)
            if appointment:
                for patient_option in patient_options:
                    if str(appointment["patient_id"]) in patient_option:
                        patient_var.set(patient_option)
                        break
                
                for doctor_option in doctor_options:
                    if str(appointment["doctor_id"]) in doctor_option:
                        doctor_var.set(doctor_option)
                        break
                
                for service_option in service_options:
                    if str(appointment["service_id"]) in service_option:
                        service_var.set(service_option)
                        break
                
                try:
                    start_dt = datetime.strptime(appointment["start_datetime"], "%Y-%m-%d %H:%M:%S")
                    date_entry.delete(0, 'end')
                    date_entry.insert(0, start_dt.strftime("%Y-%m-%d"))
                    time_var.set(start_dt.strftime("%H:%M"))
                    
                    if appointment["end_datetime"]:
                        end_dt = datetime.strptime(appointment["end_datetime"], "%Y-%m-%d %H:%M:%S")
                        duration = int((end_dt - start_dt).total_seconds() / 60)
                        duration_var.set(duration)
                except:
                    pass
                
                status_var.set(appointment["status"])
                notes_text.insert("1.0", appointment["notes"] or "")
                # (Diagnosis/Medicine removed from appointment prefill)
        
        # Button frame - always visible at bottom
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        def save_appointment():
            patient_str = patient_var.get()
            doctor_str = doctor_var.get()
            service_str = service_var.get()
            date_str = date_entry.get().strip()
            time_str = time_var.get().strip()
            duration = duration_var.get()
            status = status_var.get()
            notes = notes_text.get("1.0", "end").strip()
            # diagnosis/medicine fields removed
            
            if not patient_str:
                messagebox.showerror("Missing", "Please select a patient")
                patient_combobox.focus()
                return
            
            if not doctor_str:
                messagebox.showerror("Missing", "Please select a doctor")
                doctor_combobox.focus()
                return
            
            if not service_str:
                messagebox.showerror("Missing", "Please select a service")
                service_combobox.focus()
                return
            
            if not date_str:
                messagebox.showerror("Missing", "Please enter a date")
                date_entry.focus()
                return
            
            if not time_str:
                messagebox.showerror("Missing", "Please select a time")
                return
            
            try:
                # Parse IDs correctly - split by ":" and take the first part
                patient_id = int(patient_str.split(":")[0].strip())
                doctor_id = int(doctor_str.split(":")[0].strip())
                service_id = int(service_str.split(":")[0].strip())
            except (ValueError, IndexError) as e:
                messagebox.showerror("Error", f"Invalid selection format: {str(e)}")
                return
            
            try:
                start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showerror("Date", "Invalid date/time format. Use YYYY-MM-DD and HH:MM")
                return
            
            end_dt = start_dt + timedelta(minutes=duration)
            
            if appointment_id:
                # Edit existing appointment
                current_appointment = get_appointment(appointment_id)
                
                # If changing status to "completed" from another status
                if current_appointment and status == "completed" and current_appointment["status"] != "completed":
                    # Show payment dialog for completion
                    dialog = ctk.CTkToplevel(form_window)
                    dialog.title(f"Mark Appointment #{appointment_id} as Completed")
                    dialog.geometry("500x350")
                    dialog.transient(form_window)
                    dialog.grab_set()
                    
                    dialog.update_idletasks()
                    width = dialog.winfo_width()
                    height = dialog.winfo_height()
                    x = (form_window.winfo_screenwidth() // 2) - (width // 2)
                    y = (form_window.winfo_screenheight() // 2) - (height // 2)
                    dialog.geometry(f'{width}x{height}+{x}+{y}')
                    
                    payment_frame = ctk.CTkFrame(dialog)
                    payment_frame.pack(padx=25, pady=25, fill="both", expand=True)
                    
                    service_price = current_appointment["total_amount"]
                    
                    info_label = ctk.CTkLabel(
                        payment_frame,
                        text=f"Service Total: ₱{service_price:.2f}",
                        font=ctk.CTkFont(size=18, weight="bold")
                    )
                    info_label.pack(pady=(0, 25))
                    
                    payment_status_label = ctk.CTkLabel(payment_frame, text="Payment Status:", font=ctk.CTkFont(size=14))
                    payment_status_label.pack(pady=(10, 5))
                    
                    payment_status_var = ctk.StringVar(value="paid")
                    payment_status_combobox = ctk.CTkComboBox(payment_frame, values=["paid", "partial", "pending"],
                                                              variable=payment_status_var, width=250, height=40)
                    payment_status_combobox.pack(pady=(0, 15))
                    
                    amount_label = ctk.CTkLabel(payment_frame, text="Amount Paid (₱):", font=ctk.CTkFont(size=14))
                    amount_label.pack(pady=(15, 5))
                    
                    amount_var = ctk.DoubleVar(value=service_price)
                    amount_entry = ctk.CTkEntry(payment_frame, textvariable=amount_var, width=250, height=40)
                    amount_entry.pack(pady=(0, 25))
                    
                    def save_completion_and_edit():
                        payment_status = payment_status_var.get()
                        amount_paid = amount_var.get()
                        
                        if amount_paid < 0:
                            messagebox.showerror("Invalid", "Amount cannot be negative")
                            return
                        
                        if amount_paid > service_price:
                            messagebox.showwarning("Warning", f"Amount paid (₱{amount_paid:.2f}) exceeds total (₱{service_price:.2f})")
                        
                        # Update appointment details
                        update_appointment_details(appointment_id, patient_id, doctor_id, service_id,
                                                 start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                                 end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                                 status, notes)
                        
                        # Mark as completed with payment
                        mark_appointment_completed(appointment_id, payment_status, amount_paid)
                        
                        messagebox.showinfo("Success", f"Appointment #{appointment_id} updated and marked as completed")
                        dialog.destroy()
                        form_window.destroy()
                        self.show_appointments()
                    
                    def cancel_completion():
                        dialog.destroy()
                    
                    payment_button_frame = ctk.CTkFrame(payment_frame)
                    payment_button_frame.pack(pady=10)
                    
                    save_button = ctk.CTkButton(
                        payment_button_frame,
                        text="Save and Mark Completed",
                        command=save_completion_and_edit,
                        width=200,
                        height=40,
                        font=ctk.CTkFont(size=14)
                    )
                    save_button.pack(side="left", padx=5)
                    
                    cancel_button = ctk.CTkButton(
                        payment_button_frame,
                        text="Cancel",
                        command=cancel_completion,
                        width=180,
                        height=40,
                        font=ctk.CTkFont(size=14)
                    )
                    cancel_button.pack(side="left", padx=5)
                    
                    return  
                
                # Regular update for non-completed status changes
                update_appointment_details(appointment_id, patient_id, doctor_id, service_id,
                                         start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                         end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                         status, notes)
                
                messagebox.showinfo("Success", f"Appointment #{appointment_id} updated")
                form_window.destroy()
                self.show_appointments()
            else:
                # Create new appointment
                aid, err = add_appointment(patient_id, doctor_id, service_id,
                                           start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                          end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                          status, notes)
                
                if err:
                    messagebox.showerror("Error", err)
                    return
                
                messagebox.showinfo("Success", f"Appointment created (ID: {aid})")
                form_window.destroy()
                self.show_appointments()
        
        # If editing an existing appointment, add a "View Receipt" button
        if appointment_id:
            def show_receipt():
                try:
                    receipt = generate_receipt(appointment_id)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not generate receipt: {e}")
                    return

                dialog = ctk.CTkToplevel(form_window)
                dialog.title(f"Receipt for Appointment #{appointment_id}")
                dialog.geometry("700x520")
                dialog.transient(form_window)
                dialog.grab_set()

                dialog.update_idletasks()
                width = dialog.winfo_width()
                height = dialog.winfo_height()
                x = (form_window.winfo_screenwidth() // 2) - (width // 2)
                y = (form_window.winfo_screenheight() // 2) - (height // 2)
                dialog.geometry(f'{width}x{height}+{x}+{y}')

                txt = ctk.CTkTextbox(dialog, width=660, height=380)
                txt.pack(padx=10, pady=10, fill="both", expand=True)
                txt.insert("1.0", receipt)
                txt.configure(state="disabled")

                def save_to_file():
                    from tkinter import filedialog
                    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
                    if path:
                        try:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(receipt)
                            messagebox.showinfo("Saved", f"Receipt saved to {path}")
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not save file: {e}")

                bottom = ctk.CTkFrame(dialog)
                bottom.pack(pady=8)
                ctk.CTkButton(bottom, text="Save", command=save_to_file, width=140, height=36).pack(side="left", padx=8)
                ctk.CTkButton(bottom, text="Close", command=dialog.destroy, width=140, height=36).pack(side="left", padx=8)

            view_button = ctk.CTkButton(
                button_frame,
                text="View Receipt",
                command=show_receipt,
                width=160,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            view_button.grid(row=0, column=0, padx=10, pady=10)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_appointment,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        save_button.grid(row=0, column=1, padx=10, pady=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=form_window.destroy,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Set focus to patient combobox
        if not appointment_id:
            form_window.after(100, lambda: patient_combobox.focus())

    def show_overdue_appointments(self):
        """Display overdue appointments"""
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="📝 Overdue Appointments", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Check for new overdue appointments
        from database import check_overdue_appointments
        count = check_overdue_appointments()
        if count > 0:
            info_label = ctk.CTkLabel(
                title_frame,
                text=f"⚠️  {count} appointment(s) marked as overdue",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            info_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        
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
        
        cols = ("id", "patient", "doctor", "service", "scheduled_time", "end_time", "original_status")
        tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            height=12
        )
        tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.config(command=tree.yview)
        
        column_widths = {
            "id": 60,
            "patient": 180,
            "doctor": 180,
            "service": 180,
            "scheduled_time": 160,
            "end_time": 160,
            "original_status": 120
        }
        
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=column_widths.get(c, 140))
        
        # Load overdue appointments
        from database import get_overdue_appointments
        overdue_appointments = get_overdue_appointments()
        
        if not overdue_appointments:
            no_data_label = ctk.CTkLabel(
                tree_frame,
                text="No overdue appointments",
                font=ctk.CTkFont(size=16)
            )
            no_data_label.grid(row=0, column=0, padx=20, pady=100)
        else:
            for apt in overdue_appointments:
                try:
                    start_dt = datetime.strptime(apt["start_datetime"], "%Y-%m-%d %H:%M:%S")
                    start_str = start_dt.strftime("%Y-%m-%d %H:%M")
                    end_dt = datetime.strptime(apt["end_datetime"], "%Y-%m-%d %H:%M:%S")
                    end_str = end_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    start_str = apt["start_datetime"]
                    end_str = apt["end_datetime"]
                
                tree.insert("", "end", values=(
                    apt["id"],
                    apt["patient_name"],
                    apt["doctor_name"],
                    apt["service_name"],
                    start_str,
                    end_str,
                    "Overdue"
                ))
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def view_archived():
            self.show_archived_appointments()
        
        def refresh_view():
            self.show_overdue_appointments()
        
        def back_to_appointments():
            self.show_appointments()
        
        ctk.CTkButton(
            button_frame,
            text="📋 View Archived Appointments",
            command=view_archived,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#e9c46a"
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=refresh_view,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="⬅️ Back to Appointments",
            command=back_to_appointments,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=5)

    def show_archived_appointments(self):
        """Display all archived appointments"""
        self.clear_main_content()
        
        title_frame = ctk.CTkFrame(self.main_content)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🗃️ Archived Appointments", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
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
        
        cols = ("id", "patient", "doctor", "service", "scheduled_time", "archived_at", "reason")
        tree = ttk.Treeview(
            tree_container, 
            columns=cols,
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            height=12
        )
        tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.config(command=tree.yview)
        
        column_widths = {
            "id": 60,
            "patient": 180,
            "doctor": 180,
            "service": 180,
            "scheduled_time": 160,
            "archived_at": 160,
            "reason": 120
        }
        
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=column_widths.get(c, 140))
        
        # Load archived appointments
        from database import get_archived_appointments
        archived_appointments = get_archived_appointments()
        
        if not archived_appointments:
            no_data_label = ctk.CTkLabel(
                tree_frame,
                text="No archived appointments",
                font=ctk.CTkFont(size=16)
            )
            no_data_label.grid(row=0, column=0, padx=20, pady=100)
        else:
            for apt in archived_appointments:
                try:
                    start_dt = datetime.strptime(apt["start_datetime"], "%Y-%m-%d %H:%M:%S")
                    start_str = start_dt.strftime("%Y-%m-%d %H:%M")
                    archived_dt = datetime.strptime(apt["archived_at"], "%Y-%m-%d %H:%M:%S")
                    archived_str = archived_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    start_str = apt["start_datetime"]
                    archived_str = apt["archived_at"]
                
                tree.insert("", "end", values=(
                    apt["original_id"],
                    apt["patient_name"],
                    apt["doctor_name"],
                    apt["service_name"],
                    start_str,
                    archived_str,
                    apt["archived_reason"].title()
                ))
        
        button_frame = ctk.CTkFrame(self.main_content)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def back_to_overdue():
            self.show_overdue_appointments()
        
        def back_to_appointments():
            self.show_appointments()
        
        ctk.CTkButton(
            button_frame,
            text="📝 View Overdue",
            command=back_to_overdue,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="⬅️ Back to Appointments",
            command=back_to_appointments,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5, pady=5)