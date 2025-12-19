# gui_main.py
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from auth import LoginWindow, Login
from gui_views_core import PatientViews
from gui_views_doctors import DoctorViews
from gui_views_services import ServiceViews
from gui_views_appointments import AppointmentViews
from gui_views_tooth import ToothViews
from gui_views_recycle import RecycleViews
from database import db_execute, db_fetchall, db_fetchone, get_connection, get_appointments, update_doctor_availability_auto, check_overdue_appointments

class MainApp(ctk.CTk, PatientViews, DoctorViews, ServiceViews, AppointmentViews, ToothViews, RecycleViews):
    def __init__(self):
        super().__init__()
        
        self.title("Dental Clinic System")
        self.geometry("1400x750")
        
        # Make window responsive
        self.minsize(1200, 700)
        
        self._center_window()
        self.current_user = {"username": Login.USERNAME, "role": "admin"}
        self._create_main_window()
        
        # Create users table if it doesn't exist
        self._setup_user_table()

    def _setup_user_table(self):
        """Create users table for multi-user support"""
        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert default admin user if not exists
            c.execute("SELECT COUNT(*) FROM users WHERE username=?", ("doctor",))
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                         ("doctor", "dentalclinic123", "admin", "System Administrator"))
            conn.commit()
        except Exception as e:
            print(f"Error setting up users table: {e}")
        finally:
            conn.close()

    def _center_window(self):
        self.update_idletasks()
        width = 1400
        height = 750
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_main_window(self):
        # Configure main grid - 2 columns: sidebar (fixed) and main content
        self.grid_columnconfigure(0, weight=0)  # Sidebar - fixed width
        self.grid_columnconfigure(1, weight=1)  # Main content - expands
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame - WIDER (320px)
        self.sidebar_frame = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color="#d6d6dd")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)  # Prevent shrinking
        
        # Configure sidebar grid - single column
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(0, weight=1)  # Scrollable frame takes all space
        
        # Create a canvas and scrollbar for the sidebar
        sidebar_canvas = ctk.CTkCanvas(self.sidebar_frame, highlightthickness=0, bg="#c7c7d6")
        sidebar_scrollbar = ctk.CTkScrollbar(self.sidebar_frame, orientation="vertical", command=sidebar_canvas.yview)
        
        sidebar_canvas.grid(row=0, column=0, sticky="nsew")
        sidebar_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure canvas
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        sidebar_canvas.bind('<Configure>', lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        
        # Create inner frame for sidebar content
        sidebar_inner_frame = ctk.CTkFrame(sidebar_canvas, fg_color="#cdcdda")
        sidebar_canvas.create_window((0, 0), window=sidebar_inner_frame, anchor="nw", width=300)
        
        # Logo/Header section
        header_frame = ctk.CTkFrame(sidebar_inner_frame, fg_color="transparent", height=120)
        header_frame.pack(fill="x", padx=10, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Logo
        logo_label = ctk.CTkLabel(
            header_frame, 
            text="🦷 Dental Clinic", 
            font=ctk.CTkFont(size=28, weight="bold", family="Arial"),
            text_color="white"
        )
        logo_label.pack(pady=(15, 5))
        
        # User info with better styling
        user_frame = ctk.CTkFrame(header_frame, fg_color="#DEE1E7", corner_radius=10, height=60)
        user_frame.pack(fill="x", padx=10, pady=10)
        user_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user['username']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(pady=(10, 2))
        
        ctk.CTkLabel(
            user_frame,
            text=f"Role: {self.current_user['role'].title()}",
            font=ctk.CTkFont(size=12),
            text_color="#e6e6e6"
        ).pack()
        
        # Navigation buttons - larger and better spaced
        nav_buttons = [
            ("🏥 Patients", self.show_patients, "#2a9d8f"),
            ("📅 Appointments", self.show_appointments, "#e9c46a"),
            ("📅 Calendar View", self.show_calendar, "#4CC9F0"),
            ("⚠️ Overdue Appointments", self.show_overdue_appointments, "#f4a261"),
            ("💰 Services & Prices", self.show_services, "#f4a261"),
            ("👨‍⚕️ Doctors", self.show_doctors, "#264653"),
            ("🦷 Tooth Records", self.show_tooth_records_main, "#e76f51"),
            ("📋 Tooth Reference", self.show_tooth_reference, "#2a9d8f"),
            ("⚙️ Admin Panel", self.show_admin_panel, "#9d4edd"),
            ("🗑️ Recycle Bin", self.show_recycle_bin, "#6a0572"),
        ]
        
        for text, command, color in nav_buttons:
            btn = ctk.CTkButton(
                sidebar_inner_frame,
                text=text,
                command=command,
                height=50,
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
                fg_color=color,
                hover_color=f"#{hex(int(color[1:], 16) - 0x222222)[2:]:0>6}",
                corner_radius=8,
                text_color="white",
                border_width=0
            )
            # Add icon padding
            btn_text = btn.cget("text")
            btn.configure(text=f"   {btn_text}")
            
            btn.pack(fill="x", padx=15, pady=8)
        
        # Spacer before logout button
        spacer_frame = ctk.CTkFrame(sidebar_inner_frame, fg_color="transparent", height=20)
        spacer_frame.pack(fill="x", pady=10)
        
        # Logout button
        logout_button = ctk.CTkButton(
            sidebar_inner_frame, 
            text="🚪 Logout", 
            command=self.logout,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#d00000",
            hover_color="#9d0208",
            corner_radius=8,
            text_color="white"
        )
        logout_button.pack(fill="x", padx=15, pady=(20, 30))
        
        # Update canvas scrollregion when inner frame changes size
        sidebar_inner_frame.bind("<Configure>", lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        
        # Bind mouse wheel to scroll
        def _on_mousewheel(event):
            sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        sidebar_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Make sidebar column expandable
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Main content area
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="#f8f9fa")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Show default view
        self.show_patients()

    def show_calendar(self):
        """Display a compact calendar view of appointments"""
        self.clear_main_content()
        
        # Create main container
        main_container = ctk.CTkFrame(self.main_content)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # Title and controls
        title_frame = ctk.CTkFrame(main_container)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="📅 Appointment Calendar",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Navigation controls
        control_frame = ctk.CTkFrame(title_frame)
        control_frame.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
        self.current_calendar_date = datetime.now()
        
        def prev_month():
            self.current_calendar_date = self.current_calendar_date.replace(day=1) - timedelta(days=1)
            self._update_calendar()
        
        def next_month():
            next_month = self.current_calendar_date.replace(day=28) + timedelta(days=7)
            self.current_calendar_date = next_month.replace(day=1)
            self._update_calendar()
        
        def go_today():
            self.current_calendar_date = datetime.now()
            self._update_calendar()
        
        ctk.CTkButton(control_frame, text="◀", width=40, command=prev_month).pack(side="left", padx=2)
        ctk.CTkButton(control_frame, text="Today", width=80, command=go_today).pack(side="left", padx=2)
        ctk.CTkButton(control_frame, text="▶", width=40, command=next_month).pack(side="left", padx=2)
        
        # Calendar container
        calendar_container = ctk.CTkFrame(main_container)
        calendar_container.grid(row=1, column=0, sticky="nsew", pady=5)
        calendar_container.grid_columnconfigure(0, weight=1)
        calendar_container.grid_rowconfigure(1, weight=1)
        
        self.calendar_frame = ctk.CTkFrame(calendar_container)
        self.calendar_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self._update_calendar()

    def _update_calendar(self):
        """Update calendar display"""
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Month header
        month_year = self.current_calendar_date.strftime("%B %Y")
        ctk.CTkLabel(
            self.calendar_frame,
            text=month_year,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=7, pady=(0, 10))
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            ctk.CTkLabel(
                self.calendar_frame,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=1, column=i, padx=2, pady=2)
        
        # Get first day of month
        first_day = self.current_calendar_date.replace(day=1)
        # Get weekday (0=Monday, 6=Sunday)
        weekday = first_day.weekday()
        
        # Get all days in month
        if first_day.month == 12:
            next_month = first_day.replace(year=first_day.year+1, month=1, day=1)
        else:
            next_month = first_day.replace(month=first_day.month+1, day=1)
        
        # Calculate days in month
        days_in_month = (next_month - timedelta(days=1)).day
        
        # Get appointments for this month
        start_date = first_day.strftime("%Y-%m-%d 00:00:00")
        end_date = next_month.strftime("%Y-%m-%d 00:00:00")
        appointments = get_appointments(start_date, end_date)
        
        # Group appointments by day
        appointments_by_day = {}
        for apt in appointments:
            apt_date = datetime.strptime(apt["start_datetime"], "%Y-%m-%d %H:%M:%S")
            day_key = apt_date.day
            if day_key not in appointments_by_day:
                appointments_by_day[day_key] = []
            appointments_by_day[day_key].append(apt)
        
        # Create calendar grid
        row = 2
        col = weekday
        
        for day in range(1, days_in_month + 1):
            day_frame = ctk.CTkFrame(self.calendar_frame, width=100, height=80, corner_radius=5)
            day_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            day_frame.grid_propagate(False)
            
            # Day number
            day_label = ctk.CTkLabel(
                day_frame,
                text=str(day),
                font=ctk.CTkFont(size=12, weight="bold")
            )
            day_label.pack(pady=(5, 0))
            
            # Check if today
            today = datetime.now()
            if (self.current_calendar_date.year == today.year and 
                self.current_calendar_date.month == today.month and 
                day == today.day):
                day_frame.configure(fg_color="#e6f7ff", border_width=1, border_color="#4CC9F0")
            
            # Show appointment count
            if day in appointments_by_day:
                count = len(appointments_by_day[day])
                if count > 0:
                    # Check for overdue appointments first
                    if any(apt["status"] == "overdue" for apt in appointments_by_day[day]):
                        color = "#ff6b6b"  # Red for overdue
                    elif any(apt["status"] == "completed" for apt in appointments_by_day[day]):
                        color = "#51cf66"  # Green for completed
                    elif any(apt["status"] == "cancelled" for apt in appointments_by_day[day]):
                        color = "#868e96"  # Gray for cancelled
                    else:
                        color = "#ff6b6b"  # Default red for appointments
                    
                    count_label = ctk.CTkLabel(
                        day_frame,
                        text=f"{count} appt",
                        font=ctk.CTkFont(size=9),
                        text_color=color
                    )
                    count_label.pack()
                    
                    # Add click event to view details
                    def show_day_details(day_num=day):
                        self._show_day_appointments(day_num, appointments_by_day[day_num])
                    
                    day_frame.bind("<Button-1>", lambda e, d=day: show_day_details(d))
                    day_label.bind("<Button-1>", lambda e, d=day: show_day_details(d))
                    if 'count_label' in locals():
                        count_label.bind("<Button-1>", lambda e, d=day: show_day_details(d))
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Configure grid columns
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="col")

    def _show_day_appointments(self, day, appointments):
        """Show appointments for a specific day"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Appointments - {self.current_calendar_date.strftime('%B')} {day}")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            main_frame,
            text=f"Appointments for {self.current_calendar_date.strftime('%B')} {day}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 15))
        
        if not appointments:
            ctk.CTkLabel(
                main_frame,
                text="No appointments scheduled",
                font=ctk.CTkFont(size=14)
            ).pack(pady=50)
        else:
            # Create scrollable frame
            scroll_frame = ctk.CTkScrollableFrame(main_frame)
            scroll_frame.pack(fill="both", expand=True, pady=10)
            
            for apt in appointments:
                apt_frame = ctk.CTkFrame(scroll_frame, height=60)
                apt_frame.pack(fill="x", pady=2, padx=5)
                apt_frame.pack_propagate(False)
                
                # Parse time
                apt_time = datetime.strptime(apt["start_datetime"], "%Y-%m-%d %H:%M:%S")
                time_str = apt_time.strftime("%H:%M")
                
                # Status colors - ADD OVERDUE STATUS
                status_colors = {
                    "scheduled": "#4CC9F0",
                    "confirmed": "#4361ee",
                    "completed": "#51cf66",
                    "cancelled": "#868e96",
                    "overdue": "#ff6b6b"  # NEW: Red for overdue
                }
                
                # Left side: Time and basic info
                left_frame = ctk.CTkFrame(apt_frame, fg_color="transparent")
                left_frame.pack(side="left", fill="both", expand=True, padx=10)
                
                ctk.CTkLabel(
                    left_frame,
                    text=f"{time_str} - {apt['patient_name']}",
                    font=ctk.CTkFont(size=13)
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    left_frame,
                    text=f"Dr. {apt['doctor_name']}",
                    font=ctk.CTkFont(size=11)
                ).pack(anchor="w")
                
                # Right side: Status
                right_frame = ctk.CTkFrame(apt_frame, fg_color="transparent")
                right_frame.pack(side="right", padx=10)
                
                status_color = status_colors.get(apt["status"], "#868e96")
                status_label = ctk.CTkLabel(
                    right_frame,
                    text=apt["status"].title(),
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=status_color
                )
                status_label.pack(pady=10)
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Close",
            command=dialog.destroy,
            width=100
        ).pack()

    def show_admin_panel(self):
        """Display admin panel with system information and utilities"""
        self.clear_main_content()
        
        # Create main container with proper constraints
        main_container = ctk.CTkFrame(self.main_content)
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame for admin panel
        main_scroll = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        main_scroll.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_scroll.grid_columnconfigure(0, weight=1)
        
        # Title with better styling
        title_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame, 
            text="⚙️ Admin Panel", 
            font=ctk.CTkFont(size=36, weight="bold", family="Arial"),
            text_color="#1a1a2e"
        ).grid(row=0, column=0, sticky="w", pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="System Management Dashboard",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        ).grid(row=1, column=0, sticky="w", pady=(0, 20))
        
        # Dashboard with cards - improved layout
        dashboard_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        dashboard_frame.grid(row=1, column=0, sticky="ew", pady=(0, 30))
        dashboard_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
        
        from database import get_patients, get_doctors, get_appointments, get_services
        
        patients = get_patients()
        doctors = get_doctors()
        appointments = get_appointments()
        services = get_services()
        
        # Calculate statistics
        stats = [
            ("👥 Patients", len(patients), "#2a9d8f"),
            ("👨‍⚕️ Doctors", len(doctors), "#264653"),
            ("💰 Services", len(services), "#e9c46a"),
            ("📅 Appointments", len(appointments), "#e76f51")
        ]
        
        # Create stat cards
        for i, (title, value, color) in enumerate(stats):
            card = ctk.CTkFrame(dashboard_frame, height=120, fg_color="white", corner_radius=15)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            card.grid_propagate(False)
            
            # Card header
            header_frame = ctk.CTkFrame(card, fg_color=color, corner_radius=15)
            header_frame.pack(fill="x", pady=(0, 15))
            
            ctk.CTkLabel(
                header_frame,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(pady=10)
            
            # Card value
            ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=42, weight="bold"),
                text_color="#1a1a2e"
            ).pack(expand=True)
            
            # Add subtle shadow effect
            card.configure(border_width=1, border_color="#e0e0e0")
        
        # User Management Section
        user_mgmt_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=15)
        user_mgmt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        user_mgmt_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        section_header = ctk.CTkFrame(user_mgmt_frame, fg_color="#9d4edd", corner_radius=15)
        section_header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            section_header,
            text="👥 User Management",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Current user info
        user_info_frame = ctk.CTkFrame(user_mgmt_frame, fg_color="transparent")
        user_info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            user_info_frame,
            text=f"👤 Logged in as: {self.current_user['username']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1a1a2e"
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            user_info_frame,
            text=f"🏷️ Role: {self.current_user['role'].title()}",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        ).pack(anchor="w", pady=(0, 15))
        
        # Buttons for user management
        user_buttons_frame = ctk.CTkFrame(user_mgmt_frame, fg_color="transparent")
        user_buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        user_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        button_configs = [
            ("➕ Add New User", self.show_add_user_form, "#2a9d8f"),
            ("👁️ View All Users", self.show_all_users, "#264653"),
            ("🔐 Change Password", self.change_current_password, "#e9c46a")
        ]
        
        for i, (text, command, color) in enumerate(button_configs):
            btn = ctk.CTkButton(
                user_buttons_frame,
                text=text,
                command=command,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=f"#{hex(int(color[1:], 16) - 0x222222)[2:]:0>6}",
                corner_radius=8,
                text_color="white"
            )
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # System Utilities Section
        utils_frame = ctk.CTkFrame(main_scroll, fg_color="white", corner_radius=15)
        utils_frame.grid(row=3, column=0, sticky="ew", pady=(0, 30))
        utils_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        utils_header = ctk.CTkFrame(utils_frame, fg_color="#2a9d8f", corner_radius=15)
        utils_header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(
            utils_header,
            text="⚙️ System Utilities",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Utility buttons
        utils_buttons_frame = ctk.CTkFrame(utils_frame, fg_color="transparent")
        utils_buttons_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        utils_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        utils_configs = [
            ("🔄 Refresh Doctor Availability", self.refresh_doctor_availability, "#2a9d8f"),
            ("⚠️ Check Overdue Appointments", self.check_overdue_appointments, "#e76f51"),
            ("💾 Create System Backup", self.system_backup, "#264653"),
            ("🗑️ Clear Recycle Bin", self.clear_recycle_bin, "#d00000")
        ]
        
        for i, (text, command, color) in enumerate(utils_configs):
            btn = ctk.CTkButton(
                utils_buttons_frame,
                text=text,
                command=command,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=f"#{hex(int(color[1:], 16) - 0x222222)[2:]:0>6}",
                corner_radius=8,
                text_color="white"
            )
            btn.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # Configure column weights for responsive design
        main_scroll.grid_columnconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)

    def check_overdue_appointments(self):
        """Manual check for overdue appointments"""
        count = check_overdue_appointments()
        if count > 0:
            messagebox.showinfo("Overdue Check", f"✅ {count} appointment(s) marked as overdue!")
        else:
            messagebox.showinfo("Overdue Check", "✅ No overdue appointments found.")
        self.show_admin_panel()

    def show_add_user_form(self, user_id=None):
        """Show form to add/edit users"""
        form_window = ctk.CTkToplevel(self)
        form_window.title("Add New User" if user_id is None else "Edit User")
        form_window.geometry("500x500")
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
        
        title_text = "➕ Add New User" if user_id is None else "✏️ Edit User"
        title_label = ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Username
        ctk.CTkLabel(fields_frame, text="👤 Username:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, sticky="w", padx=10, pady=(15, 5))
        username_entry = ctk.CTkEntry(fields_frame, width=300, height=35)
        username_entry.grid(row=0, column=1, padx=10, pady=(15, 5))
        
        # Full Name
        ctk.CTkLabel(fields_frame, text="📝 Full Name:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        fullname_entry = ctk.CTkEntry(fields_frame, width=300, height=35)
        fullname_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Password
        ctk.CTkLabel(fields_frame, text="🔒 Password:" if user_id is None else "🔒 New Password (leave blank to keep current):", 
                    font=ctk.CTkFont(size=14)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        password_entry = ctk.CTkEntry(fields_frame, width=300, height=35, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Role
        ctk.CTkLabel(fields_frame, text="🏷️ Role:", font=ctk.CTkFont(size=14)).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        role_var = ctk.StringVar(value="doctor")
        role_combo = ctk.CTkComboBox(fields_frame, values=["admin", "doctor"], variable=role_var, width=300, height=35)
        role_combo.grid(row=3, column=1, padx=10, pady=5)
        
        # Load existing user data if editing
        if user_id:
            user = db_fetchone("SELECT * FROM users WHERE id=?", (user_id,))
            if user:
                username_entry.insert(0, user["username"])
                fullname_entry.insert(0, user["full_name"] or "")
                role_var.set(user["role"])
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=20)
        
        def save_user():
            username = username_entry.get().strip()
            full_name = fullname_entry.get().strip()
            password = password_entry.get().strip()
            role = role_var.get()
            
            if not username:
                messagebox.showerror("Error", "Username is required")
                return
            
            if user_id is None and not password:
                messagebox.showerror("Error", "Password is required for new users")
                return
            
            try:
                if user_id:
                    # Update existing user
                    if password:
                        db_execute("UPDATE users SET username=?, full_name=?, role=?, password=? WHERE id=?",
                                 (username, full_name, role, password, user_id))
                    else:
                        db_execute("UPDATE users SET username=?, full_name=?, role=? WHERE id=?",
                                 (username, full_name, role, user_id))
                    messagebox.showinfo("Success", "✅ User updated successfully")
                else:
                    # Add new user
                    db_execute("INSERT INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                             (username, password, role, full_name))
                    messagebox.showinfo("Success", "✅ User added successfully")
                
                form_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to save user: {str(e)}")
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save",
            command=save_user,
            width=120,
            height=35,
            fg_color="#2a9d8f"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=form_window.destroy,
            width=120,
            height=35,
            fg_color="#d00000"
        ).pack(side="left", padx=10)

    def show_all_users(self):
        """Display all users in a table"""
        self.clear_main_content()
        
        # Create main container
        main_container = ctk.CTkFrame(self.main_content)
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        title_frame = ctk.CTkFrame(main_container)
        title_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="👥 User Management", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        add_button = ctk.CTkButton(
            title_frame,
            text="➕ Add New User",
            command=self.show_add_user_form,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2a9d8f"
        )
        add_button.grid(row=0, column=1, sticky="e", padx=15, pady=15)
        
        # Create treeview for users
        tree_frame = ctk.CTkFrame(main_container)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        main_container.grid_rowconfigure(1, weight=1)
        
        import tkinter.ttk as ttk
        
        cols = ("id", "username", "full_name", "role", "created_at")
        users_tree = ttk.Treeview(
            tree_frame, 
            columns=cols,
            show="headings",
            height=15
        )
        
        users_tree.heading("id", text="ID")
        users_tree.heading("username", text="👤 Username")
        users_tree.heading("full_name", text="📝 Full Name")
        users_tree.heading("role", text="🏷️ Role")
        users_tree.heading("created_at", text="📅 Created")
        
        users_tree.column("id", width=50)
        users_tree.column("username", width=150)
        users_tree.column("full_name", width=200)
        users_tree.column("role", width=100)
        users_tree.column("created_at", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=users_tree.yview)
        users_tree.configure(yscrollcommand=scrollbar.set)
        
        users_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Load users
        users = db_fetchall("SELECT * FROM users ORDER BY id")
        for user in users:
            users_tree.insert("", "end", values=(
                user["id"],
                user["username"],
                user["full_name"] or "",
                user["role"],
                user["created_at"]
            ))
        
        # Button frame
        button_frame = ctk.CTkFrame(main_container)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        def edit_selected():
            selection = users_tree.selection()
            if not selection:
                messagebox.showinfo("Select", "Please select a user to edit")
                return
            user_id = int(users_tree.item(selection[0])["values"][0])
            self.show_add_user_form(user_id)
        
        def delete_selected():
            selection = users_tree.selection()
            if not selection:
                messagebox.showinfo("Select", "Please select a user to delete")
                return
            
            user_id = int(users_tree.item(selection[0])["values"][0])
            username = users_tree.item(selection[0])["values"][1]
            
            if username == self.current_user["username"]:
                messagebox.showerror("Error", "❌ You cannot delete your own account!")
                return
            
            if messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?"):
                db_execute("DELETE FROM users WHERE id=?", (user_id,))
                messagebox.showinfo("Success", "✅ User deleted")
                self.show_all_users()
        
        ctk.CTkButton(
            button_frame,
            text="✏️ Edit Selected",
            command=edit_selected,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="🗑️ Delete Selected",
            command=delete_selected,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#d00000"
        ).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="⬅️ Back to Admin Panel",
            command=self.show_admin_panel,
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Configure layout
        main_container.update_idletasks()

    def change_current_password(self):
        """Change password for current user"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("400x400")
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
        
        ctk.CTkLabel(
            main_frame,
            text="🔐 Change Password",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(main_frame, text="Current Password:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        current_pass_entry = ctk.CTkEntry(main_frame, show="*", width=300, height=35)
        current_pass_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="New Password:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        new_pass_entry = ctk.CTkEntry(main_frame, show="*", width=300, height=35)
        new_pass_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="Confirm New Password:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        confirm_pass_entry = ctk.CTkEntry(main_frame, show="*", width=300, height=35)
        confirm_pass_entry.pack(pady=(0, 20))
        
        def save_password():
            current_pass = current_pass_entry.get()
            new_pass = new_pass_entry.get()
            confirm_pass = confirm_pass_entry.get()
            
            # Verify current password
            user = db_fetchone("SELECT * FROM users WHERE username=?", (self.current_user["username"],))
            if not user or user["password"] != current_pass:
                messagebox.showerror("Error", "❌ Current password is incorrect")
                return
            
            if not new_pass:
                messagebox.showerror("Error", "❌ New password cannot be empty")
                return
            
            if new_pass != confirm_pass:
                messagebox.showerror("Error", "❌ New passwords do not match")
                return
            
            # Update password
            db_execute("UPDATE users SET password=? WHERE username=?", (new_pass, self.current_user["username"]))
            messagebox.showinfo("Success", "✅ Password changed successfully!")
            dialog.destroy()
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Password",
            command=save_password,
            width=140,
            height=35,
            fg_color="#2a9d8f"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            width=140,
            height=35,
            fg_color="#d00000"
        ).pack(side="left", padx=5)

    def refresh_doctor_availability(self):
        """Refresh doctor availability"""
        update_doctor_availability_auto()
        messagebox.showinfo("Success", "✅ Doctor availability refreshed!")
        self.show_admin_panel()

    def system_backup(self):
        """Create system backup"""
        import shutil
        import os
        from datetime import datetime
        from database import DB_FILE
        
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"dental_backup_{timestamp}.db")
        
        try:
            shutil.copy2(DB_FILE, backup_file)
            messagebox.showinfo("Backup Successful", f"✅ Backup created at:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"❌ Error: {str(e)}")

    def clear_recycle_bin(self):
        """Clear all items from recycle bin"""
        from database import get_recycle_items, permanently_delete_recycle_item
        
        items = get_recycle_items()
        if not items:
            messagebox.showinfo("Empty", "🗑️ Recycle bin is already empty")
            return
        
        if messagebox.askyesno("Confirm", f"Permanently delete {len(items)} item(s) from recycle bin?\nThis action cannot be undone!"):
            for item in items:
                permanently_delete_recycle_item(item["id"])
            messagebox.showinfo("Success", f"✅ Deleted {len(items)} item(s)")
            self.show_admin_panel()

    def logout(self):
        self.destroy()
        login_window = LoginWindow()
        login_window.mainloop()

    def clear_main_content(self):
        """Clear all widgets from main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        # Force update to ensure cleanup
        self.main_content.update_idletasks()