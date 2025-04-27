from enum import Enum
from pathlib import Path
import json
from typing import Any, Dict
from datetime import datetime
from parlant.core.tools import ToolContext, ToolResult
from parlant.core.services.tools.plugins import tool

from utils.json_utils import _load_data, _update_data

from utils.date_utils import _format_datetime, _sort_datetime

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def load_doctor_availability(context: ToolContext, doctor_name:str) -> ToolResult:
    doctor_data=_load_data(Path(DOCTORSDB_PATH))
    doctor = next((entry for entry in doctor_data if entry["doctor"]["name"] == doctor_name), None)
    if doctor is None:
        return ToolResult(f"No doctor with the name {doctor_name}")
    availabilities = doctor["doctor"]["practice_details"]["scheduling"]["availability"]
    sorted_availability = _sort_datetime(availabilities)
    
    return ToolResult(data=json.dumps(sorted_availability), utterance_fields={"doctor_name": doctor_name, "availabilities": availabilities})

def schedule_doctor_appointment(patient_id:str, doctor_name: str, requested_schedule_date: datetime, type:Enum) -> Dict[str, Any] | str:
    
    _doctors_data_db = _load_data(Path(DOCTORSDB_PATH))
    _doctor = next((entry["doctor"] for entry in _doctors_data_db if entry["doctor"]["name"]==doctor_name), None)
    req_date_str, req_time_str = _format_datetime(requested_schedule_date)
    
    if _doctor is None:
        return (f"No doctor with the name {doctor_name}")
    
    _doctor_availability = _doctor["practice_details"]["scheduling"]["availability"]
    _doctor_patient_upcoming_appointments = next((entry["upcoming_appointments"] for entry in _doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if _doctor_patient_upcoming_appointments is None:
        return (f"No upcoming appointments for patient id {patient_id}")
    
    date_in_availability = next((entry for entry in _doctor_availability if entry["date"] == req_date_str and req_time_str in entry["times"]), None)
    
    if date_in_availability is None:
        return (f"Doctor {doctor_name} is not available on {req_date_str} at {req_time_str}")

    if date_in_availability["times"] and len(date_in_availability["times"]) > 1:
        date_in_availability["times"].remove(req_time_str)
    else: 
        _doctor_availability.remove(date_in_availability)
        
    _doctor_patient_upcoming_appointments.append(
        {
            "date": req_date_str,
            "time": req_time_str,
            "type": type.value,
            "lab_work_ordered": "--basic metabolic panel",
        })
    
    _update_data(Path(DOCTORSDB_PATH), _doctors_data_db)
    return (json.dumps(_doctor))


def reschedule_doctor_appointment(patient_id:str, doctor_name: str, scheduled_date: datetime, requested_date: datetime) -> Dict[str, Any] | str:
    print("-------------------------RESCHEUDLE DOCTOR APPOINTMENT START-------------------------")
    _doctors_data_db = _load_data(Path(DOCTORSDB_PATH))
    _doctor = next((entry["doctor"] for entry in _doctors_data_db if entry["doctor"]["name"]==doctor_name), None)
    
    if _doctor is None:
        return (f"No doctor with the name {doctor_name}")

    curr_date_str, curr_time_str = _format_datetime(scheduled_date)
    req_date_str, req_time_str = _format_datetime(requested_date)

    _doctor_availability = _doctor["practice_details"]["scheduling"]["availability"]
    _doctor_patient_upcoming_appointments = next((entry["upcoming_appointments"] for entry in _doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if _doctor_patient_upcoming_appointments is None:
        return (f"No upcoming appointments for patient id {patient_id}")

    availability_appointment_matched = next((entry for entry in _doctor_availability if entry["date"] == req_date_str and req_time_str in entry["times"]), None)
    
    if availability_appointment_matched is None:
        return (f" No availability is {doctor_name}'s schedule")
    print(availability_appointment_matched)
    if (
        availability_appointment_matched
        and availability_appointment_matched["times"]
        and len(availability_appointment_matched["times"]) > 1
    ):
        print(availability_appointment_matched)
        availability_appointment_matched["times"].remove(req_time_str)
        availability_appointment_matched["times"].append(curr_time_str)
    else:
        _doctor_availability.remove(availability_appointment_matched)

    # 1. access _doctor_patient_upcoming_appointments
    # 2. match currently_scheduled_date with the one that's on _doctor_patient_upcoming_appointments
    # 3. replace the date and time with requested_date date and time
    upcoming_appointment_matched = next((entry for entry in _doctor_patient_upcoming_appointments if entry["date"] == curr_date_str and entry["time"] == curr_time_str),None)
    if upcoming_appointment_matched is None:
        return (f" No upcoming appointments is {doctor_name}'s schedule")

    upcoming_appointment_matched["date"] = req_date_str
    upcoming_appointment_matched["time"] = req_time_str

    print("-------------------------RESCHEUDLE DOCTOR APPOINTMENT END-------------------------")
    _update_data(Path(DOCTORSDB_PATH), _doctors_data_db)
    return (json.dumps(_doctor))


def cancel_doctor_appointment(patient_id:str, doctor_name: str, scheduled_date: datetime, reason: str) -> Dict[str, Any] | str:
    _doctors_data_db = _load_data(Path(DOCTORSDB_PATH))
    _doctor = next((entry["doctor"] for entry in _doctors_data_db if entry["doctor"]["name"]==doctor_name), None)
    curr_date_str, curr_time_str = _format_datetime(scheduled_date)
    
    if _doctor is None:
        return (f"No doctor with the name {doctor_name}")

    _doctor_availability = _doctor["practice_details"]["scheduling"]["availability"]
    _doctor_patient_upcoming_appointments = next((entry["upcoming_appointments"] for entry in _doctor["patients"] if entry["patient_id"] == patient_id), None)
    
    if _doctor_patient_upcoming_appointments is None:
        return (f"No upcoming appointments for patient id {patient_id}")

    # 1. access _doctor_patient_upcoming_appointments
    # 2. match currently_scheduled_date with the one that's on _doctor_patient_upcoming_appointments
    # 3. add a status parameter in the object to ve "cancelled"
    
    
    upcoming_appointment_matched = next((entry for entry in _doctor_patient_upcoming_appointments if entry["date"] == curr_date_str and entry["time"] == curr_time_str), None)
    if upcoming_appointment_matched is None:
        return (f"No upcoming appointments for {doctor_name}")

    upcoming_appointment_matched["status"] = "cancelled"
    upcoming_appointment_matched["cancel_reason"] = reason

    availability_appointment_matched = next(
        (entry for entry in _doctor_availability if entry["date"] == curr_date_str),
        None,
    )
    if availability_appointment_matched is None:
        return (f"No availability for {doctor_name}")

    # 1. match _doctor_availability date with current date
    # 1. if date exists, add the time there
    # 3. if date doesn't exist add the date and times there
    if availability_appointment_matched:
        availability_appointment_matched["times"].append(curr_time_str)
    else:
        _doctor_availability.append({"date": curr_date_str, "times": [curr_time_str]})

    _update_data(Path(DOCTORSDB_PATH), _doctors_data_db)
    return (json.dumps(_doctors_data_db))
