from fastapi import APIRouter, UploadFile, HTTPException, status
from core.file_processor import FileProcessor
from core.models import ProcessingResponse

router = APIRouter()
file_processor = FileProcessor()

@router.post("/upload", 
             response_model=ProcessingResponse,
             status_code=status.HTTP_202_ACCEPTED,
             summary="Upload floor plan file",
             description="Upload PDF or image file for processing")
async def upload_file(file: UploadFile):
    """
    Handle file upload and initiate processing
    
    Args:
        file (UploadFile): The floor plan file (PDF, JPG, or PNG)
        
    Returns:
        ProcessingResponse: Processing status and file information
        
    Raises:
        HTTPException: If file format is invalid or processing fails
    """
    # Validate file type
    valid_types = ["application/pdf", "image/jpeg", "image/png"]
    content_type = file.content_type or ""
    
    if not any(content_type.endswith(t.split('/')[-1]) for t in valid_types):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be PDF, JPG, or PNG"
        )
    
    try:
        # Process the file
        result = await file_processor.process_file(file)
        return ProcessingResponse(
            status="success",
            message="File uploaded successfully",
            file_info=result
        )
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )