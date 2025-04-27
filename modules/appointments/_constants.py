from enum import Enum
from typing import List, TypedDict

class DoctorAvailabilityItem(TypedDict):
    date: str
    times: List[str]

class AppointmentType(Enum):
    REGULAR = "Regular Appointment"
    FOLLOW_UP = "Follow Up"
    ROUTINE = "Routine Check-up"
    SICK = "Sick Visit"
    CONSULTATION = "Consultation Appointment"
    TREATMENT = "Treatment Appointment"
    PRE_POST_OPERATION = "Pre-Operative or Post-Operative Visit"
    ANNUAL = "Annual Physical"
    ORTHOPEDIC = "Orthopedic Consultation"
    MRI = "MRI Scan"


PREPARATION_INSTRUCTIONS = {
    AppointmentType.REGULAR: "Nothing special. Bring your current medications and any medical record you want the doctor to view",
    AppointmentType.FOLLOW_UP: "Nothing special. Bring your current medications and any medical record you want the doctor to view",
    AppointmentType.ROUTINE: "Nothing",
    AppointmentType.SICK: "Wear a mask and list symptoms beforehand.",
    AppointmentType.CONSULTATION: "Bring your referral form, relevant medical records/test results.",
    AppointmentType.TREATMENT: "Bring current medications, insurance card and comfortable clothing",
    AppointmentType.PRE_POST_OPERATION: "For pre-op: bring insurance cards, medication list, and advance directive if you have one; for post-op: bring wound care supplies and your discharge instructions.",
    AppointmentType.ANNUAL: "Bring your complete medication list, immunization records, and come fasting if bloodwork is planned (water is permitted).",
    AppointmentType.ORTHOPEDIC: "Bring recent X-rays or MRI scans.",
    AppointmentType.MRI: "Avoid wearing metal objects. Bring your referral form, wear metal-free clothing (no zippers, underwire, jewelry), and inform staff of any implants or claustrophobia concerns.",
}