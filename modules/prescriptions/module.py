from contextlib import AsyncExitStack
from lagom import Container

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
)

from modules.prescriptions.general import create_auth_request, update_auth_request

EXIT_STACK = AsyncExitStack()

PORT = 8200
TOOLS = [
create_auth_request, update_auth_request
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
        name="prescriptions",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()

