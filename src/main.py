from fastapi import FastAPI
from src.resources import router, websocket_router
from fastapi_lifespan_manager import LifespanManager
from src.utils.websocket_manager import ConnectionManager


manager = LifespanManager()
connection_manager = ConnectionManager()


@manager.add  # type: ignore
async def start_redis_listener(app: FastAPI):
    connection_manager.start_listener()
    yield


app = FastAPI(lifespan=manager)

app.include_router(router.dataset_manager_router, prefix="/data")
app.include_router(websocket_router.ws_router, prefix="/ws")
