from collections.abc import Awaitable, Callable
from typing import Any

from fastapi_socketio import SocketManager
from socketio import AsyncNamespace

from app import app

socket_manager = SocketManager(app=app)
EventHandler = Callable[[dict[str, Any], Callable[[dict[str, Any]], Awaitable[None]]], Awaitable[None]]


class DefaultNamespace(AsyncNamespace):
    def __init__(self, namespace: str | None = None) -> None:
        super().__init__(namespace)
        self.event_handlers: dict[str, EventHandler] = {}

    def register_event(self, event: str) -> Callable[[EventHandler], EventHandler]:
        def decorator(func: EventHandler) -> EventHandler:
            async def wrapped_function(sid: str, data: dict[str, Any]) -> None:
                async def callback(response: dict[str, Any]) -> None:
                    await self.emit(event, response, to=sid)

                await func(data, callback)

            self.event_handlers[event] = wrapped_function
            self.on(event, wrapped_function)
            return func

        return decorator


default_namespace = DefaultNamespace(namespace="/api/ws")
socket_manager._sio.register_namespace(default_namespace)  # noqa: SLF001
