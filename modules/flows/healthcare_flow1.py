from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from lagom import Container
import json
from parlant.core.background_tasks import BackgroundTaskService
from parlant.core.services.tools.plugins import PluginServer, tool
from parlant.core.services.tools.service_registry import ServiceRegistry
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions

from modules.doctors import (
    load_doctor_availability,
    schedule_doctor_appointment,
    reschedule_doctor_appointment,
    cancel_doctor_appointment,
)

from modules.patients import (
    load_patient_by_id,
    schedule_patient_appointment,
    reschedule_patient_appointment,
    cancel_patient_appointment,
)

server_instance: PluginServer | None = None


class AppointmentType(Enum):
    REGULAR = "Regular Appointment"
    FOLLOW_UP = "Follow Up"
    ROUTINE = "Routine Check-up"
    SICK = "Sick Visit"
    CONSULTATION = "Consultation Appointment"
    TREATMENT = "Treatment Appointment"
    PRE_POST_OPERATION = "Pre-Operative or Post-Operative Visit"
    ANNUAL = "Annual Physical"
    ORTHOPEDIC = "Orthopedic Consultation"
    MRI = "MRI Scan"


PREPARATION_INSTRUCTIONS = {
    AppointmentType.REGULAR: "Nothing special. Bring your current medications and any medical record you want the doctor to view",
    AppointmentType.FOLLOW_UP: "Nothing special. Bring your current medications and any medical record you want the doctor to view",
    AppointmentType.ROUTINE: "Nothing",
    AppointmentType.SICK: "Wear a mask and list symptoms beforehand.",
    AppointmentType.CONSULTATION: "Bring your referral form, relevant medical records/test results.",
    AppointmentType.TREATMENT: "Bring current medications, insurance card and comfortable clothing",
    AppointmentType.PRE_POST_OPERATION: "For pre-op: bring insurance cards, medication list, and advance directive if you have one; for post-op: bring wound care supplies and your discharge instructions.",
    AppointmentType.ANNUAL: "Bring your complete medication list, immunization records, and come fasting if bloodwork is planned (water is permitted).",
    AppointmentType.ORTHOPEDIC: "Bring recent X-rays or MRI scans.",
    AppointmentType.MRI: "Avoid wearing metal objects. Bring your referral form, wear metal-free clothing (no zippers, underwire, jewelry), and inform staff of any implants or claustrophobia concerns.",
}

@tool
def schedule_appointment(
    context: ToolContext,
    doctor_name: str,
    requested_date: datetime,
    type: Annotated[
        Optional[AppointmentType],
        ToolParameterOptions(
            significance="Need to know what type of appointment in order to schedule it"
        ),
    ]=AppointmentType.REGULAR,
) -> ToolResult:
    if type is None:
        type = AppointmentType.REGULAR
    print(f"Requested appointment type: {type.value}")
    confirmation = {
        "doctor": schedule_doctor_appointment(
            context.customer_id, doctor_name, requested_date, type
        ),
        "patient": schedule_patient_appointment(
            context.customer_id,
            doctor_name,
            requested_date,
            type,
            preperation=PREPARATION_INSTRUCTIONS[type],
        ),
    }
    seriazable_confirmation = json.dumps(confirmation)
    print(seriazable_confirmation)
    return ToolResult(seriazable_confirmation)


@tool
def reschedule_appointment(
    context: ToolContext,
    doctor_name: str,
    scheduled_date: datetime,
    requested_date: datetime,
) -> ToolResult:
    confirmation = {
        "doctor": reschedule_doctor_appointment(
            context.customer_id, doctor_name, scheduled_date, requested_date
        ),
        "patient": reschedule_patient_appointment(
            context.customer_id, doctor_name, scheduled_date, requested_date
        ),
    }
    return ToolResult(json.dumps(confirmation))


@tool
def cancel_appointment(context:ToolContext, doctor_name:str, scheduled_date: datetime, reason:str) -> ToolResult:
    print(scheduled_date)
    confirmation = {
        "doctor": cancel_doctor_appointment(context.customer_id, doctor_name, scheduled_date, reason),
        "patient": cancel_patient_appointment(context.customer_id, doctor_name, scheduled_date, reason),
    }
    return ToolResult(json.dumps(confirmation))


async def initialize_module(container: Container) -> None:
    global server_instance
    _background_task_service = container[BackgroundTaskService]

    server = PluginServer(
        tools=[
            load_patient_by_id,
            load_doctor_availability,
            schedule_appointment,
            reschedule_appointment,
            cancel_appointment,
        ],
        port=8094,
        host="127.0.0.1",
        hosted=True,
    )

    await _background_task_service.start(
        server.serve(),
        tag="Healthcare Plugin",
    )

    server_instance = server

    service_registry = container[ServiceRegistry]
    await service_registry.update_tool_service(
        name="healthcare",
        kind="sdk",
        url="http://127.0.0.1:8094",
        transient=True,
    )


async def shutdown_module() -> None:
    global server_instance

    if server_instance is not None:
        await server_instance.shutdown()
        server_instance = None
