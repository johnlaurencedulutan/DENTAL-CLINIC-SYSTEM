👥 Patient Management
Add, edit, view, and delete patient records

Age-based automatic tooth chart generation

Contact information and medical notes storage

"Finish Treatment" functionality

View patient's appointment history



📅 Appointment Scheduling
Schedule appointments with doctors

Smart auto-assign doctors based on service type

View appointments by date with filtering

Payment status management (paid/partial/pending)

Appointment completion with payment tracking

Overlap prevention for doctor schedules



👨‍⚕️ Doctor Management
Manage doctor profiles with specialties

Track doctor availability

View appointment counts per doctor

Auto-assignment based on service requirements



💰 Services & Pricing
Manage dental services catalog

Set and update service prices

10 default services included

Easy service management interface



🦷 Advanced Tooth Records System
Age-appropriate tooth charts (primary & permanent)

Visual tooth status indicators with color coding

Individual tooth notes and status tracking

Tooth reference guide with complete numbering system

Automatic chart updates when patient age changes



🚀 Quick Start
Prerequisites
Python 3.8 or higher

pip (Python package manager)

Installation
Install required package:

bash
pip install customtkinter
Save the code as dental_clinic.py

Run the application:

bash
python dental_clinic.py
Default Login Credentials
Username: doctor

Password: dentalclinic123



📖 User Guide
Getting Started
Login using the default credentials

Navigate using the sidebar menu

Explore different modules

Managing Patients
To add a new patient:

Click "Patients" in sidebar

Click "Add Patient" button

Fill in patient details

System automatically creates appropriate tooth chart

To edit a patient:

Select patient from the list

Click "View/Edit"

Modify details as needed

Tooth chart updates automatically if age changes

Scheduling Appointments
To create a new appointment:

Click "Appointments" in sidebar

Click "New Appointment"

Select patient, service, and date/time

Use "Auto Assign Doctor" for automatic specialist selection

Save appointment

To mark appointment as completed:

Select appointment from list

Click "Mark Completed"

Enter payment status and amount

Save changes

Managing Tooth Records
To view/edit tooth records:

Click "Tooth Records" in sidebar

Select a patient from dropdown

Click "Open Tooth Records"

Click on any tooth to edit its status

Set status: Healthy, Cavity, Filling, or Extracted

Add notes for specific dental issues



🦷 Tooth Numbering System
Primary Teeth (Children - 20 teeth)
Letters A-T

For children under 12 years

Permanent Teeth (Adults - 32 teeth)
Numbers 1-32

For teens and adults

Age-Based Tooth Charts
Age	Teeth Count	Type
0-2 years	8	Primary teeth only
3-5 years	20	All primary teeth
6-11 years	24	Mixed dentition
12-17 years	28	Most permanent teeth
18+ years	32	All permanent teeth
🔧 Technical Features
Smart Doctor Assignment
Automatically assigns doctors based on service type:

Pediatric services → Pediatric Dentistry specialist

Orthodontic services → Orthodontics specialist

Surgical services → Oral Surgery specialist

Gum services → Periodontics specialist

General services → General Dentistry

Dynamic Tooth Chart
Charts update automatically when patient age changes

Prevents tracking non-existent teeth

Visual color coding for easy status identification

Payment Management
Track payment status (Paid/Partial/Pending)

Record actual amounts paid

Mark appointments as completed with payment info

View payment history per patient



🎯 Usage Examples
Scenario: Child Dental Checkup
Add a 5-year-old patient

System creates 20-tooth primary chart

Schedule "Pediatric Checkup" appointment

System auto-assigns pediatric dentist

After checkup, update tooth statuses

Scenario: Adult Root Canal
Select adult patient

Schedule "Root Canal" service

System auto-assigns appropriate specialist

Complete appointment with payment

Update affected tooth status to "filled"



🗃️ Database Structure
Tables
doctors - Doctor information and availability

patients - Patient records including tooth data

services - Dental services and pricing

appointments - Appointment scheduling and payment tracking

Default Data
The system includes:

5 sample doctors with different specialties

10 common dental services with prices

1 sample patient



🛠️ Customization
Changing Defaults
Login credentials: Edit Login class constants

Default services: Modify DEFAULT_SERVICES list

Default doctors: Modify DEFAULT_DOCTORS list

Tooth names: Edit PRIMARY_TEETH and PERMANENT_TEETH lists

Database Backup
Database is stored in dental_clinic.db file

Backup this file regularly for data safety

To reset: delete the file and restart application



🐛 Troubleshooting
Issue	Solution
Login not working	Use default: doctor/dentalclinic123
Database errors	Delete dental_clinic.db and restart
Import errors	pip install customtkinter
Window sizing issues	App is fixed at 1400x750 (main), 500x450 (login)
Tooth chart not showing	Verify patient age is set correctly.
