from pydantic import UUID4
from sqlalchemy import update

from core.dto import AMQPMessage, Points, Status

from db.engine import DatabaseEngine
from db.task import Task
from settings import get_settings, DatabaseSettings, AppSettings


class ConsumerService:

    def __init__(self):
        self.database = DatabaseEngine(
            db_url=str(get_settings(DatabaseSettings).url),
            debug=get_settings(AppSettings).debug,
        )

    async def proceed_message(self, message: bytes):
        parsed_message = self._parse_message(message)
        sorted_message = self._tsp_solver(parsed_message.points)
        await self._update_task_results_db(parsed_message.id, sorted_message)

    async def _update_task_results_db(
        self, id_: UUID4, points: Points
    ) -> Task:
        stmt = (
            update(Task)
            .where(Task.id == id_)
            .values(status=Status.COMPLETED, points=points.model_dump_json())
            .returning(Task)
        )
        return await self.database.save(stmt)

    @staticmethod
    def _tsp_solver(points: Points) -> Points:
        # TODO написать основную логику
        # TODO изменить ограничение на размер в ДТО
        # TODO изменить размер в ридми
        return points

    @staticmethod
    def _parse_message(message: bytes) -> AMQPMessage:
        return AMQPMessage.model_validate_json(message)
