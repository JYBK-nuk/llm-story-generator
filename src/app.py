import socketio
from fastapi import FastAPI

from api import api_router
from api.socketio import ws

app = FastAPI()

app.mount("/socket.io", socketio.ASGIApp(ws.sio))
app.include_router(router=api_router)


@app.get("/")
def read_root() -> dict:
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
