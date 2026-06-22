from pydantic import BaseModel
from pydantic import PositiveInt


class Id(BaseModel):
    id: PositiveInt
