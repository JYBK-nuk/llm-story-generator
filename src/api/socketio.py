from collections.abc import Awaitable, Callable
from typing import Any

import socketio

# 定義事件處理器的類型
EventHandler = Callable[[dict[str, Any], Callable[[dict[str, Any]], Awaitable[None]]], Awaitable[None]]


class SocketServer:
    def __init__(self) -> None:
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

    def register_event(self, event: str) -> Callable[[EventHandler], EventHandler]:
        def decorator(func: EventHandler) -> EventHandler:
            async def wrapped_function(sid: str, data: dict[str, Any]) -> None:
                async def callback(response: dict[str, Any]) -> None:
                    # 發送回應給客戶端
                    print(f"Sending response to event: {event} with data: {response} to sid: {sid}")
                    await self.sio.emit(event, response, to=sid)

                async def sent_event(event: str, data: dict[str, Any]) -> None:
                    await self.sio.emit(event, data, to=sid)

                await func(data, callback, sent_event)

            # 註冊事件
            print(f"Registering event: {event}")
            self.sio.on(event, wrapped_function)
            return func

        return decorator


# 實例化 SocketServer
ws = SocketServer()
