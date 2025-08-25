from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ErrorResponse(BaseModel):
    type: str = "error"
    error: str


class QuestionListResponse(BaseModel):
    type: str = "question_list"
    questions: List[str]
    header: str
    id: Optional[str] = None


class SQLResponse(BaseModel):
    type: str = "sql"
    id: str
    text: str


class DataFrameResponse(BaseModel):
    type: str = "df"
    id: str
    df: str  # JSON string
    df_markdown: str


class PlotlyFigureResponse(BaseModel):
    type: str = "plotly_figure"
    id: str
    chart_url: str


class TrainingDataResponse(BaseModel):
    id: str


class SuccessResponse(BaseModel):
    success: bool


class QuestionCacheResponse(BaseModel):
    type: str = "question_cache"
    id: str
    question: str
    sql: str
    df: str  # JSON string
    fig: str  # JSON string
    followup_questions: List[str]


class QuestionHistoryResponse(BaseModel):
    type: str = "question_history"
    questions: List[Dict[str, Any]]
