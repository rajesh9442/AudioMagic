from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import time
from core.audio_processor import AudioProcessor
 
app = FastAPI(debug=True)
processor = AudioProcessor()
 
BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(UPLOAD_DIR, exist_ok=True)
 
SPLEETER_DIR = os.path.join(UPLOAD_DIR, "spleeter_output")
os.makedirs(SPLEETER_DIR, exist_ok=True)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
def cleanup_old_uploads(upload_dir: str, spleeter_dir: str, max_files: int = 4):
    """
    Checks the upload directory for files.
    If there are more than max_files, deletes the oldest file(s)
    and removes its corresponding folder in the spleeter_output directory.
    """
    # List only files in UPLOAD_DIR (ignore directories)
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    if len(files) > max_files:
        # Sort files by creation time (oldest first)
        files.sort(key=lambda f: os.path.getctime(os.path.join(upload_dir, f)))
        # Calculate number of files to delete
        num_to_delete = len(files) - max_files
        for i in range(num_to_delete):
            file_to_delete = files[i]
            file_path = os.path.join(upload_dir, file_to_delete)
            try:
                os.remove(file_path)
                # Remove corresponding folder in spleeter_output (if exists)
                base_name = os.path.splitext(file_to_delete)[0]
                corresponding_folder = os.path.join(spleeter_dir, base_name)
                if os.path.exists(corresponding_folder):
                    shutil.rmtree(corresponding_folder)
                print(f"Deleted old file: {file_to_delete} and folder: {corresponding_folder}")
            except Exception as e:
                print(f"Error deleting {file_to_delete}: {e}")
 
@app.post("/process")
async def process_file(
    file: UploadFile = File(...),
    mode: str = Form("music")
):
    try:
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
 
        # Clean up old uploads if more than 4 exist
        cleanup_old_uploads(UPLOAD_DIR, SPLEETER_DIR, max_files=4)
 
        # Process audio and get path to separated track
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