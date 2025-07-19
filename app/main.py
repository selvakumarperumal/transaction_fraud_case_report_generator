from app.api.endpoints.report import router as report_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(report_router)
@app.get("/")
async def root():
    return {"message": "Welcome to the Transaction Fraud Case Report Generator API"}
