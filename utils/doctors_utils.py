from typing import Any, Dict, List

def get_doctors_availabilities(_doctor_data:Dict[str, Any]) -> List[Dict[str, Any]]:
    if _doctor_data is None:
        raise ValueError("Doctor not found")
    
    availability = _doctor_data["practice_details"]["scheduling"]["availability"]
    if not isinstance(availability, list):
        raise TypeError(f"Expected a list, but got {type(availability)}")
    
    return availability

def get_doctor_patient_upcoming_appointments(_doctor_data:Dict[str, Any], patient_id:str) -> List[Dict[str, Any]]:
    if _doctor_data is None:
        raise ValueError("Doctor not found")
    
    patient = next((entry for entry in _doctor_data["patients"] if entry["patient_id"] == patient_id))
    if patient:
        upcoming_appointments = patient["upcoming_appointments"]
    if not isinstance(upcoming_appointments, list):
        raise TypeError(f"Expected a list, but got {type(upcoming_appointments)}")
    
    return upcoming_appointments