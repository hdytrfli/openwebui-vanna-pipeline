from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.responses import DataFrameResponse
from app.services.vanna_service import vanna
from app.api.dependencies import requires_cache
import io

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/download_csv")
async def download_csv(cache_data: dict = Depends(requires_cache(["df"]))):
    """Download query results as CSV file."""
    try:
        df = cache_data["df"]
        id = cache_data["id"]

        csv_data = df.to_csv()

        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={id}.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_training_data", response_model=DataFrameResponse)
async def get_training_data():
    """Get current training data."""
    try:
        df = vanna.get_training_data()
        return DataFrameResponse(
            id="training_data", df=df.head(25).to_json(orient="records")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
