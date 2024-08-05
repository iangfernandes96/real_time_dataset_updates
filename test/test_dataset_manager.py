import pytest
from unittest.mock import patch
from src.data import DatasetManager


# Test Initialization
def test_initialization():
    with patch('src.data.dataset_manager.redis.Redis') as mock_redis:
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.exists.return_value = False

        _ = DatasetManager(rows=10, columns=5)
        assert mock_redis_instance.hmset.call_count == 5


# Test Get Dataset
@pytest.mark.asyncio
async def test_get_dataset():
    with patch('src.data.dataset_manager.redis.Redis') as mock_redis:
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.hget.return_value = '0.5'

        manager = DatasetManager(rows=10, columns=5)
        dataset = await manager.get_dataset(page=1, page_size=2)

        assert len(dataset) == 2
        assert dataset[0]['col_0'] == 0.5


# Test Apply Update Function
@pytest.mark.asyncio
async def test_apply_update_function():
    with patch('src.data.dataset_manager.redis.Redis') as mock_redis:
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.hgetall.return_value = {'0': '0.5', '1': '0.6'}
        mock_redis_instance.hmset.return_value = None

        manager = DatasetManager(rows=10, columns=5)
        await manager.apply_update_function('0')

        args, kwargs = mock_redis_instance.hmset.call_args
        assert args[0] == f"{manager.dataset_key}:col_0"
        updated_values = args[1]
        assert all(float(v) > 0.5 for v in updated_values.values())


# Test Non-Deterministic Function
@pytest.mark.asyncio
async def test_non_deterministic_function():
    result = await DatasetManager.non_deterministic_function(0.5)
    assert 0.5 <= result <= 1.5


# Test Redis Connection
def test_redis_connection():
    with patch('src.data.dataset_manager.redis.Redis') as mock_redis:
        mock_redis_instance = mock_redis.return_value

        manager = DatasetManager()
        assert manager.redis_client == mock_redis_instance
