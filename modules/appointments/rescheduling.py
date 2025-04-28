from datetime import datetime
from pathlib import Path
from typing import Any, Optional,Annotated
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions
from utils.date_utils import _format_datetime
from utils.json_utils import _load_data, _update_data

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def reschedule_appointment(context:ToolContext, doctor_name:str, scheduled_date:Annotated[datetime, ToolParameterOptions(
    description="Need the date and time for rescheduling")], requested_date:Annotated[datetime, ToolParameterOptions(
    description="Need the date and time for rescheduling")]) -> ToolResult:

    updated_doctor_result = _update_doctor_data(context.customer_id, doctor_name, scheduled_date, requested_date)
    if updated_doctor_result:
        return ToolResult(updated_doctor_result)
    
    updated_patient_result = _update_patient_data(context.customer_id, doctor_name, scheduled_date, requested_date)
    if updated_patient_result:
        return ToolResult(updated_patient_result)
    
    verified_result = _verify_update(context.customer_id, doctor_name,  scheduled_date, requested_date)
    if "error" in verified_result:
        return ToolResult(verified_result["error"])
    
    return ToolResult("")

def _update_doctor_data(patient_id:str, doctor_name:str, scheduled_date:datetime, requested_date:datetime) -> Optional[str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    doctor = next((doc["doctor"] for doc in doctors_data if doc["doctor"]["name"] == doctor_name), None)
    
    if doctor is None:
        return f"Doctor {doctor_name} not found."
    
    scheduled_date_slot, scheduled_time_slot = _format_datetime(scheduled_date)
    requested_date_slot, requested_time_slot = _format_datetime(requested_date)
    
    availabilities = doctor["scheduling"]["availability"]
    
    requested_slot_in_availabilities = next((entry for entry in availabilities if entry["date"] == requested_date_slot and requested_time_slot in entry["times"]), None)
    if requested_slot_in_availabilities is None:
        return f"--Doctor {doctor_name} is not available at {requested_date_slot} at {requested_time_slot}."
    
    # this is also for structuring the json properly. can be removed if we're working with a proper db. It simply removes the object if it's empty
    if requested_slot_in_availabilities["times"] and len(requested_slot_in_availabilities["times"]) > 1:
        requested_slot_in_availabilities["times"].remove(requested_time_slot)
    else:
        availabilities.remove(requested_slot_in_availabilities)
    
    scheduled_slot_in_availabilities = next((entry for entry in availabilities if entry["date"] == scheduled_date_slot), None)
    if scheduled_slot_in_availabilities is None:
        availabilities.append({
            "date": scheduled_date_slot,
            "times": [scheduled_time_slot],
        })
    else: 
        scheduled_slot_in_availabilities["times"].append(scheduled_time_slot)
        
    upcoming_appointments = next((entry["upcoming_appointments"] for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if upcoming_appointments is None:
        return f"Patient {patient_id} not found in doctor's records."
    
    matched_scheduled_appointment = next((entry for entry in upcoming_appointments if entry["date"] == scheduled_date_slot and entry["time"] == scheduled_time_slot), None)
    if matched_scheduled_appointment is None:
        return f"Patient {patient_id} has no appointment scheduled on {scheduled_date}."
    
    matched_scheduled_appointment["date"] = requested_date_slot
    matched_scheduled_appointment["time"] = requested_time_slot
    
    _update_data(Path(DOCTORSDB_PATH), doctors_data)
    return None

def _update_patient_data(patient_id:str, doctor_name:str, scheduled_date:datetime, requested_date:datetime) -> Optional[str]:
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((pat for pat in patient_data if pat["patient_id"] == patient_id), None)
    scheduled_date_slot, scheduled_time_slot = _format_datetime(scheduled_date)
    requested_date_slot, requested_time_slot = _format_datetime(requested_date)
    
    if patient is None:
        return f"Patient {patient_id} not found."
    
    appointments = patient["medical_info"]["appointments"]
    matched_appointment = next((entry for entry in appointments if entry["date"] == scheduled_date_slot and entry["time"] == scheduled_time_slot), None)
    
    if matched_appointment is None:
        return f"Patient {patient_id} has no appointment scheduled on {scheduled_date}."
    
    matched_appointment["date"] = requested_date_slot
    matched_appointment["time"] = requested_time_slot
    
    _update_data(Path(PATIENTSDB_PATH), patient_data)
    return None

def _verify_update(patient_id:str, doctor_name:str, scheduled_date:datetime, requested_date:datetime) -> dict[Any, str]:
    doctors_data = _load_data(Path(DOCTORSDB_PATH))
    patient_data = _load_data(Path(PATIENTSDB_PATH))
    scheduled_date_slot, scheduled_time_slot = _format_datetime(scheduled_date)
    requested_date_slot, requested_time_slot = _format_datetime(requested_date)
    
    doctor = next((doc["doctor"] for doc in doctors_data if doc["doctor"]["name"] == doctor_name), None)
    if doctor is None:  
        return {"error": f"Doctor {doctor_name} not found."}
    
    doctor_availabilities = doctor["scheduling"]["availability"]
    if doctor_availabilities is None:
        return {"error": "1. Issue with the appointment rescheduling."}
    
    requested_slot_in_availabilities = next((entry for entry in doctor_availabilities if entry["date"] == requested_date_slot and requested_time_slot in entry["times"]), None)
    
    if requested_slot_in_availabilities:
        return {"error": "2. Issue with the appointment rescheduling."}
    
    scheduled_slot_in_availabilities = next((entry for entry in doctor_availabilities if entry["date"] == scheduled_date_slot and scheduled_time_slot in entry["times"]), None)
    
    if scheduled_slot_in_availabilities is None:
        return {"error": "3. Issue with the appointment rescheduling."}
    
    doctor_patient_upcoming = next((entry["upcoming_appointments"] for entry in doctor["patients"] if entry["patient_id"] == patient_id), None)
    if doctor_patient_upcoming is None:
        return {"error": "4. Issue with the appointment rescheduling."}
    
    doctor_patient_upcoming_match = next((entry for entry in doctor_patient_upcoming if entry["date"] == requested_date_slot and entry["time"] == requested_time_slot), None)
    
    if doctor_patient_upcoming_match is None:
        return {"error": "5. Issue with the appointment rescheduling."}
    
    doctor_patient_upcoming_non_match = next((entry for entry in doctor_patient_upcoming if entry["date"] == scheduled_date_slot and entry["time"] == scheduled_time_slot), None)
    
    if doctor_patient_upcoming_non_match:
        print(doctor_patient_upcoming_non_match)
        return {"error": "6. Issue with the appointment rescheduling."}
        
    patient = next((pat for pat in patient_data if pat["patient_id"] == patient_id), None)
    if patient is None:  
        return {"error": f"Patient {patient_id} not found."}
    
    patient_appointments = patient["medical_info"]["appointments"]
    
    patient_appointments_requested = next((entry for entry in patient_appointments if entry["date"] == requested_date_slot and entry["time"] == requested_time_slot), None)
    patient_appointments_scheduled = next((entry for entry in patient_appointments if entry["date"] == scheduled_date_slot and entry["time"] == scheduled_time_slot), None)
    
    if patient_appointments_requested is None or patient_appointments_scheduled:
        return {"error": "7. Issue with the appointment rescheduling."}
    
    return {
        "patient": patient_appointments_requested,
        "doctor": doctor_patient_upcoming_match,
    }