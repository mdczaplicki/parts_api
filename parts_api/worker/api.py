import uvicorn
from fastapi import FastAPI

from parts_api.category.router import CATEGORY_ROUTER
from parts_api.manufacturer.router import MANUFACTURER_ROUTER
from parts_api.model.router import MODEL_ROUTER
from parts_api.part.router import PART_ROUTER

app = FastAPI(
    title="Parts REST API",
)
app.include_router(MANUFACTURER_ROUTER, prefix="/manufacturers", tags=["Manufacturer"])
app.include_router(CATEGORY_ROUTER, prefix="/categories", tags=["Category"])
app.include_router(MODEL_ROUTER, prefix="/models", tags=["Model"])
app.include_router(PART_ROUTER, prefix="/parts", tags=["Part"])

if __name__ == "__main__":
    uvicorn.run("parts_api.worker.api:app", host="0.0.0.0", reload=True)
