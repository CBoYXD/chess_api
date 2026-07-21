from pydantic import BaseModel, field_validator

class Rating(BaseModel):
    on_win: int
    on_lose: int
    on_draw: int
    
    @field_validator("on_win", "on_lose", "on_draw", mode="before")
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        if not isinstance(v, float):
            raise ValueError("Field must be a float")
        return round(v)
