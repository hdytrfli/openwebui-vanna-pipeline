from fastapi import HTTPException, Query, Depends
from typing import List
from app.services.cache_service import get_cache


def requires_cache(fields: List[str]):
    """Dependency to check if required fields exist in cache."""

    def dependency(id: str = Query(..., description="Cache ID")):
        cache = get_cache()

        if not id:
            raise HTTPException(status_code=400, detail="No id provided")

        for field in fields:
            if cache.get(id=id, field=field) is None:
                raise HTTPException(status_code=400, detail=f"No {field} found")

        field_values = {field: cache.get(id=id, field=field) for field in fields}
        field_values["id"] = id

        return field_values

    return dependency
