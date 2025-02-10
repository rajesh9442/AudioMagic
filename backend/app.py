from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from core.audio_processor import AudioProcessor

app = FastAPI(debug=True)
processor = AudioProcessor()

BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    mode: str = Form("music")
):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        output_path = processor.process_audio(file_path, mode)
        relative_path = os.path.relpath(output_path, BASE_DIR)
        return {"download_link": relative_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    full_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)
