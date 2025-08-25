from pydantic import BaseModel
from typing import Optional


class TrainingDataRequest(BaseModel):
    question: Optional[str] = None
    sql: Optional[str] = None
    ddl: Optional[str] = None
    documentation: Optional[str] = None


class RemoveTrainingDataRequest(BaseModel):
    id: str
