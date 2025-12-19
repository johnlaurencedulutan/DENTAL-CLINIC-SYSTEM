# database.py
import sqlite3
import json
from datetime import datetime, timedelta
from models import DB_FILE, DEFAULT_SERVICES, DEFAULT_DOCTORS, get_appropriate_tooth_set_for_age, get_tooth_count_for_age

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def check_and_fix_database():
    """Check and fix database schema issues"""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("PRAGMA table_info(doctors)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_available' not in column_names:
            print("Fixing database: adding is_available column...")
            c.execute("ALTER TABLE doctors ADD COLUMN is_available INTEGER DEFAULT 1")
            conn.commit()
            print("Database fixed successfully!")
        
        # Check and fix other tables if needed (no diagnosis/medicine auto-add here)
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
        FOREIGN KEY(service_id) REFERENCES services(id) ON DELETE CASCADE
    )
    """)
    
    # Payment transactions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS payment_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        patient_id INTEGER,
        transaction_date TEXT,
        payment_method TEXT,
        amount REAL,
        description TEXT,
        reference_number TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(appointment_id) REFERENCES appointments(id),
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    
    # Insurance table
    c.execute("""
    CREATE TABLE IF NOT EXISTS patient_insurance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        insurance_provider TEXT,
        policy_number TEXT,
        coverage_amount REAL,
        valid_until TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    
    # Recycle bin for soft-deleted records
    c.execute("""
    CREATE TABLE IF NOT EXISTS recycle_bin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT,
        row_id INTEGER,
        data_json TEXT,
        deleted_at TEXT
    )
    """)
    
    # Archived appointments for overdue/cancelled appointments
    c.execute("""
    CREATE TABLE IF NOT EXISTS archived_appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_id INTEGER,
        patient_id INTEGER,
        doctor_id INTEGER,
        service_id INTEGER,
        start_datetime TEXT,
        end_datetime TEXT,
        original_status TEXT,
        notes TEXT,
        is_completed INTEGER,
        payment_status TEXT,
        amount_paid REAL,
        total_amount REAL,
        archived_at TEXT,
        archived_reason TEXT DEFAULT 'overdue',
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id),
        FOREIGN KEY(service_id) REFERENCES services(id)
    )
    """)
    
    conn.commit()
    conn.close()
    
def seed_defaults():
    conn = get_connection()
    c = conn.cursor()
    
    # Check and seed services
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        for s in DEFAULT_SERVICES:
            c.execute("INSERT INTO services(name,description,price) VALUES(?,?,?)", s)
    
    # Check and seed doctors
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        for d in DEFAULT_DOCTORS:
            c.execute("INSERT INTO doctors(name,specialty,contact,is_available) VALUES(?,?,?,?)", d)
    
    # Check and seed patients
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
    try:
        c.execute(query, params)
        conn.commit()
        last_id = c.lastrowid
        return last_id
    except Exception as e:
        print(f"Database error in db_execute: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        raise e
    finally:
        conn.close()

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
                    filtered_records[tooth_id] = {"status": "healthy", "notes": "", "present": True}
                    
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
        "UPDATE patients SET first_name=?, last_name=?, age=?, type=?, contact=?, notes=? WHERE id= ?",
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
    move_to_recycle("patients", pid)

def get_patients():
    return db_fetchall("SELECT * FROM patients ORDER BY id ASC")

def get_patient(pid):
    return db_fetchone("SELECT * FROM patients WHERE id=?", (pid,))

def add_doctor(name, specialty, contact, is_available=1):
    return db_execute("INSERT INTO doctors(name,specialty,contact,is_available) VALUES(?,?,?,?)",
                      (name,specialty,contact,is_available))

def get_doctors():
    return db_fetchall("SELECT * FROM doctors ORDER BY id ASC")

def get_available_doctors():
    return db_fetchall("SELECT * FROM doctors WHERE is_available=1 ORDER BY name")

def update_doctor(did, name, specialty, contact, is_available):
    db_execute("UPDATE doctors SET name=?, specialty=?, contact=?, is_available=? WHERE id=?",
               (name,specialty,contact,is_available,did))

def toggle_doctor_availability(did, is_available):
    db_execute("UPDATE doctors SET is_available=? WHERE id=?", (is_available,did))

def update_doctor_availability_auto():
    """Automatically update doctor availability based on scheduled appointments."""
    doctors = get_doctors()
    
    for doctor in doctors:
        result = db_fetchone(
            "SELECT COUNT(*) as count FROM appointments WHERE doctor_id=? AND status IN ('scheduled','confirmed') AND is_completed=0",
            (doctor['id'],)
        )

        pending_count = result['count'] if result else 0
        should_be_available = 0 if pending_count > 0 else 1

        if doctor['is_available'] != should_be_available:
            db_execute("UPDATE doctors SET is_available=? WHERE id=?", (should_be_available, doctor['id']))

def remove_doctor(did):
    """Delete a doctor and their appointments"""
    from tkinter import messagebox
    
    appointments = db_fetchall("SELECT * FROM appointments WHERE doctor_id=?", (did,))
    if appointments:
        response = messagebox.askyesno(
            "Doctor has Appointments",
            f"This doctor has {len(appointments)} appointment(s).\n\nDelete doctor and all appointments?"
        )
        if response:
            for a in appointments:
                move_to_recycle("appointments", a["id"])
        else:
            return False
    
    move_to_recycle("doctors", did)
    return True

def get_doctor_appointment_count(did):
    result = db_fetchone("SELECT COUNT(*) as count FROM appointments WHERE doctor_id=?", (did,))
    return result["count"] if result else 0

def get_services():
    return db_fetchall("SELECT * FROM services ORDER BY id ASC")

def add_service(name, desc, price):
    return db_execute("INSERT INTO services(name,description,price) VALUES(?,?,?)", (name,desc,price))

def update_service(sid, name, desc, price):
    db_execute("UPDATE services SET name=?, description=?, price=? WHERE id=?", (name,desc,price,sid))

def delete_service(sid):
    move_to_recycle("services", sid)

def get_service_price(sid):
    result = db_fetchone("SELECT price FROM services WHERE id=?", (sid,))
    return result["price"] if result else 0.0

def add_appointment(patient_id, doctor_id, service_id, start_dt, end_dt, status="scheduled", notes=""):
    """Add a new appointment to the database"""
    # Convert to strings if datetime objects are passed
    if hasattr(start_dt, 'strftime'):
        start_dt_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        start_dt_str = str(start_dt)
    
    if hasattr(end_dt, 'strftime'):
        end_dt_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        end_dt_str = str(end_dt)
    
    # Validate doctor availability
    doctor = db_fetchone("SELECT * FROM doctors WHERE id=? AND is_available=1", (doctor_id,))
    if not doctor:
        return None, "Doctor is not available."

    # Get service price
    service_price = get_service_price(service_id)
    if service_price is None:
        return None, "Service not found or has no price."

    # Check for overlapping appointments
    overlapping = db_fetchone("""
        SELECT * FROM appointments
        WHERE doctor_id=? AND status IN ('scheduled','confirmed')
        AND NOT (end_datetime<=? OR start_datetime>=?)
    """, (doctor_id, start_dt_str, end_dt_str))
    
    if overlapping:
        return None, "Doctor has overlapping appointment at that time."

    try:
        aid = db_execute("""
            INSERT INTO appointments(
                patient_id, doctor_id, service_id, 
                start_datetime, end_datetime, status, notes,
                total_amount
            ) VALUES(?,?,?,?,?,?,?,?)
        """, (
            patient_id, doctor_id, service_id, 
            start_dt_str, end_dt_str, status, notes,
            service_price
        ))
        
        # Auto-update doctor availability
        update_doctor_availability_auto()
        
        return aid, None
    except Exception as e:
        return None, f"Database error: {str(e)}"

def update_appointment_status(aid, status):
    db_execute("UPDATE appointments SET status=? WHERE id=?", (status, aid))
    update_doctor_availability_auto()

def mark_appointment_completed(aid, payment_status, amount_paid):
    db_execute("""
        UPDATE appointments 
        SET is_completed=1, payment_status=?, amount_paid=?
        WHERE id=?
    """, (payment_status, amount_paid, aid))
    update_doctor_availability_auto()

def update_appointment_payment(aid, payment_status, amount_paid):
    db_execute("""
        UPDATE appointments 
        SET payment_status=?, amount_paid=?
        WHERE id=?
    """, (payment_status, amount_paid, aid))

def update_appointment_details(aid, patient_id, doctor_id, service_id, start_dt, end_dt, status, notes):
    """Update appointment details"""
    # Convert to strings if datetime objects are passed
    if hasattr(start_dt, 'strftime'):
        start_dt = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(end_dt, 'strftime'):
        end_dt = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    service_price = get_service_price(service_id)
    
    db_execute("""
        UPDATE appointments 
        SET patient_id=?, doctor_id=?, service_id=?, 
            start_datetime=?, end_datetime=?, status=?, notes=?,
            total_amount=?
        WHERE id=?
    """, (patient_id, doctor_id, service_id, start_dt, end_dt, 
          status, notes, service_price, aid))
    
    update_doctor_availability_auto()

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
        params = (start, end)
    q += " ORDER BY start_datetime"
    return db_fetchall(q, params)

def get_appointment(aid):return db_fetchone("""SELECT a.*, s.name as service_name FROM appointments a LEFT JOIN services s ON s.id = a.service_id WHERE a.id=? """, (aid,))

def delete_appointment(aid):
    move_to_recycle("appointments", aid)
    update_doctor_availability_auto()

def get_appointments_by_patient(patient_id):
    return db_fetchall("""
        SELECT a.*, d.name as doctor_name, s.name as service_name
        FROM appointments a
        LEFT JOIN doctors d ON d.id=a.doctor_id
        LEFT JOIN services s ON s.id=a.service_id
        WHERE a.patient_id=?
        ORDER BY a.start_datetime DESC
    """, (patient_id,))

def update_tooth_records(patient_id, tooth_json):
    db_execute("UPDATE patients SET tooth_records=? WHERE id=?", (tooth_json, patient_id))

def auto_assign_doctor(service_name, start_dt=None, end_dt=None):
    """Auto-assign a doctor based on service specialty and availability."""
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

    # If start/end not provided, fallback to random available doctor
    if not start_dt or not end_dt:
        doctor = db_fetchone("""
            SELECT * FROM doctors 
            WHERE specialty LIKE ? AND is_available=1 
            ORDER BY RANDOM() LIMIT 1
        """, (f'%{specialty}%',))
        return doctor

    # Convert to strings if datetime objects
    if hasattr(start_dt, 'strftime'):
        start_str = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        start_str = str(start_dt)

    if hasattr(end_dt, 'strftime'):
        end_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        end_str = str(end_dt)

    # Query candidate doctors and check for overlaps
    candidates = db_fetchall("SELECT * FROM doctors WHERE specialty LIKE ? AND is_available=1", (f'%{specialty}%',))
    for doc in candidates:
        overlap = db_fetchone("""
            SELECT COUNT(*) as count FROM appointments
            WHERE doctor_id=? AND status IN ('scheduled','confirmed')
            AND NOT (end_datetime<=? OR start_datetime>=?)
        """, (doc['id'], start_str, end_str))

        if not overlap or overlap['count'] == 0:
            return doc

    # No available doctor for the requested slot
    return None

def move_to_recycle(table_name, row_id):
    """Soft delete: move record to recycle bin."""
    row = db_fetchone(f"SELECT * FROM {table_name} WHERE id=?", (row_id,))
    if not row:
        return False

    row_dict = {k: row[k] for k in row.keys()}
    data_json = json.dumps(row_dict)
    deleted_at = datetime.utcnow().isoformat()

    db_execute("INSERT INTO recycle_bin(table_name,row_id,data_json,deleted_at) VALUES(?,?,?,?)",
               (table_name, row_id, data_json, deleted_at))
    
    db_execute(f"DELETE FROM {table_name} WHERE id=?", (row_id,))
    return True

def get_recycle_items():
    return db_fetchall("SELECT * FROM recycle_bin ORDER BY deleted_at DESC")

def restore_recycle_item(rid):
    item = db_fetchone("SELECT * FROM recycle_bin WHERE id=?", (rid,))
    if not item:
        return False, "Not found"

    data = json.loads(item["data_json"])
    table = item["table_name"]

    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data.keys()])
    values = tuple(data.values())

    try:
        db_execute(f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})", values)
    except Exception as e:
        return False, str(e)

    db_execute("DELETE FROM recycle_bin WHERE id=?", (rid,))
    return True, "Record restored successfully"

def permanently_delete_recycle_item(rid):
    db_execute("DELETE FROM recycle_bin WHERE id=?", (rid,))
    return True

# OVERDUE APPOINTMENTS FUNCTIONS
def check_overdue_appointments():
    """Check for appointments that are overdue and mark them"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Find scheduled appointments that have passed their end time
        c.execute("""
            SELECT a.* 
            FROM appointments a
            WHERE a.status IN ('scheduled', 'confirmed')
            AND a.end_datetime < ?
        """, (current_time,))
        
        overdue_appointments = c.fetchall()
        
        count = 0
        for apt in overdue_appointments:
            try:
                # Archive the appointment
                c.execute("""
                    INSERT INTO archived_appointments (
                        original_id, patient_id, doctor_id, service_id,
                        start_datetime, end_datetime, original_status,
                        notes, is_completed, payment_status, amount_paid,
                        total_amount, archived_at, archived_reason
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    apt["id"], apt["patient_id"], apt["doctor_id"], apt["service_id"],
                    apt["start_datetime"], apt["end_datetime"], apt["status"],
                    apt["notes"], apt["is_completed"], apt["payment_status"],
                    apt["amount_paid"], apt["total_amount"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "overdue"
                ))
                
                # Update status to overdue
                c.execute("UPDATE appointments SET status='overdue' WHERE id=?", (apt["id"],))
                count += 1
            except Exception as e:
                print(f"Error processing appointment {apt['id']}: {e}")
        
        if count > 0:
            conn.commit()
            print(f"Marked {count} appointment(s) as overdue")
        
        conn.close()
        return count
    except Exception as e:
        print(f"Error checking overdue appointments: {e}")
        return 0

def get_overdue_appointments():
    """Get all overdue appointments"""
    return db_fetchall("""
        SELECT a.*, 
               p.first_name||' '||p.last_name AS patient_name,
               d.name AS doctor_name,
               s.name AS service_name
        FROM appointments a 
        LEFT JOIN patients p ON p.id=a.patient_id
        LEFT JOIN doctors d ON d.id=a.doctor_id
        LEFT JOIN services s ON s.id=a.service_id
        WHERE a.status = 'overdue'
        ORDER BY a.end_datetime ASC
    """)

def get_archived_appointments():
    """Get all archived appointments"""
    return db_fetchall("""
        SELECT a.*, 
               p.first_name||' '||p.last_name AS patient_name,
               d.name AS doctor_name,
               s.name AS service_name
        FROM archived_appointments a 
        LEFT JOIN patients p ON p.id=a.patient_id
        LEFT JOIN doctors d ON d.id=a.doctor_id
        LEFT JOIN services s ON s.id=a.service_id
        ORDER BY a.archived_at DESC
    """)

def manually_check_overdue():
    """Manual function to check overdue appointments"""
    count = check_overdue_appointments()
    return count

# PAYMENT SYSTEM FUNCTIONS
def add_payment_transaction(appointment_id, patient_id, payment_method, amount, description="", reference_number=""):
    """Add a payment transaction"""
    return db_execute("""
        INSERT INTO payment_transactions (appointment_id, patient_id, transaction_date, 
                                         payment_method, amount, description, reference_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (appointment_id, patient_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          payment_method, amount, description, reference_number))

def get_payment_transactions(patient_id=None, appointment_id=None):
    """Get payment transactions with filters"""
    query = """
        SELECT pt.*, 
               p.first_name||' '||p.last_name AS patient_name,
               a.id as appointment_id
        FROM payment_transactions pt
        LEFT JOIN patients p ON p.id=pt.patient_id
        LEFT JOIN appointments a ON a.id=pt.appointment_id
        WHERE 1=1
    """
    params = []
    
    if patient_id:
        query += " AND pt.patient_id=?"
        params.append(patient_id)
    
    if appointment_id:
        query += " AND pt.appointment_id=?"
        params.append(appointment_id)
    
    query += " ORDER BY pt.transaction_date DESC"
    
    return db_fetchall(query, params)

def get_patient_balance(patient_id):
    """Get patient's outstanding balance"""
    appointments = db_fetchall("""
        SELECT * FROM appointments 
        WHERE patient_id=? AND is_completed=1
    """, (patient_id,))
    
    total_balance = 0
    for apt in appointments:
        balance = apt["total_amount"] - apt["amount_paid"]
        if balance > 0:
            total_balance += balance
    
    return total_balance

def add_patient_insurance(patient_id, provider, policy_number, coverage_amount, valid_until, notes=""):
    """Add insurance information for a patient"""
    return db_execute("""
        INSERT INTO patient_insurance (patient_id, insurance_provider, policy_number, 
                                      coverage_amount, valid_until, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, provider, policy_number, coverage_amount, valid_until, notes))

def get_patient_insurance(patient_id):
    """Get insurance information for a patient"""
    return db_fetchall("SELECT * FROM patient_insurance WHERE patient_id=?", (patient_id,))

def update_appointment_discount(appointment_id, discount_amount):
    """Apply discount to an appointment"""
    appointment = get_appointment(appointment_id)
    if not appointment:
        return False
    
    return True

def get_daily_payments(date=None):
    """Get daily payment summary"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    return db_fetchall("""
        SELECT 
            DATE(transaction_date) as payment_date,
            payment_method,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount
        FROM payment_transactions
        WHERE DATE(transaction_date) = ?
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """, (date,))

def get_monthly_payments(year=None, month=None):
    """Get monthly payment summary"""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    return db_fetchall("""
        SELECT 
            strftime('%Y-%m', transaction_date) as payment_month,
            payment_method,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount
        FROM payment_transactions
        WHERE strftime('%Y', transaction_date) = ? 
          AND strftime('%m', transaction_date) = ?
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """, (str(year), f"{month:02d}"))

def generate_receipt(appointment_id):
    """Generate receipt text for an appointment"""
    appointment = get_appointment(appointment_id)
    if not appointment:
        return None
    
    patient = get_patient(appointment["patient_id"])
    if not patient:
        return None
    
    transactions = get_payment_transactions(appointment_id=appointment_id)
    
    receipt = f"""
    =============================================
                DENTAL CLINIC RECEIPT
    =============================================
    Receipt #: {appointment_id:06d}
    Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    Patient: {patient['first_name']} {patient['last_name']}
    Contact: {patient['contact']}
    
    Service: {appointment['service_name'] if appointment['service_name'] else 'Consultation'}
    Original Amount: ₱{appointment['total_amount']:.2f}
    Amount Paid: ₱{appointment['amount_paid']:.2f}
    Balance Due: ₱{appointment['total_amount'] - appointment['amount_paid']:.2f}
    Payment Status: {appointment['payment_status'].upper()}
    
    --- Payment Transactions ---
    """
    
    if transactions:
        for i, trans in enumerate(transactions, 1):
            receipt += f"\n{i}. {trans['transaction_date'][:16]} - {trans['payment_method']}: ₱{trans['amount']:.2f}"
            if trans['reference_number']:
                receipt += f" (Ref: {trans['reference_number']})"
    else:
        receipt += "\nPayment transactions recorded."
    
    receipt += f"""
    
    Thank you for your payment!
    =============================================
    """
    
    return receipt

def get_outstanding_payments():
    """Get all appointments with outstanding payments"""
    return db_fetchall("""
        SELECT a.*,
               p.first_name||' '||p.last_name AS patient_name,
               d.name AS doctor_name,
               s.name AS service_name,
               (a.total_amount - a.amount_paid) as balance_due
        FROM appointments a
        LEFT JOIN patients p ON p.id=a.patient_id
        LEFT JOIN doctors d ON d.id=a.doctor_id
        LEFT JOIN services s ON s.id=a.service_id
        WHERE a.is_completed=1 
          AND (a.total_amount - a.amount_paid) > 0
        ORDER BY balance_due DESC
    """)

def apply_payment_to_appointment(appointment_id, payment_method, amount, description="", reference_number=""):
    """Apply payment to an appointment and record transaction"""
    appointment = get_appointment(appointment_id)
    if not appointment:
        return False, "Appointment not found"
    
    # Record payment transaction
    add_payment_transaction(appointment_id, appointment["patient_id"], 
                           payment_method, amount, description, reference_number)
    
    # Update appointment payment
    new_amount_paid = appointment["amount_paid"] + amount
    update_appointment_payment(appointment_id, "partial" if new_amount_paid < appointment["total_amount"] else "paid", 
                              new_amount_paid)
    
    return True, "Payment applied successfully"

def initialize_database():
    """Initialize database with all tables and defaults"""
    print("Initializing database...")
    create_tables()
    check_and_fix_database()
    seed_defaults()
    print("Database initialized successfully!")