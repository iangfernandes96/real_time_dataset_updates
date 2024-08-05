# type: ignore
from fastapi import WebSocket
from typing import Dict, Set
import redis
from src.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_CONNECTION_KEY,
    REDIS_USER_ID_COUNTER,
    REDIS_CHANNEL
)
import threading
import asyncio
from redis.exceptions import ConnectionError


class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )
        self.connections_key = REDIS_CONNECTION_KEY
        self.connections: Dict[int, WebSocket] = {}
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe(REDIS_CHANNEL)

    def start_listener(self):
        threading.Thread(target=self.listen_to_channel, daemon=True).start()

    def listen_to_channel(self):
        while True:
            try:
                for message in self.pubsub.listen():
                    if message['type'] == 'message':
                        asyncio.run(self.handle_message(message['data']))
            except ConnectionError:
                print("Connection closed by server, retrying...")
                self.redis_client = redis.Redis(host=REDIS_HOST,
                                                port=REDIS_PORT, db=0,
                                                decode_responses=True)
                self.pubsub = self.redis_client.pubsub()
                self.pubsub.subscribe(REDIS_CHANNEL)

    async def handle_message(self, message):
        active_connections = await self.get_active_connections()
        for user_id in active_connections:
            user_id = int(user_id)
            await self.send_message_to_user(user_id, {"message": message})

    def get_new_user_id(self):
        return self.redis_client.incr(REDIS_USER_ID_COUNTER)

    async def get_active_connections(self) -> Set:
        active_connections = self.redis_client.smembers(self.connections_key)
        if active_connections:
            active_connections = set(active_connections)
            return {int(conn_id) for conn_id in active_connections}
        return set()

    async def connect(self, websocket: WebSocket, connection_id: int):
        await websocket.accept()
        self.connections[connection_id] = websocket
        self.redis_client.sadd(self.connections_key, connection_id)

    async def disconnect(self, user_id: int):
        if user_id in self.connections:
            websocket = self.connections.pop(user_id)
            try:
                await websocket.close()
            except RuntimeError:
                print("Websocket already closed")
                pass
        self.redis_client.srem(self.connections_key, user_id)

    async def send_message_to_user(self, user_id: int, message: dict) -> bool:
        if user_id in self.connections:
            websocket = self.connections[user_id]
            await websocket.send_json(message)
            return True
        return False

    async def send_message_to_all_users(self, message: dict) -> bool:
        msgs_sent = False
        active_connections = await self.get_active_connections()
        for user_id in active_connections:
            user_id = int(user_id)
            msgs_sent = await self.send_message_to_user(user_id, message)
        return msgs_sent

    def publish_message(self, message: str):
        self.redis_client.publish(REDIS_CHANNEL, message)
