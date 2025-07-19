import os
from fastapi import UploadFile
from app.core.config import Settings
import pandas as pd
from fastapi import UploadFile, HTTPException
from typing import Union, Any, Annotated

settings = Settings()
UPLOAD_DIRECTORY = settings.UPLOAD_DIRECTORY
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

async def save_file(file: UploadFile) -> str:
    """
    Save the uploaded file to the server's filesystem, only allowing CSV and TXT files.
    
    Args:
        file (UploadFile): The file to be saved.
    
    Returns:
        str: The path where the file is saved.
    """
    allowed_extensions = {"csv", "txt", "log"}
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only CSV and TXT files are allowed.")

    try:
        filepath = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        return filepath
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        await file.close()

# Define a function to read the file and return its content
async def read_file(filepath: str) -> Annotated[Union[pd.DataFrame, str], Any]:
    """
    Read the content of the file and return it as a DataFrame or string.
    
    Args:
        filepath (str): The path to the file.

    Returns:
        Annotated[Union[pd.DataFrame, str], Any]: The content of the file as a DataFrame or string.
    """
    file_extension = filepath.split(".")[-1].lower()

    if file_extension == "csv":
        return pd.read_csv(filepath).to_string()
    elif file_extension in {"txt", "log"}:
        with open(filepath, "r") as f:
            return f.read()
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Only CSV, TXT, and LOG files are allowed.")