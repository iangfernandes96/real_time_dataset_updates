from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from src.utils.websocket_manager import ConnectionManager

from .utils import measure_latency

ws_manager = ConnectionManager()

ws_router = APIRouter()

templates = Jinja2Templates(directory="templates")


async def register_user(websocket: WebSocket, user_id: int):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            print(f"Accepted connection for user {user_id}")
            data = await websocket.receive_text()
            await websocket.send_text(f"{user_id} {data}")
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id)


@ws_router.route("/get_user_id")
@measure_latency
async def get_user_id(request):
    return JSONResponse({"user_id": ws_manager.get_new_user_id()})


@ws_router.route("/dashboard")
@measure_latency
async def login_endpoint(request):
    return templates.TemplateResponse("index.html", {"request": request})


@ws_router.websocket("/user/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await register_user(websocket, user_id)
