from enum import Enum

from pydantic import BaseModel, UUID4, field_validator, model_validator, Field

from core.exceptions import ToManyPointsError


class CreatedTaskResponse(BaseModel):
    id: UUID4


class SinglePoint(BaseModel):
    lat: float | None = None
    lng: float | None = None

    @field_validator("lat", "lng", mode="before")
    @classmethod
    def validate_atts(cls, value: str, *args):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class Points(BaseModel):
    points: list[SinglePoint]

    @model_validator(mode="after")
    @classmethod
    def validate_points(cls, model):
        valid_points = []
        for point in model.points:
            if point.lat is not None and point.lng is not None:
                valid_points.append(point)
        model.points = valid_points
        if len(model.points) > 1000:
            raise ToManyPointsError("Слишком много точек (> 1000)")
        return model


class TaskDetailDTO(BaseModel):
    id: UUID4
    points: Points | None = None
    limit: int = Field(exclude=True)
    offset: int = Field(exclude=True)

    @model_validator(mode="after")
    @classmethod
    def validate_points(cls, model):
        if model.points is None:
            return model
        model.points.points = model.points.points[
            model.offset : model.offset + model.limit
        ]
        return model


class Status(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class AMQPMessage(BaseModel):
    id: UUID4
    points: Points
