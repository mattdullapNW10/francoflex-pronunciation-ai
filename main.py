"""FastAPI application for pronunciation analysis."""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import tempfile
import os
from speechace import (
    get_speechace_response,
    convert_speechace_to_custom_response,
    add_ai_feedback_to_response
)

app = FastAPI(
    title="Francoflex Pronunciation API",
    description="API for analyzing French pronunciation using SpeechAce and OpenAI",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/pronunciation_analysis")
async def pronunciation_analysis(
    audio_file: UploadFile = File(..., description="Audio file (WAV, MP3, etc.)"),
    target_text: str = Form(..., description="Target text to analyze pronunciation against"),
    lv1: Optional[str] = Form(None, description="Optional level 1 parameter"),
    lv2: Optional[str] = Form(None, description="Optional level 2 parameter"),
    user_id: Optional[str] = Form(None, description="Optional user ID")
):
    """
    Analyze pronunciation from an uploaded audio file.
    
    Args:
        audio_file: The audio file containing user pronunciation
        target_text: The target text to compare against
        lv1: Optional level 1 parameter
        lv2: Optional level 2 parameter  
        user_id: Optional user ID for tracking
    
    Returns:
        JSON response with pronunciation analysis including:
        - overall_score: Overall pronunciation score (0-100)
        - cefr_score: CEFR level assessment
        - word_analysis: Detailed word-by-word analysis
        - ai_feedback: AI-powered feedback for each word
    """
    try:
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}") as temp_file:
            # Read and save the uploaded file
            audio_content = await audio_file.read()
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            # Open the audio file and call SpeechAce API
            with open(temp_file_path, "rb") as audio_file_obj:
                raw_response = get_speechace_response(audio_file_obj, target_text)
            
            # Convert to custom format
            custom_response = convert_speechace_to_custom_response(raw_response)
            
            # Add AI feedback
            response_with_feedback = add_ai_feedback_to_response(custom_response)
            
            # Add metadata
            response_with_feedback['metadata']['user_id'] = user_id
            response_with_feedback['metadata']['target_text'] = target_text
            response_with_feedback['metadata']['lv1'] = lv1
            response_with_feedback['metadata']['lv2'] = lv2
            
            return JSONResponse(content=response_with_feedback)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=f"Audio file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing pronunciation analysis: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Francoflex Pronunciation API",
        "version": "1.0.0",
        "endpoints": {
            "pronunciation_analysis": "/pronunciation_analysis"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

