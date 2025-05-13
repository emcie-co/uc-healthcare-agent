from contextlib import AsyncExitStack
from lagom import Container

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
)

from modules.appointments.general import get_patient_data, get_doctors_availability
# from modules.appointments.scheduling import schedule_appointment 
# from modules.appointments.rescheduling import reschedule_appointment
from modules.appointments.canceling import cancel_appointment

from modules.appointments.tests import schedule_appointment, reschedule_appointment

EXIT_STACK = AsyncExitStack()

PORT = 8199
TOOLS = [
    get_patient_data,
    get_doctors_availability,
    schedule_appointment,
    reschedule_appointment,
    cancel_appointment
]

async def initialize_module(container: Container) -> None:
    host = "127.0.0.1"

    server = PluginServer(
        tools=TOOLS,
        port=PORT,
        host=host,
        hosted=True,
    )

    await container[ServiceRegistry].update_tool_service(
        name="appointments",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()

