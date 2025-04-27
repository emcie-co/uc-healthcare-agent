from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Optional
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions
from utils.date_utils import _format_datetime
from utils.json_utils import _load_data, _update_data

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def cancel_appointment(context: ToolContext, doctor_name: str, scheduled_date: datetime, reason: str) -> ToolResult:
    
    updated_doctor_result = _update_doctor_data(context.customer_id, doctor_name, scheduled_date, reason)
    if updated_doctor_result:
        return ToolResult(updated_doctor_result)
    
    updated_patient_result = _update_patient_data(context.customer_id, doctor_name, scheduled_date, reason)
    if updated_patient_result:
        return ToolResult(updated_patient_result)
    
    verified_result = _verify_update(context.customer_id, doctor_name, scheduled_date, reason)
    if "error" in verified_result:
        return ToolResult(verified_result["error"])
        
    return ToolResult(f"Appointment with {doctor_name} on {scheduled_date} has been canceled.")

def _update_doctor_data(patient_id: str, doctor_name: str, scheduled_date: datetime, reason: str) -> Optional[str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    doctor = next((doc["doctor"] for doc in doctors_data if doc["name"] == doctor_name), None)
    
    if doctor is None:
        return f"No doctor with the name {doctor_name}"
    
    availability = doctor["scheduling"]["availability"]
    _date, _time = _format_datetime(scheduled_date)
    
    match_timeslot = next ((slot for slot in availability if slot["date"] == _date and _time in slot["times"]), None)
    if match_timeslot is None:
        availability.append({"date": _date, "times": [_time]})
    else:
        return f"Timeslot {_time} on {_date} is already in record."
    
    patient_upcoming = next((entry["upcoming_appointments"] for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    if patient_upcoming is None:
        return f"No patient with the ID {patient_id}"
    
    patient_scheduled_appointment = next((slot for slot in patient_upcoming if slot["date"] == _date and slot["time"] == _time), None)
    if patient_scheduled_appointment is None:
        return f"No appointment scheduled for patient {patient_id} on {_date} at {_time}"
    
    patient_scheduled_appointment["status"] = "canceled"
    patient_scheduled_appointment["reason"] = reason
    
    _update_data(Path(DOCTORSDB_PATH), doctors_data)
    return None

def _update_patient_data(patient_id: str, doctor_name: str, scheduled_date: datetime, reason: str) -> Optional[str]:
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((pat for pat in patient_data if pat["patient_id"] == patient_id), None)
    
    if patient is None:
        return f"No patient with the ID {patient_id}"
    
    appointments = patient["medical_info"]["appointments"]
    _date, _time = _format_datetime(scheduled_date)
    
    match_appointment = next((entry for entry in appointments if entry["date"] == _date and entry["time"] == _time), None)
    if match_appointment is None:
        return f"No appointment scheduled for patient {patient_id} on {_date} at {_time}"
    
    match_appointment["status"] = "canceled"
    match_appointment["reason"] = reason
    
    _update_data(Path(PATIENTSDB_PATH), patient_data)
    return None

def _verify_update(patient_id: str, doctor_name: str, scheduled_date: datetime, reason: str) -> dict[Any, str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    _date, _time = _format_datetime(scheduled_date)
    
    doctor = next((doc["doctor"] for doc in doctors_data if doc["name"] == doctor_name), None)
    patient = next((pat for pat in patient_data if pat["patient_id"] == patient_id), None)
    
    if not doctor:
        return {"error": f"Doctor {doctor_name} not found."}
    
    if not patient:
        return {"error": f"Patient {patient_id} not found."}
    
    doctor_scheduling_availability = next((entry for entry in doctor["scheduling"]["availability"] if entry["date"] == _date and _time in entry["times"]), None)
    if not doctor_scheduling_availability:
        return {"error": f"{scheduled_date} has to been restored to {doctor_name}'s availability."}
    
    doctor_patient = next((entry for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    if not doctor_patient:
        return {"error": f"Patient {patient_id} not found in doctor's records."}
    
    doctor_patient_upcoming_appointments = next((entry for entry in doctor_patient["upcoming_appointments"] if entry["date"] == _date and entry["time"] == _time), None)
    if not doctor_patient_upcoming_appointments:
        return {"error": f"Patient {patient_id} has no appointments for that time."}
    
    if doctor_patient_upcoming_appointments["status"] != "canceled":
        return {"error": f"Patient {patient_id} has unsuccessfully canceled the appointment."}
    
    patient_scheduled_appointment = next((entry for entry in patient["medical_info"]["appointments"] if entry["date"] == _date and entry["time"] == _time), None)
    if not patient_scheduled_appointment:
        return {"error": f"Patient {patient_id} has no appointments for that time."}
    
    if patient_scheduled_appointment["status"] != "canceled":
        return {"error": f"Patient {patient_id} has unsuccessfully canceled the appointment."}
    
    return {
        "patient": doctor_patient_upcoming_appointments,
        "doctor": patient_scheduled_appointment
    }