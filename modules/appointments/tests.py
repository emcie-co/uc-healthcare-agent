from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Optional
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions
from utils.date_utils import _format_datetime
from utils.json_utils import _load_data, _update_data

PATIENTSDB_PATH = "./data/patients.json"
DOCTORSDB_PATH = "./data/doctors.json"

doctor_name = "Dr. Chen"
# doctors_data = _load_data(Path(DOCTORSDB_PATH))
patient_data = _load_data(Path(PATIENTSDB_PATH))
# doctor = next((doc["doctor"] for doc in doctors_data if doc["doctor"]["name"] == doctor_name), None)
patient = next((pat for pat in patient_data if pat["patient_id"] == "C9XHUuuk1J"), None)

if patient:
    patient_appointments = patient["medical_info"]["appointments"]
    print(patient_appointments)





# patient_appointment = patient["medical_info"]["appointments"]


# if not patient_appointment:
#     print(f"No appointments found for patient {patient['patient_id']}")

# patient_booked_appointment = next((entry for entry in patient_appointment if entry["date"] == "2025-03-30" and entry["time"] == "10:30"), None)

# if not patient_booked_appointment:
#     print(f"Patient {doctor_name} not found in doctor's records.")

# print(doctor)
