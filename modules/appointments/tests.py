from datetime import datetime
from typing import Annotated
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions
from modules.appointments._constants import AppointmentType

@tool
def schedule_appointment(context:ToolContext, doctor_name: str, requested_slot:datetime, appointment_type:AppointmentType = AppointmentType.REGULAR, )-> ToolResult:
    print({
        "context.customer_id": context.customer_id,
        "doctor_name": doctor_name,
        "requested_slot": requested_slot,
        "appointment_type": appointment_type
    })
        
    return ToolResult(f"Appointment scheduled with {doctor_name} on {requested_slot}.")


@tool
def reschedule_appointment(context:ToolContext, doctor_name:str, 
    scheduled_date:Annotated[datetime, ToolParameterOptions(
    description="Need the date and time for rescheduling")], 
    requested_date:Annotated[datetime, ToolParameterOptions(
    description="Need the date and time for rescheduling")]) -> ToolResult:
    
    print({
        "context.customer_id": context.customer_id,
        "doctor_name": doctor_name,
        "scheduled_date": scheduled_date,
        "requested_date": requested_date
    })
        
    return ToolResult(f"Appointment rescheduled with {doctor_name} on {requested_date}.")