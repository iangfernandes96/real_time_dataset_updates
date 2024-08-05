import pytest
from unittest.mock import MagicMock, patch
from fastapi import WebSocket
from src.utils.websocket_manager import ConnectionManager
from src.config import (REDIS_CONNECTION_KEY, REDIS_CHANNEL)


@pytest.fixture
def mock_redis(mocker):
    mock_redis = mocker.patch('src.utils.websocket_manager.redis.Redis',
                              autospec=True)
    return mock_redis


@pytest.fixture
def connection_manager(mock_redis):
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect(connection_manager, mock_redis):
    mock_websocket = MagicMock(spec=WebSocket)
    connection_id = 1
    await connection_manager.connect(mock_websocket, connection_id)
    assert connection_manager.connections[connection_id] == mock_websocket
    mock_redis().sadd.assert_called_once_with(REDIS_CONNECTION_KEY,
                                              connection_id)
    mock_websocket.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect(connection_manager, mock_redis):
    mock_websocket = MagicMock(spec=WebSocket)
    connection_id = 1
    await connection_manager.connect(mock_websocket, connection_id)
    await connection_manager.disconnect(connection_id)
    assert connection_id not in connection_manager.connections
    mock_redis().srem.assert_called_once_with(REDIS_CONNECTION_KEY,
                                              connection_id)
    mock_websocket.close.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_to_user(connection_manager):
    mock_websocket = MagicMock(spec=WebSocket)
    connection_id = 1
    message = {"message": "test"}
    await connection_manager.connect(mock_websocket, connection_id)
    result = await connection_manager.send_message_to_user(connection_id,
                                                           message)
    assert result is True
    mock_websocket.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_message_to_all_users(connection_manager, mock_redis):
    mock_websocket_1 = MagicMock(spec=WebSocket)
    mock_websocket_2 = MagicMock(spec=WebSocket)
    connection_id_1 = 1
    connection_id_2 = 2
    message = {"message": "test"}

    await connection_manager.connect(mock_websocket_1, connection_id_1)
    await connection_manager.connect(mock_websocket_2, connection_id_2)
    mock_redis().smembers.return_value = {str(connection_id_1),
                                          str(connection_id_2)}
    result = await connection_manager.send_message_to_all_users(message)
    assert result is True
    mock_websocket_1.send_json.assert_called_once_with(message)
    mock_websocket_2.send_json.assert_called_once_with(message)


def test_publish_message(connection_manager, mock_redis):
    message = "test message"
    connection_manager.publish_message(message)
    mock_redis().publish.assert_called_once_with(REDIS_CHANNEL, message)


def test_start_listener(connection_manager):
    with patch.object(connection_manager, 'listen_to_channel',
                      return_value=None) as mock_listen:
        connection_manager.start_listener()
        mock_listen.assert_called_once()
