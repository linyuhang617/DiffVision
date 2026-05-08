from pydantic import BaseModel


class DiffRegion(BaseModel):
    x: int
    y: int
    w: int
    h: int
    area: int
    severity: str
