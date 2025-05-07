from pathlib import Path
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult
from utils.date_utils import _sort_datetime
from utils.json_utils import _load_data


PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

@tool
def get_patient_data(context: ToolContext) -> ToolResult:
    patients_data = _load_data(Path(PATIENTSDB_PATH))
    patient = next((entry["patient"] for entry in patients_data if entry["patient"]["patient_id"] == context.customer_id), None)
    if patient is None:
        return ToolResult("Don't have information for this patient")
    
    scheduled_appointments = patient["medical_info"]["appointments"]
    if scheduled_appointments is None:
        return ToolResult("No scheduled appointments found for this patient")
    
    next_appointment = _sort_datetime(scheduled_appointments)[0]
        
    return ToolResult(
        data=patient, 
        utterance_fields={
        "patient_name": patient["name"],
        "scheduled_appointments":patient["medical_info"]["appointments"],
        "scheduled_date_slot": next_appointment["date"],
        "scheduled_time_slot": next_appointment["time"],
        "lab_work_details": patient["medical_info"]["lab_work"][0]["instructions"],
    })


@tool
def get_doctors_availability(context: ToolContext, doctor_name:str) -> ToolResult:
    doctors_data=_load_data(Path(DOCTORSDB_PATH))
    doctor = next((entry["doctor"] for entry in doctors_data if entry["doctor"]["name"] == doctor_name), None)
    
    if doctor is None:
        return ToolResult(f"No doctor with the name {doctor_name}")
    
    availabilities = doctor["scheduling"]["availability"]
    sorted_availability = _sort_datetime(availabilities)
    sorted_availability = availabilities
    
    first_two_slots = []
    for entry in sorted_availability:
        if entry["times"]:
            for time in entry["times"]:
                first_two_slots.append({"date": entry["date"], "time": time})
                if len(first_two_slots) == 2:
                    break
            if len(first_two_slots) == 2:
                break

    return ToolResult(
        data=sorted_availability,
        utterance_fields={
            "doctor_name": doctor_name,
            "first_date_slot": first_two_slots[0]["date"],
            "first_time_slot": first_two_slots[0]["time"],
            "second_date_slot": first_two_slots[1]["date"],
            "second_time_slot": first_two_slots[1]["time"],
        },
    )