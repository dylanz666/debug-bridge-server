from pydantic import BaseModel


class Command(BaseModel):
    command: str
