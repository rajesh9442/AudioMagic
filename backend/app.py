from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from core.audio_processor import AudioProcessor
import logging
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

print("Starting FastAPI with GPU support...")
app = FastAPI(debug=True)
processor = AudioProcessor()

BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEMUC_DIR = os.path.join(BASE_DIR, "separated")
os.makedirs(DEMUC_DIR, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_old_uploads(upload_dir: str, demucs_dir: str, max_files: int = 4):
    """
    Removes the oldest processed files if more than `max_files` exist.
    """
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    if len(files) > max_files:
        files.sort(key=lambda f: os.path.getctime(os.path.join(upload_dir, f)))
        num_to_delete = len(files) - max_files
        for i in range(num_to_delete):
            file_to_delete = files[i]
            file_path = os.path.join(upload_dir, file_to_delete)
            try:
                os.remove(file_path)
                base_name = os.path.splitext(file_to_delete)[0]
                corresponding_folder = os.path.join(demucs_dir, base_name)
                if os.path.exists(corresponding_folder):
                    shutil.rmtree(corresponding_folder)
                print(f"Deleted old file: {file_to_delete} and folder: {corresponding_folder}")
            except Exception as e:
                print(f"Error deleting {file_to_delete}: {e}")

@app.post("/process")
async def process_file(file: UploadFile = File(...), mode: str = Form(...)):
    """
    Processes the uploaded file based on the selected mode.
    - "Vocal and Music" → Returns normal vocals and music.
    - "Cat Version" → Converts vocals into meow sounds and merges them with instrumental.
    """
    try:
        logging.info(f"✅ Received file: {file.filename}")
        logging.info(f"✅ Processing mode received: {mode}")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        cleanup_old_uploads(UPLOAD_DIR, DEMUC_DIR, max_files=4)
        tracks = processor.process_audio(file_path)

        if mode == "Vocal and Music":
            return {
                "vocals_link": os.path.relpath(tracks["vocals"], BASE_DIR),
                "music_link": os.path.relpath(tracks["accompaniment"], BASE_DIR)
            }

        elif mode == "Cat Version":
            meow_vocal_path = os.path.join(UPLOAD_DIR, "meow_vocal_adjusted.wav")
            processor.generate_meow_vocals(tracks["vocals"], meow_vocal_path)

            final_meow_music = os.path.join(UPLOAD_DIR, "final_meow_music.wav")
            processor.merge_meow_with_instrumental(tracks["accompaniment"], meow_vocal_path, final_meow_music)

            return {"final_meow_music": os.path.relpath(final_meow_music, BASE_DIR)}

        else:
            logging.error(f"❌ Invalid mode received: {mode}")
            raise HTTPException(status_code=400, detail="Invalid mode selected.")

    except Exception as e:
        logging.error(f"❌ Error processing file: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    Downloads the processed audio file.
    """
    full_path = os.path.join(BASE_DIR, file_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)