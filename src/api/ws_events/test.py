from collections.abc import Awaitable, Callable
from typing import Any

from api.socketio import default_namespace


@default_namespace.register_event("name")
async def handle_name_event(
    data: dict[str, Any],
    callback: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    print(f"Received 'name' event with data: {data}")
    response = {"message": f"Hello, {data.get('payload', {}).get('name', 'Anonymous')}!"}
    await callback(response)


@default_namespace.register_event("message")
async def handle_message_event(
    data: dict[str, Any],
    callback: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    print(f"Received 'message' event with data: {data}")
    response = {"message": f"Message received: {data.get('payload', {}).get('text', '')}"}
    await callback(response)
