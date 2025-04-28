from lagom import Container
from parlant.core.background_tasks import BackgroundTaskService
from parlant.core.services.tools.plugins import PluginServer
from parlant.core.services.tools.service_registry import ServiceRegistry
from modules.appointments.general import get_patient_data, get_doctors_availability
from modules.appointments.scheduling import schedule_appointment 
from modules.appointments.rescheduling import reschedule_appointment
from modules.appointments.canceling import cancel_appointment

server_instance: PluginServer | None = None


async def initialize_module(container: Container) -> None:
    global server_instance
    _background_task_service = container[BackgroundTaskService]

    server = PluginServer(
        tools=[
            get_patient_data,
            get_doctors_availability,
            schedule_appointment,
            reschedule_appointment,
            cancel_appointment
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
        name="appointments_management",
        kind="sdk",
        url="http://127.0.0.1:8094",
        transient=True,
    )


async def shutdown_module() -> None:
    global server_instance

    if server_instance is not None:
        await server_instance.shutdown()
        server_instance = None
