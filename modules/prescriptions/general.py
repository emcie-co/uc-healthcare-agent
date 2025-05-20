from pathlib import Path
from typing import Optional
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult

from helpers.json import _load_data, _update_data
from helpers.general import find_entity

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def create_auth_request(context:ToolContext, doctor_name:str, type:str, medication:str, message:str, priority:str)->ToolResult:
    update_patient_data = _update_patient_data(context.customer_id, doctor_name, type, medication, message, priority)
    update_doctor_data = _update_doctor_data(context.customer_id, doctor_name, type, medication, message, priority)
    
    if update_patient_data and "error" in update_patient_data:
        return ToolResult(update_patient_data)
    
    if update_doctor_data and "error" in update_doctor_data:
        return ToolResult(update_doctor_data)
    
    return ToolResult(f"Authorization request for {medication} sent to {doctor_name}.")

def _update_patient_data(patient_id:str, doctor_name:str, type:str, medication:str, message:str, priority:str) -> Optional[str]:
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = find_entity(patients_data, "patient", "patient_id", patient_id)
    
    if patient is None:
        return f"error: Patient {patient_id} not found."
    
    requests = patient["medical_info"].setdefault("requests", [])
    requests.append({
        "type": type,
        "medication": medication,
        "message": message,
        "status": "pending",
        "priority": priority,
        "process_time": "2-3 business days",
    })
    
    _update_data(Path(PATIENTSDB_PATH), patients_data)
    
    return None

def _update_doctor_data(patient_id:str, doctor_name:str, type:str, medication:str, message:str, priority:str) -> Optional[str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    doctor = find_entity(doctors_data, "doctor", "name", doctor_name)
    if doctor is None:
        return f"error: Doctor {doctor_name} not found."
    
    patient = next((entry for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if patient is None:
        return f"error: Patient {patient_id} not found."
    
    requests = patient.setdefault("requests", [])
    requests.append({
        "type": type,
        "medication": medication,
        "message": message,
        "status": "pending",
        "priority": priority,
        "process_time": "2-3 business days",
    })
    
    _update_data(Path(DOCTORSDB_PATH), doctors_data)
    
    return None

@tool
def update_auth_request(context:ToolContext, doctor_name:str, medication:str, priority:str) -> ToolResult:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    doctor = find_entity(doctors_data, "doctor", "name", doctor_name)
    
    if doctor is None:
        return ToolResult(f"Doctor {doctor_name} not found.")
    
    from_patient = next((entry for entry in doctor["patients"] if entry["patient_id"] ==  context.customer_id), None)
    
    if from_patient is None:
        return ToolResult(f"Patient {context.customer_id} not found.")
    
    from_patient_request = find_entity(from_patient["requests"], "requests", "medication", medication)
    if from_patient_request is None:
        return ToolResult(f"Request for {medication} not found.")
    
    from_patient_request["priority"] = "urgent"
    
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = find_entity(patients_data, "patient", "patient_id", context.customer_id)
    
    if patient is None:
        return ToolResult(f"Patient {context.customer_id} not found.")
    
    patient_request = find_entity(from_patient["requests"], "requests", "medication", medication)
    if patient_request is None:
        return ToolResult(f"Request for {medication} not found.")
    
    patient_request["priority"] = "urgent"
    
    return ToolResult(f"Authorization request for {medication} updated to urgent.")