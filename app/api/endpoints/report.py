from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import save_file, read_file
from app.services.langchain_service import analyze_transaction_history
from app.services.schemas import TransactionAnalysis
from app.api.endpoints.schemas import FileUploadResponse

router = APIRouter()

# Endpoint to upload transaction history file
@router.post("/upload-transaction-history", response_model=FileUploadResponse)
async def upload_transaction_history(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        filepath = await save_file(file)
        return FileUploadResponse(filepath=filepath, message="File uploaded successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to analyze transaction history
@router.post("/analyze-transaction-history", response_model=TransactionAnalysis)
async def analyze_transaction_history_endpoint(filepath: str):
    try:
        # Read the content of the file
        transaction_history = await read_file(filepath)
        
        # Analyze the transaction history using the LangChain service
        analysis_result = analyze_transaction_history(transaction_history)
        
        return analysis_result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))