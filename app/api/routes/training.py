from fastapi import APIRouter, HTTPException
from app.services.vanna_service import vanna
from app.models.requests import TrainingDataRequest, RemoveTrainingDataRequest
from app.models.responses import TrainingDataResponse, SuccessResponse

router = APIRouter(prefix="/api", tags=["training"])


@router.post("/train", response_model=TrainingDataResponse)
async def add_training_data(request: TrainingDataRequest):
    """Add new training data to improve model performance."""
    try:
        id = vanna.train(
            question=request.question,
            sql=request.sql,
            ddl=request.ddl,
            documentation=request.documentation,
        )
        return TrainingDataResponse(id=id)
    except Exception as e:
        print("TRAINING ERROR", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove_training_data", response_model=SuccessResponse)
async def remove_training_data(request: RemoveTrainingDataRequest):
    """Remove training data by ID."""
    try:
        if vanna.remove_training_data(id=request.id):
            return SuccessResponse(success=True)
        else:
            raise HTTPException(status_code=400, detail="Couldn't remove training data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
