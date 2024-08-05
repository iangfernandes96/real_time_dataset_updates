from fastapi import APIRouter
from pydantic import BaseModel
from src.data import DatasetManager
from .utils import (operate_and_update, measure_latency)
from src.config import DATASET_COLS
from typing import List, Dict, Any
import asyncio


class UpdateRequest(BaseModel):
    column: int
    user_id: int


dataset_manager_router = APIRouter()
dataset_manager = DatasetManager()


@dataset_manager_router.get("/get_dataset")
@measure_latency
async def fetch_dataset(page: int = 1, page_size: int = 50) -> List[Dict[Any, Any]]: # noqa
    return await dataset_manager.get_dataset(page, page_size)


@dataset_manager_router.post("/update_column")
async def update_column(req: UpdateRequest) -> Dict[str, str]:
    column = req.column
    if not -1 < column < DATASET_COLS:
        return {"status": "Please provide a number between 0 and 9"}
    asyncio.create_task(operate_and_update(dataset_manager, str(column), req.user_id))   # noqa
    return {"status": "update started"}
