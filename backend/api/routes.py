from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from core.audio_processor import AudioProcessor
from versions.cat_version import CatVersion
from fastapi.responses import FileResponse
import os
import re

router = APIRouter()

processor = AudioProcessor()
cat_processor = CatVersion()

def sanitize_filename(filename):
    """Sanitize filename to avoid issues with special characters."""
    return re.sub(r'[\\/*?:"<>|()&]', '_', filename)

@router.post("/process")
async def process_file(file: UploadFile = File(...), mode: str = Form(...)):
    try:
        safe_filename = sanitize_filename(file.filename)
        file_path = os.path.join("temp", safe_filename)

        os.makedirs("temp", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        tracks = processor.process_audio(file_path)

        if mode == "Vocal and Music":
            return {
                "vocals_link": tracks["vocals"],
                "music_link": tracks["accompaniment"]
            }
        elif mode == "Cat Version":
            meow_vocal_path = os.path.join("temp", "meow_vocal_adjusted.wav")
            final_meow_music = os.path.join("temp", "final_meow_music.wav")

            cat_processor.generate_meow_vocals(tracks["vocals"], meow_vocal_path)
            cat_processor.merge_meow_with_instrumental(tracks["accompaniment"], meow_vocal_path, final_meow_music)

            return {"final_meow_music": final_meow_music}
        else:
            raise HTTPException(status_code=400, detail="Invalid mode selected.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)