from pydantic import BaseModel, Field

# Define the model output schema
class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    filepath: str = Field(
        description="The path of the uploaded file."
    )
    message: str = Field(
        description="A message indicating the status of the upload."
    )