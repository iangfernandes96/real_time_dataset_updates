from src.data import DatasetManager
from typing import Dict, Callable
from functools import wraps
import asyncio

from src.utils.websocket_manager import ConnectionManager

websocket_connection_manager = ConnectionManager()


def measure_latency(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = asyncio.get_event_loop().time()
        result = await func(*args, **kwargs)
        end_time = asyncio.get_event_loop().time()
        latency = (end_time - start_time) * 1000
        print(f"Latency for {func.__name__}: {round(latency, 4)}ms")
        return result

    return wrapper


@measure_latency
async def operate_and_update(
    dataset_manager: DatasetManager, column: str, user_id: int
) -> bool:
    try:
        await dataset_manager.apply_update_function(column)
        print("Dataset updated")
        notification_msg = f"Column {column} updated by user {user_id}"
        websocket_connection_manager.publish_message(notification_msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


async def notify_all_users(message: str) -> Dict[str, str]:
    message_dict = {"message": message}
    await websocket_connection_manager.send_message_to_all_users(message_dict)
    return {"status": "notification sent"}
