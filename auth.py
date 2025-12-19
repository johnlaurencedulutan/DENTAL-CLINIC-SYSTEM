# auth.py
import customtkinter as ctk
from tkinter import messagebox
from database import create_tables, seed_defaults, get_connection, db_fetchone, check_and_fix_database

class Login:
    USERNAME = "doctor"
    PASSWORD = "dentalclinic123"
    
    @staticmethod
    def authenticate(username, password):
        """Fallback authentication with hardcoded credentials"""
        return username == Login.USERNAME and password == Login.PASSWORD
    
    @staticmethod
    def authenticate_db(username, password):
        """Authenticate against users table in database"""
        # First, ensure the users table exists
        Login._setup_users_table()
        
        # Check for user in database
        user = db_fetchone("SELECT * FROM users WHERE username=?", (username,))
        if user and user["password"] == password:
            return True, user["role"]
        return False, None
    
    @staticmethod
    def _setup_users_table():
        """Create users table if it doesn't exist"""
        conn = get_connection()
        c = conn.cursor()
        try:
            # Check if users table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not c.fetchone():
                # Create users table
                c.execute("""
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL,
                        full_name TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert default admin user
                c.execute("INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                         ("doctor", "dentalclinic123", "admin", "System Administrator"))
                conn.commit()
                print("Users table created with default admin user")
            else:
                # Check if default user exists
                c.execute("SELECT COUNT(*) FROM users WHERE username=?", ("doctor",))
                if c.fetchone()[0] == 0:
                    c.execute("INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                             ("doctor", "dentalclinic123", "admin", "System Administrator"))
                    conn.commit()
        except Exception as e:
            print(f"Error setting up users table: {e}")
        finally:
            conn.close()

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Dental Clinic System - Login")
        self.geometry("500x500")
        self.resizable(False, False)
        
        self._center_window()
        self._create_widgets()
        
        # Initialize database
        create_tables()
        check_and_fix_database()
        seed_defaults()
        
        # Setup users table
        Login._setup_users_table()

    def _center_window(self):
        self.update_idletasks()
        width = 500
        height = 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=30, pady=30, fill="both", expand=True)
        
        # Logo/Title section
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(pady=(20, 40))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🦷 Dental Clinic System", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Dental Clinic Management", 
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Login form
        form_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        form_title = ctk.CTkLabel(
            form_frame,
            text="Login to Continue",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        form_title.pack(pady=(25, 30))
        
        # Username field
        username_label = ctk.CTkLabel(form_frame, text="Username:", font=ctk.CTkFont(size=14))
        username_label.pack(pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Enter username",
            width=320, 
            height=45, 
            font=ctk.CTkFont(size=16)
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password field
        password_label = ctk.CTkLabel(form_frame, text="Password:", font=ctk.CTkFont(size=14))
        password_label.pack(pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Enter password",
            width=320, 
            height=45, 
            show="*", 
            font=ctk.CTkFont(size=16)
        )
        self.password_entry.pack(pady=(0, 30))
        
        # Login button
        login_button = ctk.CTkButton(
            form_frame, 
            text="Login", 
            command=self._login,
            width=320,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2E86AB",
            hover_color="#1B6B93"
        )
        login_button.pack(pady=(0, 20))
        
        # Demo credentials
        demo_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        demo_frame.pack(pady=(10, 5))
        
        demo_label = ctk.CTkLabel(
            demo_frame,
            text="Demo Credentials:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        demo_label.pack()
        
        credentials_label = ctk.CTkLabel(
            demo_frame,
            text="Username: doctor | Password: dentalclinic123",
            font=ctk.CTkFont(size=12)
        )
        credentials_label.pack()
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda event: self._login())
        self.password_entry.bind("<Return>", lambda event: self._login())
        
        # Set focus to username field
        self.username_entry.focus()

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Missing Fields", "Please enter both username and password")
            return
        
        # Try database authentication first
        auth_success, role = Login.authenticate_db(username, password)
        
        if auth_success:
            self.destroy()
            from gui_main import MainApp
            app = MainApp()
            # Set current user info
            app.current_user = {"username": username, "role": role}
            app.mainloop()
        else:
            # Fallback to hardcoded credentials (for backward compatibility)
            if Login.authenticate(username, password):
                self.destroy()
                from gui_main import MainApp
                app = MainApp()
                app.mainloop()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
                self.password_entry.delete(0, 'end')
                self.password_entry.focus()

if __name__ == "__main__":
    # Test the login window
    app = LoginWindow()
    app.mainloop()