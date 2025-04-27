from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict
from parlant.core.services.tools.plugins import tool
from datetime import datetime
from parlant.core.tools import ToolContext, ToolResult

from utils.json_utils import _load_data, _update_data
from utils.date_utils import _format_datetime

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def load_patient_by_id(context: ToolContext) -> ToolResult:
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((entry for entry in patients_data if entry["patient_id"] == context.customer_id), None)
    if patient:
        return ToolResult(data=patient)
        
    return ToolResult("Don't have information for this patient")


def schedule_patient_appointment(patient_id:str, doctor_name:str, requested_date:datetime, type:Enum, preperation:str)->Dict[str, Any] | str | Any:
    _patients_data_db = _load_data(Path(PATIENTSDB_PATH))
    _patient= next((entry for entry in _patients_data_db if entry["patient_id"] == patient_id), None)
    req_date_str, req_time_str = _format_datetime(requested_date)

    if _patient is None:
        return (f"Patient {patient_id} not found")
    
    _patient_appointments = _patient["medical_info"]["appointments"]
    if _patient_appointments is None:
        return (f"No appointments found for {patient_id}")
    
    _patient_appointments_match = next((entry for entry in _patient_appointments if entry["doctor"] == doctor_name and entry["date"] != req_date_str and entry["time"] != req_time_str), None)
    if _patient_appointments_match:
        _patient_appointments.append({
            "doctor": doctor_name,
            "type": type.value,
            "date": req_date_str,
            "time": req_time_str,
            "location": None,
            "status": "scheduled",
            "preparation": preperation
        })
    _update_data(Path(PATIENTSDB_PATH), _patients_data_db)
    return (json.dumps(_patient))


def reschedule_patient_appointment(patient_id:str, doctor_name:str, scheduled_date:datetime, requested_date:datetime)->Dict[str, Any] | str :
    _patients_data_db = _load_data(Path(PATIENTSDB_PATH))
    _patient= next((entry for entry in _patients_data_db if entry["patient_id"] == patient_id), None)
    curr_date_str, curr_time_str = _format_datetime(scheduled_date)
    req_date_str, req_time_str = _format_datetime(requested_date)

    if _patient is None:
        return (f"Patient {patient_id} not found")
    
    
    _patient_appointments = _patient["medical_info"]["appointments"]
    if _patient_appointments is None:
        return (f"No appointments found for {patient_id}")
    
    _patient_current_appointment = next((entry for entry in _patient_appointments if entry["doctor"] == doctor_name and entry["date"] == curr_date_str and entry["time"] == curr_time_str), None)
    if _patient_current_appointment:
        _patient_current_appointment["date"] = req_date_str
        _patient_current_appointment["time"] = req_time_str
        _patient_current_appointment["status"] = "rescheduled"
    
    _update_data(Path(PATIENTSDB_PATH), _patients_data_db)
    return (json.dumps(_patient))


def cancel_patient_appointment(patient_id:str, doctor_name:str, scheduled_date:datetime, reason:str)->Dict[str, Any] | str:
    print('----------------CANCEL APPOINTMENT START----------------')
    _patients_data_db = _load_data(Path(PATIENTSDB_PATH))
    _patient= next((entry for entry in _patients_data_db if entry["patient_id"] == patient_id), None)
    curr_date_str, curr_time_str = _format_datetime(scheduled_date)
    print(curr_date_str)
    print(curr_time_str)
    if _patient is None:
        return (f"Patient {patient_id} not found")
    
    _patient_appointments = _patient["medical_info"]["appointments"]
    print(_patient_appointments)
    if _patient_appointments is None:
        return (f"No appointments found for {patient_id}")
    
    _patient_current_appointment = next((entry for entry in _patient_appointments if entry["doctor"] == doctor_name and entry["date"] == curr_date_str and entry["time"] == curr_time_str), None)
    print(_patient_current_appointment)
    if _patient_current_appointment:
        _patient_current_appointment["status"] = "cancelled"
        _patient_current_appointment["cancel_reason"] = reason
        
    _update_data(Path(PATIENTSDB_PATH), _patients_data_db)
    print('----------------CANCEL APPOINTMENT END----------------')
    return (json.dumps(_patient_current_appointment))

