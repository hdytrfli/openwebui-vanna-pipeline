import os
import uuid
from app.config import settings
from urllib.parse import urljoin
from app.services.vanna_service import vanna
from app.services.cache_service import get_cache
from app.api.dependencies import requires_cache
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.responses import (
    SQLResponse,
    DataFrameResponse,
    PlotlyFigureResponse,
    QuestionCacheResponse,
)

router = APIRouter(prefix="/api", tags=["sql"])


@router.get("/generate_sql", response_model=SQLResponse)
async def generate_sql(
    question: str = Query(..., description="Question to generate SQL for")
):
    """Generate SQL query from natural language question."""
    try:
        cache = get_cache()
        id = cache.generate_id()
        sql = vanna.generate_sql(question=question, allow_llm_to_see_data=True)

        cache.set(id=id, field="question", value=question)
        cache.set(id=id, field="sql", value=sql)

        return SQLResponse(id=id, text=sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/run_sql", response_model=DataFrameResponse)
async def run_sql(cache_data: dict = Depends(requires_cache(["sql"]))):
    """Execute SQL query and return results."""
    try:
        cache = get_cache()
        sql = cache_data["sql"]
        id = cache_data["id"]

        df = vanna.run_sql(sql=sql)
        cache.set(id=id, field="df", value=df)
        df_markdown = df.to_markdown(index=False)

        return DataFrameResponse(
            id=id,
            df=df.head(10).to_json(orient="records"),
            df_markdown=df_markdown,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate_plotly_figure", response_model=PlotlyFigureResponse)
async def generate_plotly_figure(
    cache_data: dict = Depends(requires_cache(["df", "question", "sql"]))
) -> PlotlyFigureResponse:
    """
    Generate Plotly visualization from query results, save as static HTML,
    and return the URL to the static asset.
    """
    try:
        cache = get_cache()
        df = cache_data["df"]
        id = cache_data["id"]
        sql = cache_data["sql"]
        question = cache_data["question"]

        code = vanna.generate_plotly_code(
            question=question,
            sql=sql,
            df_metadata="Running df.dtypes gives:\n %s" % df.dtypes,
        )

        fig = vanna.get_plotly_figure(plotly_code=code, df=df, dark_mode=False)
        fig_json = fig.to_json()

        os.makedirs(settings.static_folder, exist_ok=True)

        unique_chart_id = str(uuid.uuid4())
        chart_filename = "vanna_chart_%s.jpg" % unique_chart_id
        chart_file_path = os.path.join(settings.static_folder, chart_filename)

        fig.write_image(
            chart_file_path,
            format="jpg",
            width=1200,
            height=800,
            scale=2,
        )

        chart_url = urljoin(settings.app_url, chart_file_path.replace("\\", "/"))
        cache.set(id=id, field="fig_json", value=fig_json)
        cache.set(id=id, field="chart_url", value=chart_url)

        return PlotlyFigureResponse(id=id, chart_url=chart_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/load_question", response_model=QuestionCacheResponse)
async def load_question(
    cache_data: dict = Depends(
        requires_cache(["question", "sql", "df", "fig_json", "followup_questions"])
    )
):
    """Load complete question data from cache."""
    try:
        return QuestionCacheResponse(
            id=cache_data["id"],
            question=cache_data["question"],
            sql=cache_data["sql"],
            df=cache_data["df"].head(10).to_json(orient="records"),
            fig=cache_data["fig_json"],
            followup_questions=cache_data["followup_questions"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
