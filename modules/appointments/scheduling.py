from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult
from utils.date_utils import _format_datetime
from utils.json_utils import _load_data, _update_data

from modules.appointments._constants import AppointmentType, PREPARATION_INSTRUCTIONS

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def schedule_appointment(context:ToolContext, doctor_name: str, requested_slot:datetime, appointment_type:AppointmentType = AppointmentType.REGULAR)-> ToolResult:
    updated_doctor_result = _update_doctor_data(context.customer_id, doctor_name, requested_slot, appointment_type)
    if updated_doctor_result:
        return ToolResult(updated_doctor_result)
    
    updated_patient_result = _update_patient_data(context.customer_id, doctor_name, requested_slot, appointment_type)
    if updated_patient_result:
        return ToolResult(updated_patient_result)
    
    verified_result = _verify_update(context.customer_id, doctor_name, requested_slot)
    if "error" in verified_result:
        return ToolResult(verified_result["error"])
        
    return ToolResult(f"Appointment scheduled with {doctor_name} on {requested_slot}.")

def _update_doctor_data(patient_id: str, doctor_name:str, requested_slot:datetime, appointment_type:AppointmentType) -> Optional[str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    doctor = next((doc["doctor"] for doc in doctors_data if doc["doctor"]["name"] == doctor_name), None)
    
    if doctor is None:
        return f"Doctor {doctor_name} not found."
    
    availabilities = doctor["scheduling"]["availability"]
    upcoming_appointments = next((entry["upcoming_appointments"] for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if upcoming_appointments is None:
        return f"Doctor {doctor_name} has no upcoming appointments."
    
    _date, _time = _format_datetime(requested_slot)
    matched_slot = next((entry for entry in availabilities if entry["date"] == _date and _time in entry["times"]), None)
    
    if matched_slot is None:
        return f"Doctor {doctor_name} is not available at {requested_slot}."
    
    #  remove the times from the availability slot. If there are no more times in the availability slot, remove the date from the availabilities
    if matched_slot["times"] and len(matched_slot["times"]) > 1:
        matched_slot["times"].remove(_time)
    else:
        availabilities.remove(matched_slot)
        
    upcoming_appointments.append(
        {
            "date": _date,
            "time": _time,
            "type": appointment_type.value,
            "lab_work_ordered": "--basic metabolic panel",
        })
    
    _update_data(Path(DOCTORSDB_PATH), doctors_data)
    
    return None

def _update_patient_data(patient_id: str, doctor_name:str, requested_slot:datetime, appointment_type:AppointmentType) -> Optional[str]:
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((entry["patient"] for entry in patient_data if entry["patient_id"] == patient_id), None)
    _date, _time = _format_datetime(requested_slot)
    
    if patient is None:
        return f"Patient {patient_id} not found."
    
    appointments = patient["medical_info"]["appointments"]
    appointments.append(
        {
            "doctor": doctor_name,
            "type": appointment_type.value,
            "date": _date,
            "time": _time,
            "location": None,
            "status": "scheduled",
            "preparation": PREPARATION_INSTRUCTIONS[appointment_type],
        }
    )
    _update_data(Path(PATIENTSDB_PATH), patient_data)
    return None

def _verify_update(patient_id: str, doctor_name:str, requested_slot:datetime) -> dict[Any, str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    _date, _time = _format_datetime(requested_slot)
    
    doctor = next((doc["doctor"] for doc in doctors_data if doc["doctor"]["name"] == doctor_name), None)
    patient = next((entry["patient"] for entry in patient_data if entry["patient_id"] == patient_id), None)
    
    if doctor is None:
        return {"error": f"Doctor {doctor_name} not found."}
    
    doctor_data_patient = next((entry for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    if doctor_data_patient is None:
        return {"error": f"Patient {patient_id} not found in doctor's records."}
    
    doctors_booked_appointments = next((entry for entry in doctor_data_patient["upcoming_appointments"] if entry["date"] == _date and entry["time"] == _time), None)
    if doctors_booked_appointments is None:
        return {"error": f"Doctor {doctor_name} has no appointments for that time."}
    
    
    if patient is None:
        return {"error": f"Patient {patient_id} not found."}
    
    patient_booked_appointment = next((entry for entry in patient["medical_info"]["appointments"] if entry["date"] == _date and entry["time"] == _time), None)
    if patient_booked_appointment is None:
        return {"error": f"Patient {patient_id} has no appointments for that time."}
    
    return {
        "patient": doctors_booked_appointments,
        "doctor": patient_booked_appointment,
    }