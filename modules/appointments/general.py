from datetime import datetime
from pathlib import Path
import json
from typing import List, TypedDict, cast
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions
from utils.date_utils import _sort_datetime
from utils.json_utils import _load_data

class DoctorAvailabilityItem(TypedDict):
    date: str
    times: List[str]

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def get_patient_data(context: ToolContext) -> ToolResult:
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((entry for entry in patients_data if entry["patient_id"] == context.customer_id), None)
    if patient:
        return ToolResult(data=patient)
        
    return ToolResult("Don't have information for this patient")

@tool
def get_doctors_availability(context: ToolContext, doctor_name:str) -> ToolResult:
    doctor_data=_load_data(Path(DOCTORSDB_PATH))
    doctor = next((entry for entry in doctor_data if entry["doctor"]["name"] == doctor_name), None)
    if doctor is None:
        return ToolResult(f"No doctor with the name {doctor_name}")
    
    availabilities = doctor["doctor"]["scheduling"]["availability"]
    # sorted_availability = _sort_datetime(availabilities)
    sorted_availability = _sort_datetime(cast(List[DoctorAvailabilityItem], availabilities))
    sorted_availability = availabilities
    
    return ToolResult(
        data=json.dumps(sorted_availability), 
        utterance_fields={
            "doctor_name": doctor_name, 
            "availabilities": availabilities
            })