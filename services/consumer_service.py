import numpy as np
from pyCombinatorial.algorithm import self_organizing_maps
from pyCombinatorial.utils import util
from pydantic import UUID4
from sqlalchemy import update

from core.dto import AMQPMessage, Points, Status, SOMParams, SinglePoint

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

    def _tsp_solver(self, points: Points) -> Points:
        route, coords = self._get_matrix(points)
        return self._get_result(route, coords)

    def _get_matrix(self, points: Points) -> np.array:
        coords = [[point.lat, point.lng] for point in points.points]
        np_array = np.array(coords)
        distance_matrix = util.build_distance_matrix(np_array)
        route, _ = self_organizing_maps(
            np_array, distance_matrix, **SOMParams().model_dump()
        )
        return route, coords

    def _get_result(self, route: list, coords: np.array) -> Points:
        """Получение правильно порядка, начиная с 1-ого элемента."""
        route = route[1:]
        first_index = route.index(1)
        result_map = route[first_index:] + route[:first_index]
        result = Points(
            points=[
                SinglePoint(
                    lat=coords[elem - 1][0],
                    lng=coords[elem - 1][1],
                )
                for elem in result_map
            ]
        )
        return result

    @staticmethod
    def _parse_message(message: bytes) -> AMQPMessage:
        return AMQPMessage.model_validate_json(message)
