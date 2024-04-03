from typing import Annotated

from fastapi import APIRouter, UploadFile, Depends
from fastapi import status
from pydantic import UUID4

from core.dto import CreatedTaskResponse, TaskDetailDTO
from services.task_service import TaskService

task_router = APIRouter()


@task_router.post(
    path="/routes",
    status_code=status.HTTP_201_CREATED,
    tags=["Создание задачи"],
    name="Создание задачи",
)
async def create_task(
    file: UploadFile,
    service: Annotated[TaskService, Depends()],
) -> CreatedTaskResponse:
    return await service.create_task(file)


@task_router.get(
    path="/routes/{id_}",
    tags=["Получить информацию о задаче"],
    name="Получение информации о задаче",
)
async def get_results(
    id_: UUID4,
    service: Annotated[TaskService, Depends()],
    limit: int = 100,
    offset: int = 0,
) -> TaskDetailDTO:
    return await service.get_results(id_, limit, offset)
