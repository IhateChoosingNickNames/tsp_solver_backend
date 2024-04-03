import uuid

from fastapi import UploadFile
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from adapters.ampq import AmqpEngine
from core.dto import (
    TaskDetailDTO,
    CreatedTaskResponse,
    Points,
    Status,
    AMQPMessage,
)
from core.exceptions import IncorrectIdError
from core.utils import get_data_from_file
from db.engine import DatabaseEngine
from db.task import Task
from settings import (
    get_settings,
    DatabaseSettings,
    AppSettings,
    RabbitMqSettings,
)


class TaskService:

    def __init__(self):
        self.database = DatabaseEngine(
            db_url=str(get_settings(DatabaseSettings).url),
            debug=get_settings(AppSettings).debug,
        )

    async def create_task(
        self,
        file: UploadFile,
    ) -> CreatedTaskResponse:
        data = get_data_from_file(file)
        task = await self._create_task_db()
        broker = get_settings(RabbitMqSettings)
        print(data)
        message = AMQPMessage(
            id=task.id,
            points=data,
        )
        await AmqpEngine.publish(
            str(broker.url),
            broker.result_queue,
            message.model_dump_json(),
        )
        return CreatedTaskResponse(id=task.id)

    async def get_results(
        self,
        id_: UUID4,
        limit: int,
        offset: int,
    ) -> TaskDetailDTO:
        task = await self._get_results(id_)
        if task is None:
            raise IncorrectIdError("Такой задачи не существует.")
        if task.status != Status.COMPLETED:
            return TaskDetailDTO(
                id=task.id,
                limit=limit,
                offset=offset,
            )
        return TaskDetailDTO(
            id=task.id,
            points=Points.model_validate_json(task.points),
            limit=limit,
            offset=offset,
        )

    async def _create_task_db(self) -> CreatedTaskResponse:
        stmt = (
            insert(Task)
            .values(status=Status.PENDING, id=uuid.uuid4())
            .returning(Task)
        )
        return await self.database.save(stmt)

    async def _get_results(self, id_: UUID4) -> Task:
        stmt = select(Task).where(Task.id == id_)
        return await self.database.get_one(stmt)
