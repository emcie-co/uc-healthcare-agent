from contextlib import AsyncExitStack
from lagom import Container
from parlant.core.services.tools.plugins import tool
from parlant.core.tools import ToolContext, ToolResult, ToolParameterOptions

from parlant.sdk import (
    PluginServer,
    ServiceRegistry,
)

@tool
def test_my_tool(context: ToolContext, name: str) -> ToolResult:
    print({
        "context.customer_id": context.customer_id,
        "name": name
    })
    return ToolResult(data="this is the data", utterance_fields={
        "name": name,
        "position": "Solution Thingy",
    })

EXIT_STACK = AsyncExitStack()

PORT = 8199
TOOLS = [
test_my_tool
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
        name="tester",
        kind="sdk",
        url=f"http://{host}:{PORT}",
        transient=True,
    )

    await EXIT_STACK.enter_async_context(server)
    EXIT_STACK.push_async_callback(server.shutdown)


async def shutdown_module() -> None:
    await EXIT_STACK.aclose()

