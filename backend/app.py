# File: app.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from core.audio_processor import AudioProcessor

app = FastAPI()
processor = AudioProcessor()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary storage
UPLOAD_DIR = "temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    mode: str = "music_only"  # Options: "music_only", "cat_sound"
):
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Process audio
        output_filename = processor.process_audio(file_path, mode)
        return {"download_link": output_filename}

    except Exception as e:
        print(f"[BACKEND ERROR] {str(e)}")  # Log detailed error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename:path}")
async def download_file(filename: str):
    file_path = os.path.join("temp", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)