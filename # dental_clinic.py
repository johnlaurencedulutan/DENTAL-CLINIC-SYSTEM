# Dental Clinic System (SQLite + customtkinter) - FIXED VERSION
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
from datetime import datetime, timedelta
import math

DB_FILE = "dental_clinic.db"

# Configure customtkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# --------------------------
# Tooth name data
# (Keep your PRIMARY_TEETH and PERMANENT_TEETH lists as they were)
PRIMARY_TEETH = [
    {"id": "A", "name": "Upper Right Second Molar (Primary)"},
    {"id": "B", "name": "Upper Right First Molar (Primary)"},
    {"id": "C", "name": "Upper Right Canine (Primary)"},
    {"id": "D", "name": "Upper Right Lateral Incisor (Primary)"},
    {"id": "E", "name": "Upper Right Central Incisor (Primary)"},
    {"id": "F", "name": "Upper Left Central Incisor (Primary)"},
    {"id": "G", "name": "Upper Left Lateral Incisor (Primary)"},
    {"id": "H", "name": "Upper Left Canine (Primary)"},
    {"id": "I", "name": "Upper Left First Molar (Primary)"},
    {"id": "J", "name": "Upper Left Second Molar (Primary)"},
    {"id": "K", "name": "Lower Left Second Molar (Primary)"},
    {"id": "L", "name": "Lower Left First Molar (Primary)"},
    {"id": "M", "name": "Lower Left Canine (Primary)"},
    {"id": "N", "name": "Lower Left Lateral Incisor (Primary)"},
    {"id": "O", "name": "Lower Left Central Incisor (Primary)"},
    {"id": "P", "name": "Lower Right Central Incisor (Primary)"},
    {"id": "Q", "name": "Lower Right Lateral Incisor (Primary)"},
    {"id": "R", "name": "Lower Right Canine (Primary)"},
    {"id": "S", "name": "Lower Right First Molar (Primary)"},
    {"id": "T", "name": "Lower Right Second Molar (Primary)"},
]

PERMANENT_TEETH = [
    {"id": "1", "name": "Upper Right Third Molar (Wisdom)"},
    {"id": "2", "name": "Upper Right Second Molar"},
    {"id": "3", "name": "Upper Right First Molar"},
    {"id": "4", "name": "Upper Right Second Premolar"},
    {"id": "5", "name": "Upper Right First Premolar"},
    {"id": "6", "name": "Upper Right Canine"},
    {"id": "7", "name": "Upper Right Lateral Incisor"},
    {"id": "8", "name": "Upper Right Central Incisor"},
    {"id": "9", "name": "Upper Left Central Incisor"},
    {"id": "10", "name": "Upper Left Lateral Incisor"},
    {"id": "11", "name": "Upper Left Canine"},
    {"id": "12", "name": "Upper Left First Premolar"},
    {"id": "13", "name": "Upper Left Second Premolar"},
    {"id": "14", "name": "Upper Left First Molar"},
    {"id": "15", "name": "Upper Left Second Molar"},
    {"id": "16", "name": "Upper Left Third Molar (Wisdom)"},
    {"id": "17", "name": "Lower Left Third Molar (Wisdom)"},
    {"id": "18", "name": "Lower Left Second Molar"},
    {"id": "19", "name": "Lower Left First Molar"},
    {"id": "20", "name": "Lower Left Second Premolar"},
    {"id": "21", "name": "Lower Left First Premolar"},
    {"id": "22", "name": "Lower Left Canine"},
    {"id": "23", "name": "Lower Left Lateral Incisor"},
    {"id": "24", "name": "Lower Left Central Incisor"},
    {"id": "25", "name": "Lower Right Central Incisor"},
    {"id": "26", "name": "Lower Right Lateral Incisor"},
    {"id": "27", "name": "Lower Right Canine"},
    {"id": "28", "name": "Lower Right First Premolar"},
    {"id": "29", "name": "Lower Right Second Premolar"},
    {"id": "30", "name": "Lower Right First Molar"},
    {"id": "31", "name": "Lower Right Second Molar"},
    {"id": "32", "name": "Lower Right Third Molar (Wisdom)"},
]

# Services sample with prices (keep as is)
DEFAULT_SERVICES = [
    ("Checkup", "General dental checkup and consultation", 500.0),
    ("Extraction", "Tooth removal", 1500.0),
    ("Filling", "Tooth filling (composite)", 1200.0),
    ("Cleaning", "Scaling and polishing", 700.0),
    ("Pediatric Checkup", "Child dental checkup", 400.0),
    ("Root Canal", "Root canal treatment", 3500.0),
    ("Crown", "Dental crown placement", 5000.0),
    ("Braces", "Orthodontic braces", 20000.0),
    ("Whitening", "Teeth whitening", 3000.0),
    ("Denture", "Full or partial denture", 8000.0),
]

# Default doctors
DEFAULT_DOCTORS = [
    ("Dr. Maria Santos", "Pediatric Dentistry", "09171234567", 1),
    ("Dr. Jose Cruz", "General Dentistry", "09179876543", 1),
    ("Dr. Anna Reyes", "Orthodontics", "09175556677", 1),
    ("Dr. Robert Lim", "Oral Surgery", "09178889900", 1),
    ("Dr. Sofia Tan", "Periodontics", "09172223344", 1),
]

# --------------------------
# Database helper functions
# --------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialty TEXT,
        contact TEXT,
        is_available INTEGER DEFAULT 1
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        type TEXT,
        contact TEXT,
        notes TEXT,
        tooth_records TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        service_id INTEGER,
        start_datetime TEXT,
        end_datetime TEXT,
        status TEXT DEFAULT 'scheduled',
        notes TEXT,
        is_completed INTEGER DEFAULT 0,
        payment_status TEXT DEFAULT 'pending',
        amount_paid REAL DEFAULT 0.0,
        total_amount REAL DEFAULT 0.0,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
        FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE CASCADE
    )
    """)
    conn.commit()
    conn.close()

def seed_defaults():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        for s in DEFAULT_SERVICES:
            c.execute("INSERT INTO services(name,description,price) VALUES(?,?,?)", s)
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        for d in DEFAULT_DOCTORS:
            c.execute("INSERT INTO doctors(name,specialty,contact,is_available) VALUES(?,?,?,?)", d)
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        default_teeth = get_appropriate_tooth_set_for_age(8)
        c.execute(
            "INSERT INTO patients(first_name,last_name,age,type,contact,notes,tooth_records) VALUES(?,?,?,?,?,?,?)",
            ("Juan","Dela Cruz",8,"pediatric","09170001111","No major issues", json.dumps(default_teeth))
        )
    conn.commit()
    conn.close()

def db_execute(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def db_fetchall(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

def db_fetchone(query, params=()):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    result = c.fetchone()
    conn.close()
    return result

def get_appropriate_tooth_set_for_age(age):
    age = int(age)
    
    if age <= 2:
        baby_teeth = PRIMARY_TEETH[:8]
        return {t["id"]: {"status": "unknown", "notes": "", "present": age >= 1} for t in baby_teeth}
    
    elif age < 6:
        return {t["id"]: {"status": "unknown", "notes": "", "present": True} for t in PRIMARY_TEETH}
    
    elif age < 12:
        mixed_teeth = {}
        for t in PRIMARY_TEETH:
            if t["id"] in ["A", "B", "I", "J", "K", "L", "S", "T"]:
                mixed_teeth[t["id"]] = {"status": "unknown", "notes": "", "present": True}
        
        permanent_to_add = ["8", "9", "24", "25", "3", "14", "19", "30"]
        for t in PERMANENT_TEETH:
            if t["id"] in permanent_to_add:
                mixed_teeth[t["id"]] = {"status": "unknown", "notes": "", "present": age >= 6}
        
        return mixed_teeth
    
    elif age < 18:
        teen_teeth = {}
        for t in PERMANENT_TEETH:
            if t["id"] not in ["1", "16", "17", "32"]:
                teen_teeth[t["id"]] = {"status": "unknown", "notes": "", "present": True}
        return teen_teeth
    
    else:
        return {t["id"]: {"status": "unknown", "notes": "", "present": True} for t in PERMANENT_TEETH}

def get_tooth_count_for_age(age):
    age = int(age)
    if age <= 2:
        return 8
    elif age < 6:
        return 20
    elif age < 12:
        return 24
    elif age < 18:
        return 28
    else:
        return 32

# --------------------------
# Patient functions
# --------------------------
def add_patient(first, last, age, ptype, contact, notes, tooth_records=None):
    try:
        age_int = int(age)
    except:
        age_int = 0
    
    tooth_set = get_appropriate_tooth_set_for_age(age_int)
    
    if tooth_records is None:
        tooth_records = json.dumps(tooth_set)
    else:
        try:
            existing_records = json.loads(tooth_records)
            filtered_records = {}
            for tooth_id, tooth_info in existing_records.items():
                should_exist = False
                for age_based_tooth in tooth_set.keys():
                    if tooth_id == age_based_tooth:
                        should_exist = True
                        break
                
                if should_exist:
                    filtered_records[tooth_id] = tooth_info
            
            for tooth_id in tooth_set.keys():
                if tooth_id not in filtered_records:
                    filtered_records[tooth_id] = {"status": "unknown", "notes": "", "present": True}
            
            tooth_records = json.dumps(filtered_records)
        except:
            tooth_records = json.dumps(tooth_set)
    
    return db_execute(
        "INSERT INTO patients(first_name,last_name,age,type,contact,notes,tooth_records) VALUES(?,?,?,?,?,?,?)",
        (first,last,age_int,ptype,contact,notes,tooth_records)
    )

def update_patient(pid, first, last, age, ptype, contact, notes):
    try:
        age_int = int(age)
    except:
        age_int = 0
    
    db_execute(
        "UPDATE patients SET first_name=?, last_name=?, age=?, type=?, contact=?, notes=? WHERE id=?",
        (first,last,age_int,ptype,contact,notes,pid)
    )
    
    patient = get_patient(pid)
    if patient:
        old_age = patient["age"]
        new_age = age_int
        
        old_category = get_tooth_count_for_age(old_age)
        new_category = get_tooth_count_for_age(new_age)
        
        if old_category != new_category:
            tooth_set = get_appropriate_tooth_set_for_age(new_age)
            update_tooth_records(pid, json.dumps(tooth_set))

def delete_patient(pid):
    db_execute("DELETE FROM patients WHERE id=?", (pid,))

def get_patients():
    return db_fetchall("SELECT * FROM patients ORDER BY last_name, first_name")

def get_patient(pid):
    return db_fetchone("SELECT * FROM patients WHERE id=?", (pid,))

# --------------------------
# Doctor functions
# --------------------------
def add_doctor(name, specialty, contact, is_available=1):
    return db_execute("INSERT INTO doctors(name,specialty,contact,is_available) VALUES(?,?,?,?)", 
                     (name,specialty,contact,is_available))

def get_doctors():
    return db_fetchall("SELECT * FROM doctors ORDER BY name")

def get_available_doctors():
    return db_fetchall("SELECT * FROM doctors WHERE is_available=1 ORDER BY name")

def update_doctor(did, name, specialty, contact, is_available):
    db_execute("UPDATE doctors SET name=?, specialty=?, contact=?, is_available=? WHERE id=?", 
              (name,specialty,contact,is_available,did))

def toggle_doctor_availability(did, is_available):
    db_execute("UPDATE doctors SET is_available=? WHERE id=?", (is_available,did))

# FIXED: Renamed this function to avoid conflict
def remove_doctor(did):
    """Delete a doctor and their appointments"""
    # Check if doctor has any appointments
    appointments = db_fetchall("SELECT * FROM appointments WHERE doctor_id=?", (did,))
    if appointments:
        response = messagebox.askyesno(
            "Doctor has Appointments",
            f"This doctor has {len(appointments)} appointment(s).\n\nDelete doctor and all appointments?"
        )
        if response:
            db_execute("DELETE FROM appointments WHERE doctor_id=?", (did,))
        else:
            return False
    
    db_execute("DELETE FROM doctors WHERE id=?", (did,))
    return True

def get_doctor_appointment_count(did):
    result = db_fetchone("SELECT COUNT(*) as count FROM appointments WHERE doctor_id=?", (did,))
    return result["count"] if result else 0

# --------------------------
# Service functions
# --------------------------
def get_services():
    return db_fetchall("SELECT * FROM services ORDER BY name")

def add_service(name, desc, price):
    return db_execute("INSERT INTO services(name,description,price) VALUES(?,?,?)", (name,desc,price))

def update_service(sid, name, desc, price):
    db_execute("UPDATE services SET name=?, description=?, price=? WHERE id=?", (name,desc,price,sid))

def delete_service(sid):
    db_execute("DELETE FROM services WHERE id=?", (sid,))

def get_service_price(sid):
    result = db_fetchone("SELECT price FROM services WHERE id=?", (sid,))
    return result["price"] if result else 0.0

# --------------------------
# Appointment functions
# --------------------------
def add_appointment(patient_id, doctor_id, service_id, start_dt, end_dt, status="scheduled", notes=""):
    doctor = db_fetchone("SELECT * FROM doctors WHERE id=? AND is_available=1", (doctor_id,))
    if not doctor:
        return None, "Doctor is not available."
    
    service_price = get_service_price(service_id)
    
    overlapping = db_fetchone("""
        SELECT * FROM appointments
        WHERE doctor_id=? AND status IN ('scheduled','confirmed')
        AND NOT (end_datetime<=? OR start_datetime>=?)
    """, (doctor_id, start_dt, end_dt))
    if overlapping:
        return None, "Doctor has overlapping appointment at that time."
    
    aid = db_execute("""
        INSERT INTO appointments(patient_id,doctor_id,service_id,start_datetime,end_datetime,status,notes,total_amount)
        VALUES(?,?,?,?,?,?,?,?)
    """, (patient_id,doctor_id,service_id,start_dt,end_dt,status,notes,service_price))
    return aid, None

def update_appointment_status(aid, status):
    db_execute("UPDATE appointments SET status=? WHERE id=?", (status,aid))

def mark_appointment_completed(aid, payment_status, amount_paid):
    db_execute("""
        UPDATE appointments 
        SET is_completed=1, payment_status=?, amount_paid=?
        WHERE id=?
    """, (payment_status, amount_paid, aid))

def update_appointment_payment(aid, payment_status, amount_paid):
    db_execute("""
        UPDATE appointments 
        SET payment_status=?, amount_paid=?
        WHERE id=?
    """, (payment_status, amount_paid, aid))

def get_appointments(start=None, end=None):
    q = """SELECT a.*, 
                  p.first_name||' '||p.last_name AS patient_name, 
                  d.name AS doctor_name, 
                  s.name AS service_name,
                  s.price as service_price
           FROM appointments a 
           LEFT JOIN patients p ON p.id=a.patient_id 
           LEFT JOIN doctors d ON d.id=a.doctor_id 
           LEFT JOIN services s ON s.id=a.service_id"""
    params = ()
    if start and end:
        q += " WHERE start_datetime>=? AND start_datetime<?"
        params = (start,end)
    q += " ORDER BY start_datetime"
    return db_fetchall(q, params)

def get_appointment(aid):
    return db_fetchone("SELECT * FROM appointments WHERE id=?", (aid,))

def delete_appointment(aid):
    db_execute("DELETE FROM appointments WHERE id=?", (aid,))

def get_appointments_by_patient(patient_id):
    return db_fetchall("""
        SELECT a.*, d.name as doctor_name, s.name as service_name
        FROM appointments a
        LEFT JOIN doctors d ON d.id=a.doctor_id
        LEFT JOIN services s ON s.id=a.service_id
        WHERE a.patient_id=?
        ORDER BY a.start_datetime DESC
    """, (patient_id,))

# --------------------------
# Tooth records functions
# --------------------------
def update_tooth_records(patient_id, tooth_json):
    db_execute("UPDATE patients SET tooth_records=? WHERE id=?", (tooth_json, patient_id))

# --------------------------
# Auto Doctor Assignment
# --------------------------
def auto_assign_doctor(service_name):
    service_name_lower = service_name.lower()
    
    if any(word in service_name_lower for word in ['pediatric', 'child', 'kids']):
        specialty = 'Pediatric Dentistry'
    elif any(word in service_name_lower for word in ['braces', 'orthodontic', 'orthodontics']):
        specialty = 'Orthodontics'
    elif any(word in service_name_lower for word in ['surgery', 'extraction', 'wisdom']):
        specialty = 'Oral Surgery'
    elif any(word in service_name_lower for word in ['periodontics', 'gum']):
        specialty = 'Periodontics'
    else:
        specialty = 'General Dentistry'
    
    doctor = db_fetchone("""
        SELECT * FROM doctors 
        WHERE specialty LIKE ? AND is_available=1 
        ORDER BY RANDOM() LIMIT 1
    """, (f'%{specialty}%',))
    
    return doctor

# --------------------------
# Login Class
# --------------------------
class Login:
    USERNAME = "doctor"
    PASSWORD = "dentalclinic123"
    
    @staticmethod
    def authenticate(username, password):
        return username == Login.USERNAME and password == Login.PASSWORD

# --------------------------
# Login Window - FIXED SIZE
# --------------------------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Dental Clinic System - Login")
        # FIXED: Increased login window size
        self.geometry("500x450")
        self.resizable(False, False)
        
        self._center_window()
        self._create_widgets()
        
        create_tables()
        seed_defaults()
        
    def _center_window(self):
        self.update_idletasks()
        width = 500
        height = 450
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=30, pady=30, fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Dental Clinic System", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame, 
            text="Login to continue", 
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=(0, 40))
        
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        username_label = ctk.CTkLabel(form_frame, text="Username:", font=ctk.CTkFont(size=16))
        username_label.pack(pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=45, font=ctk.CTkFont(size=16))
        self.username_entry.pack(pady=(0, 20))
        
        password_label = ctk.CTkLabel(form_frame, text="Password:", font=ctk.CTkFont(size=16))
        password_label.pack(pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(form_frame, width=300, height=45, show="*", font=ctk.CTkFont(size=16))
        self.password_entry.pack(pady=(0, 30))
        
        login_button = ctk.CTkButton(
            form_frame, 
            text="Login", 
            command=self._login, 
            width=300, 
            height=45,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        login_button.pack(pady=(0, 10))
        
        self.username_entry.bind("<Return>", lambda event: self._login())
        self.password_entry.bind("<Return>", lambda event: self._login())
        
        self.username_entry.focus()
    
    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if Login.authenticate(username, password):
            self.destroy()
            app = MainApp()
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            self.password_entry.delete(0, 'end')

# --------------------------
# Main Application Window - FIXED SIZE
# --------------------------
class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Dental Clinic System")
        # FIXED: Increased main window size
        self.geometry("1400x750")
        
        self._center_window()
        self.current_user = {"username": Login.USERNAME, "role": "admin"}
        self._create_main_window()
        
    def _center_window(self):
        self.update_idletasks()
        width = 1400
        height = 750
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_main_window(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Dental Clinic", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        user_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text=f"User: {self.current_user['username']}",
            font=ctk.CTkFont(size=14)
        )
        user_label.grid(row=1, column=0, padx=20, pady=(0, 30))
        
        # Navigation buttons with larger fonts
        self.patients_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Patients", 
            command=self.show_patients,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.patients_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.appointments_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Appointments", 
            command=self.show_appointments,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.appointments_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.services_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Services & Prices", 
            command=self.show_services,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.services_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.doctors_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Doctors", 
            command=self.show_doctors,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.doctors_button.grid(row=5, column=0, padx=20, pady=10)
        
        self.tooth_records_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Tooth Records", 
            command=self.show_tooth_records_main,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.tooth_records_button.grid(row=6, column=0, padx=20, pady=10)
        
        self.tooth_reference_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Tooth Reference", 
            command=self.show_tooth_reference,
            height=45,
            font=ctk.CTkFont(size=15)
        )
        self.tooth_reference_button.grid(row=7, column=0, padx=20, pady=10)
        
        logout_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Logout", 
            command=self.logout,
            height=45,
            font=ctk.CTkFont(size=15),
            fg_color="red",
            hover_color="darkred"
        )
        logout_button.grid(row=8, column=0, padx=20, pady=(20, 30))
        
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        self.show_patients()
    
    def logout(self):
        self.destroy()
        login_window = LoginWindow()
        login_window.mainloop()
    
    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    # ---------- Patients View ----------
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
        
        for row in get_patients():
            name = f"{row['last_name']}, {row['first_name']}"
            tooth_count = 0
            if row["tooth_records"]:
                try:
                    records = json.loads(row["tooth_records"])
                    tooth_count = len(records)
                except:
                    tooth_count = get_tooth_count_for_age(row["age"])
            else:
                tooth_count = get_tooth_count_for_age(row["age"])
            
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
        
        # ADDED: Finish Patient button
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
        """Mark a patient's treatment as complete - NEW FUNCTION"""
        patient = get_patient(patient_id)
        if not patient:
            messagebox.showerror("Error", "Patient not found")
            return
        
        # Get all pending appointments for this patient
        appointments = get_appointments_by_patient(patient_id)
        pending_appointments = [apt for apt in appointments if apt["is_completed"] == 0]
        
        if pending_appointments:
            response = messagebox.askyesno(
                "Pending Appointments",
                f"Patient has {len(pending_appointments)} pending appointment(s).\n\n"
                "Do you want to mark all appointments as completed and finish treatment?"
            )
            
            if response:
                # Mark all pending appointments as completed
                for apt in pending_appointments:
                    mark_appointment_completed(apt["id"], "paid", apt["total_amount"])
                
                messagebox.showinfo(
                    "Success", 
                    f"Treatment completed for {patient['first_name']} {patient['last_name']}.\n"
                    f"{len(pending_appointments)} appointment(s) marked as completed."
                )
                return
        
        # If no pending appointments or user said no
        response = messagebox.askyesno(
            "Finish Treatment",
            f"Mark treatment as complete for {patient['first_name']} {patient['last_name']}?\n\n"
            "Note: This will not affect appointments."
        )
        
        if response:
            # Add completion note to patient record
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
        for apt in appointments:
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
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        def close_window():
            window.destroy()
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=close_window,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        close_button.pack()
    
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

    # ---------- Doctors View ----------
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
                # FIXED: Using renamed function remove_doctor
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
        
        # FIXED: Name field
        name_label = ctk.CTkLabel(fields_frame, text="Full Name:", font=ctk.CTkFont(size=14))
        name_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))
        name_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        name_entry.grid(row=0, column=1, padx=10, pady=(15, 5))
        
        # FIXED: Specialty field - Simplified approach
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
        
        # Create combobox without StringVar first
        specialty_combobox = ctk.CTkComboBox(fields_frame, values=specialties, width=350, height=40)
        specialty_combobox.grid(row=1, column=1, padx=10, pady=5)
        
        # FIXED: Contact field
        contact_label = ctk.CTkLabel(fields_frame, text="Contact Number:", font=ctk.CTkFont(size=14))
        contact_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        contact_entry = ctk.CTkEntry(fields_frame, width=350, height=40)
        contact_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # FIXED: Availability field
        availability_label = ctk.CTkLabel(fields_frame, text="Availability:", font=ctk.CTkFont(size=14))
        availability_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        availability_var = ctk.BooleanVar(value=True)
        availability_checkbox = ctk.CTkCheckBox(fields_frame, text="Available for appointments", 
                                               variable=availability_var, font=ctk.CTkFont(size=14))
        availability_checkbox.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # If editing, populate fields
        if doctor_id:
            doctor = db_fetchone("SELECT * FROM doctors WHERE id=?", (doctor_id,))
            if doctor:
                name_entry.insert(0, doctor["name"])
                specialty_combobox.set(doctor["specialty"])
                contact_entry.insert(0, doctor["contact"])
                availability_var.set(doctor["is_available"] == 1)
        else:
            # Set default for new doctor
            specialty_combobox.set("General Dentistry")
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def save_doctor():
            name = name_entry.get().strip()
            specialty = specialty_combobox.get().strip()  # FIXED: Using get() method directly
            contact = contact_entry.get().strip()
            is_available = 1 if availability_var.get() else 0
            
            if not name:
                messagebox.showerror("Missing", "Doctor name is required")
                return
            if not specialty:
                messagebox.showerror("Missing", "Specialty is required")
                return
            if not contact:
                messagebox.showerror("Missing", "Contact number is required")
                return
            
            if doctor_id:
                update_doctor(doctor_id, name, specialty, contact, is_available)
                messagebox.showinfo("Saved", "Doctor updated successfully")
            else:
                add_doctor(name, specialty, contact, is_available)
                messagebox.showinfo("Saved", "Doctor added successfully")
            
            form_window.destroy()
            self._refresh_doctors_tree()
        
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

    # ---------- Services & Prices ----------
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

    # ---------- Appointments ----------
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
        status_combobox = ctk.CTkComboBox(filter_frame, values=["all", "scheduled", "confirmed", "completed", "cancelled"], 
                                         variable=self.status_var, width=180, height=40)
        status_combobox.grid(row=0, column=3, padx=5, pady=10)
        
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
            rows = get_appointments(start, end)
            
            for i in self.appointments_tree.get_children():
                self.appointments_tree.delete(i)
            
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
        
        def delete_appointment():
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
            dialog.geometry("500x300")
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
            
            info_label = ctk.CTkLabel(
                main_frame,
                text=f"Total Amount: ₱{appointment['total_amount']:.2f}",
                font=ctk.CTkFont(size=16)
            )
            info_label.pack(pady=(0, 20))
            
            status_label = ctk.CTkLabel(main_frame, text="Payment Status:", font=ctk.CTkFont(size=14))
            status_label.pack(pady=(10, 5))
            
            status_var = ctk.StringVar(value=appointment["payment_status"])
            status_combobox = ctk.CTkComboBox(main_frame, values=["paid", "partial", "pending"], 
                                             variable=status_var, width=250, height=40)
            status_combobox.pack(pady=(0, 15))
            
            amount_label = ctk.CTkLabel(main_frame, text="Amount Paid (₱):", font=ctk.CTkFont(size=14))
            amount_label.pack(pady=(15, 5))
            
            amount_var = ctk.DoubleVar(value=appointment["amount_paid"])
            amount_entry = ctk.CTkEntry(main_frame, textvariable=amount_var, width=250, height=40)
            amount_entry.pack(pady=(0, 25))
            
            def save_payment():
                payment_status = status_var.get()
                amount_paid = amount_var.get()
                
                if amount_paid < 0:
                    messagebox.showerror("Invalid", "Amount cannot be negative")
                    return
                
                if amount_paid > appointment["total_amount"]:
                    messagebox.showwarning("Warning", f"Amount paid (₱{amount_paid:.2f}) exceeds total (₱{appointment['total_amount']:.2f})")
                
                update_appointment_payment(aid, payment_status, amount_paid)
                messagebox.showinfo("Success", f"Payment updated for appointment #{aid}")
                dialog.destroy()
                refresh_appointments()
            
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(pady=10)
            
            save_button = ctk.CTkButton(
                button_frame,
                text="Update Payment",
                command=save_payment,
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
            command=delete_appointment,
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
        
        refresh_appointments()

    def appointment_form(self, appointment_id=None):
        form_window = ctk.CTkToplevel(self)
        if appointment_id:
            form_window.title("Edit Appointment")
            is_edit = True
        else:
            form_window.title("New Appointment")
            is_edit = False
        form_window.geometry("700x800")
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
        
        if not is_edit:
            def auto_assign():
                service_str = service_var.get()
                if not service_str:
                    messagebox.showinfo("Select Service", "Please select a service first")
                    return
                
                service_name = service_str.split(":")[1].strip()
                
                doctor = auto_assign_doctor(service_name)
                if doctor:
                    for i, doc_option in enumerate(doctor_options):
                        if str(doctor["id"]) in doc_option:
                            doctor_var.set(doc_option)
                            messagebox.showinfo("Auto Assignment", 
                                              f"Auto-assigned: Dr. {doctor['name']} ({doctor['specialty']})")
                            return
                    
                    messagebox.showinfo("No Match", "Auto-assigned doctor is not in available list")
                else:
                    messagebox.showinfo("No Doctor", "No suitable doctor available for this service")
            
            auto_button = ctk.CTkButton(
                main_frame,
                text="Auto Assign Doctor",
                command=auto_assign,
                width=220,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="green",
                hover_color="darkgreen"
            )
            auto_button.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        patient_label = ctk.CTkLabel(main_frame, text="Patient:", font=ctk.CTkFont(size=14))
        patient_label.grid(row=1, column=0, sticky="w", padx=15, pady=(10, 5))
        
        patients = get_patients()
        patient_options = [f"{p['id']}: {p['last_name']}, {p['first_name']}" for p in patients]
        patient_var = ctk.StringVar()
        patient_combobox = ctk.CTkComboBox(main_frame, values=patient_options, 
                                          variable=patient_var, width=350, height=40)
        patient_combobox.grid(row=1, column=1, padx=15, pady=(10, 5))
        
        doctor_label = ctk.CTkLabel(main_frame, text="Doctor:", font=ctk.CTkFont(size=14))
        doctor_label.grid(row=2, column=0, sticky="w", padx=15, pady=10)
        
        all_doctors = get_doctors()
        doctor_options = []
        for d in all_doctors:
            status = "✅" if d["is_available"] == 1 else "❌"
            doctor_options.append(f"{d['id']}: {d['name']} ({d['specialty']}) {status}")
        
        doctor_var = ctk.StringVar()
        doctor_combobox = ctk.CTkComboBox(main_frame, values=doctor_options, 
                                         variable=doctor_var, width=350, height=40)
        doctor_combobox.grid(row=2, column=1, padx=15, pady=10)
        
        service_label = ctk.CTkLabel(main_frame, text="Service:", font=ctk.CTkFont(size=14))
        service_label.grid(row=3, column=0, sticky="w", padx=15, pady=10)
        
        services = get_services()
        service_options = [f"{s['id']}: {s['name']} (₱{s['price']:.2f})" for s in services]
        service_var = ctk.StringVar()
        service_combobox = ctk.CTkComboBox(main_frame, values=service_options, 
                                          variable=service_var, width=350, height=40)
        service_combobox.grid(row=3, column=1, padx=15, pady=10)
        
        date_label = ctk.CTkLabel(main_frame, text="Date (YYYY-MM-DD):", font=ctk.CTkFont(size=14))
        date_label.grid(row=4, column=0, sticky="w", padx=15, pady=10)
        date_entry = ctk.CTkEntry(main_frame, width=350, height=40)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=4, column=1, padx=15, pady=10)
        
        time_label = ctk.CTkLabel(main_frame, text="Time (HH:MM):", font=ctk.CTkFont(size=14))
        time_label.grid(row=5, column=0, sticky="w", padx=15, pady=10)
        time_entry = ctk.CTkEntry(main_frame, width=350, height=40)
        time_entry.insert(0, "09:00")
        time_entry.grid(row=5, column=1, padx=15, pady=10)
        
        duration_label = ctk.CTkLabel(main_frame, text="Duration (minutes):", font=ctk.CTkFont(size=14))
        duration_label.grid(row=6, column=0, sticky="w", padx=15, pady=10)
        duration_var = ctk.IntVar(value=30)
        duration_entry = ctk.CTkEntry(main_frame, textvariable=duration_var, width=350, height=40)
        duration_entry.grid(row=6, column=1, padx=15, pady=10)
        
        status_label = ctk.CTkLabel(main_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.grid(row=7, column=0, sticky="w", padx=15, pady=10)
        status_var = ctk.StringVar(value="scheduled")
        status_combobox = ctk.CTkComboBox(main_frame, values=["scheduled", "confirmed", "cancelled"], 
                                         variable=status_var, width=350, height=40)
        status_combobox.grid(row=7, column=1, padx=15, pady=10)
        
        notes_label = ctk.CTkLabel(main_frame, text="Notes:", font=ctk.CTkFont(size=14))
        notes_label.grid(row=8, column=0, sticky="nw", padx=15, pady=10)
        notes_text = ctk.CTkTextbox(main_frame, width=350, height=120)
        notes_text.grid(row=8, column=1, padx=15, pady=10)
        
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
                    time_entry.delete(0, 'end')
                    time_entry.insert(0, start_dt.strftime("%H:%M"))
                    
                    if appointment["end_datetime"]:
                        end_dt = datetime.strptime(appointment["end_datetime"], "%Y-%m-%d %H:%M:%S")
                        duration = int((end_dt - start_dt).total_seconds() / 60)
                        duration_var.set(duration)
                except:
                    pass
                
                status_var.set(appointment["status"])
                notes_text.insert("1.0", appointment["notes"] or "")
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=25)
        
        def save_appointment():
            patient_str = patient_var.get()
            doctor_str = doctor_var.get()
            service_str = service_var.get()
            date_str = date_entry.get().strip()
            time_str = time_entry.get().strip()
            duration = duration_var.get()
            status = status_var.get()
            notes = notes_text.get("1.0", "end").strip()
            
            if not patient_str or not doctor_str or not service_str:
                messagebox.showerror("Missing", "Please select patient, doctor, and service")
                return
            
            try:
                patient_id = int(patient_str.split(":")[0])
                doctor_id = int(doctor_str.split(":")[0])
                service_id = int(service_str.split(":")[0])
            except:
                messagebox.showerror("Error", "Invalid selection")
                return
            
            try:
                start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except:
                messagebox.showerror("Date", "Invalid date/time format")
                return
            
            end_dt = start_dt + timedelta(minutes=duration)
            
            if appointment_id:
                messagebox.showinfo("Info", "Edit functionality requires additional implementation")
                form_window.destroy()
            else:
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
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_appointment,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=form_window.destroy,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.pack(side="left", padx=10)

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
            tooth_info = records.get(tooth_id, {"status": "unknown", "notes": "", "present": True})
            status = tooth_info.get("status", "unknown")
            
            if status == "healthy":
                button_color = "green"
            elif status == "cavity":
                button_color = "red"
            elif status == "filling":
                button_color = "blue"
            elif status == "extracted":
                button_color = "gray"
            else:
                button_color = "gray"
            
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
        p = get_patient(patient_id)
        if not p:
            return
        
        records = {}
        if p["tooth_records"]:
            try:
                records = json.loads(p["tooth_records"])
            except:
                records = {}
        
        tooth_info = records.get(tooth_id, {"status": "unknown", "notes": "", "present": True})
        
        dialog = ctk.CTkToplevel(parent_window)
        dialog.title(f"Edit Tooth {tooth_id}")
        dialog.geometry("500x350")
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
        
        status_label = ctk.CTkLabel(main_frame, text="Status:", font=ctk.CTkFont(size=14))
        status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))
        
        status_var = ctk.StringVar(value=tooth_info.get("status", "unknown"))
        status_options = ["healthy", "cavity", "filling", "extracted", "unknown"]
        status_combobox = ctk.CTkComboBox(main_frame, values=status_options, 
                                         variable=status_var, width=250, height=40)
        status_combobox.grid(row=0, column=1, padx=10, pady=(15, 5))
        
        present_var = ctk.BooleanVar(value=tooth_info.get("present", True))
        present_checkbox = ctk.CTkCheckBox(main_frame, text="Tooth is present", 
                                          variable=present_var, font=ctk.CTkFont(size=14))
        present_checkbox.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        notes_label = ctk.CTkLabel(main_frame, text="Notes:", font=ctk.CTkFont(size=14))
        notes_label.grid(row=2, column=0, sticky="nw", padx=10, pady=10)
        
        notes_text = ctk.CTkTextbox(main_frame, width=250, height=120)
        notes_text.insert("1.0", tooth_info.get("notes", ""))
        notes_text.grid(row=2, column=1, padx=10, pady=10)
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_tooth():
            records[tooth_id] = {
                "status": status_var.get(),
                "notes": notes_text.get("1.0", "end").strip(),
                "present": present_var.get()
            }
            
            update_tooth_records(patient_id, json.dumps(records))
            
            messagebox.showinfo("Saved", f"Tooth {tooth_id} updated")
            dialog.destroy()
            parent_window.destroy()
            self.show_tooth_editor(patient_id)
        
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_tooth,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.pack(side="left", padx=10)

# --------------------------
# Run the application
# --------------------------
if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()