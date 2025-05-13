from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult
from helpers.date import _format_datetime
from helpers.json import _load_data, _update_data
from helpers.general import find_entity, match_availability, match_slot, remove_time_from_availability

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
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    
    doctor = find_entity(doctors_data, "doctor", "name", doctor_name)
    patient = find_entity(patients_data, "patient", "patient_id", patient_id)
    
    if doctor is None:
        return f"Doctor {doctor_name} not found."
    if patient is None:
        return f"Patient {patient_id} not found."
    
    _date, _time = _format_datetime(requested_slot)
    slot = match_availability(doctor["scheduling"]["availability"], _date, _time)
    
    if slot is None:
        return f"Doctor {doctor_name} is not available at {requested_slot}."
    
    remove_time_from_availability(doctor["scheduling"]["availability"], slot, _time)
    
    patients = doctor.setdefault("patients", [])
    patient_record = next((p for p in patients if p["patient_id"] == patient_id), None)
    if patient_record is None:
        patient_record = {
            "patient_id": patient_id,
            "name": patient["name"],
            "relationship": "primary care",
            "last_visit": "null",
            "upcoming_appointments": [],
        }
        patients.append(patient_record)
    
        patient_record.setdefault("upcoming_appointments", []).append({
        "date": _date,
        "time": _time,
        "type": appointment_type.value,
        "lab_work_ordered": "--basic metabolic panel",
    })
    
    _update_data(Path(DOCTORSDB_PATH), doctors_data)
    
    return None

def _update_patient_data(patient_id: str, doctor_name:str, requested_slot:datetime, appointment_type:AppointmentType) -> Optional[str]:
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = find_entity(patients_data, "patient", "patient_id", patient_id)
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
    _update_data(Path(PATIENTSDB_PATH), patients_data)
    
    return None

def _verify_update(patient_id: str, doctor_name:str, requested_slot:datetime) -> dict[str, Any]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    _date, _time = _format_datetime(requested_slot)
    
    doctor = find_entity(doctors_data, "doctor", "name", doctor_name)
    patient = find_entity(patients_data, "patient", "patient_id", patient_id)
    
    if doctor is None:
        return {"error": f"Doctor {doctor_name} not found."}
    
    patient_from_doctor = next((p for p in doctor["patients"] if p["patient_id"] == patient_id), None)
    
    if patient_from_doctor is None:
        return {"error": f"Patient {patient_id} not found in doctor's records."}
    
    booked_from_doctor = match_slot(patient_from_doctor["upcoming_appointments"], _date, _time)
    if booked_from_doctor is None:
        return {"error": f"Doctor {doctor_name} has no appointments for that time."}
    
    if patient is None:
        return {"error": f"Patient {patient_id} not found."}
    
    booked_from_patient = match_slot(patient["medical_info"]["appointments"], _date, _time)
    if booked_from_patient is None:
        return {"error": f"Patient {patient_id} has no appointments for that time."}
    
    return {
        "patient": booked_from_doctor,
        "doctor": booked_from_patient,
    }