# models.py
import json
from datetime import datetime

# ----------------------------
# TOOTH DEFINITIONS
# ----------------------------

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
    {"id": "1", "name": "Upper Right Third Molar"},
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
    {"id": "16", "name": "Upper Left Third Molar"},
    {"id": "17", "name": "Lower Left Third Molar"},
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
    {"id": "32", "name": "Lower Right Third Molar"},
]


DB_FILE = "dental_clinic.db"


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

DEFAULT_DOCTORS = [
    ("Dr. Maria Santos", "Pediatric Dentistry", "09171234567", 1),
    ("Dr. Jose Cruz", "General Dentistry", "09179876543", 1),
    ("Dr. Anna Reyes", "Orthodontics", "09175556677", 1),
    ("Dr. Robert Lim", "Oral Surgery", "09178889900", 1),
    ("Dr. Sofia Tan", "Periodontics", "09172223344", 1),
]


def get_appropriate_tooth_set_for_age(age):
    """
    SIMPLE RULE:
    - Age < 12  -> 20 primary teeth
    - Age >= 12 -> 32 permanent teeth
    """
    age = int(age)

    if age < 12:
        return {
            t["id"]: {"status": "healthy", "notes": "", "present": True}
            for t in PRIMARY_TEETH
        }
    else:
        return {
            t["id"]: {"status": "healthy", "notes": "", "present": True}
            for t in PERMANENT_TEETH
        }

def get_tooth_count_for_age(age):
    """Return expected tooth count for given age using non-overlapping ranges.

    - age < 3   -> 8 (some baby teeth)
    - age < 7   -> 20 (primary dentition)
    - age < 13  -> 24 (mixed dentition)
    - age < 19  -> 28 (most permanent except wisdom)
    - else      -> 32 (full permanent dentition)
    """
    age = int(age)
    if age < 3:
        return 8
    if age < 7:
        return 20
    if age < 13:
        return 24
    if age < 19:
        return 28
    return 32