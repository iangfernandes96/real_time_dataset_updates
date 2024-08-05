# type: ignore
import random
import numpy as np
import redis
from typing import Dict, List, Any
from src.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DATASET_KEY,
    DATASET_ROWS,
    DATASET_COLS
)


class DatasetManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, rows: int = DATASET_ROWS, columns: int = DATASET_COLS) -> None:  # noqa
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0,
                                        decode_responses=True)
        self.dataset_key = REDIS_DATASET_KEY

        for col in range(columns):
            col_key = f"{self.dataset_key}:col_{col}"
            if not self.redis_client.exists(col_key):
                col_data = np.random.rand(rows).round(2)
                col_dict = {str(i): str(col_data[i]) for i in range(rows)}
                self.redis_client.hmset(col_key, col_dict)
        print("Dataset initialization complete")

    async def get_dataset(self, page: int, page_size: int) -> List[Dict[Any, Any]]:  # noqa
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        dataset = []
        for row_idx in range(start_index, end_index):
            row = {}
            for col in range(DATASET_COLS):
                col_key = f"{self.dataset_key}:col_{col}"
                value = self.redis_client.hget(col_key, str(row_idx))
                row[f"col_{col}"] = float(value) if value is not None else None  # noqa
            dataset.append(row)
        return dataset

    async def apply_update_function(self, column: str) -> None:
        col_key = f"{self.dataset_key}:col_{column}"
        col_data = self.redis_client.hgetall(col_key)
        updated_col_data = {k: str(await self.non_deterministic_function(float(v)))  # noqa
                            for k, v in col_data.items()}
        self.redis_client.hmset(col_key, updated_col_data)

    @staticmethod
    async def non_deterministic_function(x: float) -> float:
        return round(x + random.random(), 2)

    async def extend_existing_dataset(self, rows: list[int], columns: list[int]):
        for col in range(DATASET_COLS):
            column_key = f"{self.dataset_key}:col_{col}"
            column_data = self.redis_client.hgetall(column_key)

            new_column_data = {str(DATASET_ROWS + i): str(i) for i in rows}
            column_data.update(new_column_data)
            self.redis_client.hmset(column_key, column_data)

        for i in range(DATASET_COLS, DATASET_COLS + len(columns)):
            column_key = f"{self.dataset_key}:col_{col}"
            new_column_data = {str(DATASET_ROWS + i): str(i) for i in rows}
            self.redis_client.hmset(column_key, column_data)
