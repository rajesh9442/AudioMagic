from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from core.audio_processor import AudioProcessor
from versions.cat_version import CatVersion
from fastapi.responses import FileResponse
import os
import re
import subprocess
import yt_dlp
import shutil

router = APIRouter()

processor = AudioProcessor()
cat_processor = CatVersion()

def sanitize_filename(filename):
    """Sanitize filename to avoid issues with special characters."""
    return re.sub(r'[\\/*?:"<>|()&]', '_', filename)

def clear_temp_folder():
    """Clears the temp folder before processing a new request."""
    temp_folder = "temp"
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

def run_ffmpeg(command):
    """Utility function to run FFmpeg commands and handle errors."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        raise Exception(f"FFmpeg failed: {result.stderr}")

def validate_file_exists(file_path, error_message):
    """Ensure that a file exists and is non-empty."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise Exception(error_message)

@router.post("/process")
async def process_file(
    file: UploadFile = File(None), 
    youtube_link: str = Form(None), 
    mode: str = Form(...)
):
    try:
        clear_temp_folder()

        os.makedirs("temp", exist_ok=True)

        # 🔄 Handle file upload or YouTube download
        if youtube_link:
            video_path = download_youtube_video(youtube_link)
            audio_path = extract_audio(video_path)
        elif file:
            safe_filename = sanitize_filename(file.filename)
            file_path = os.path.join("temp", safe_filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            audio_path = file_path
        else:
            raise HTTPException(status_code=400, detail="No file or YouTube link provided.")

        # 🎵 Process audio
        tracks = processor.process_audio(audio_path)

        if mode == "Vocal and Music":
            return handle_vocal_music_mode(tracks, youtube_link, video_path if youtube_link else None)
        
        elif mode == "Cat Version":
            return handle_cat_version_mode(tracks)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid mode selected.")

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_vocal_music_mode(tracks, youtube_link, video_path):
    """Handles Vocal and Music mode logic."""
    if youtube_link:
        vocals_video = merge_audio_with_video(tracks["vocals"], video_path, "vocals_video.mp4")
        music_video = merge_audio_with_video(tracks["accompaniment"], video_path, "music_video.mp4")
        return {
            "vocals_video": vocals_video,
            "music_video": music_video,
            "vocals_link": tracks["vocals"],
            "music_link": tracks["accompaniment"]
        }
    else:
        return {
            "vocals_link": tracks["vocals"],
            "music_link": tracks["accompaniment"]
        }

def handle_cat_version_mode(tracks):
    """Handles Cat Version mode logic."""
    meow_vocal_path = os.path.join("temp", "meow_vocal_adjusted.wav")
    final_meow_music = os.path.join("temp", "final_meow_music.wav")

    cat_processor.generate_meow_vocals(tracks["vocals"], meow_vocal_path)
    validate_file_exists(meow_vocal_path, "Meow vocal generation failed.")

    cat_processor.merge_meow_with_instrumental(tracks["accompaniment"], meow_vocal_path, final_meow_music)
    validate_file_exists(final_meow_music, "Final meow music generation failed.")

    return {"final_meow_music": final_meow_music}

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

def download_youtube_video(youtube_url):
    """Downloads YouTube video and returns its path."""
    output_template = "temp/youtube_video.%(ext)s"
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': output_template,
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            if not info:
                raise ValueError("Link doesn't exist")
            final_ext = info.get('ext', 'mp4')
            video_path = f"temp/youtube_video.{final_ext}"
    except yt_dlp.utils.DownloadError:
        raise ValueError("Link doesn't exist")
    except Exception:
        raise ValueError("Link doesn't exist")

    return video_path

def extract_audio(video_path):
    """Extracts audio from video using FFmpeg."""
    audio_output = "temp/extracted_audio.wav"
    command = ["ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_output]
    run_ffmpeg(command)
    validate_file_exists(audio_output, "Extracted audio is missing or empty.")
    return audio_output

def merge_audio_with_video(audio_path, video_path, output_name):
    """Merges audio with video."""
    output_path = f"temp/{output_name}"
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0", 
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-shortest", output_path
    ]
    run_ffmpeg(command)
    validate_file_exists(output_path, "Merged video file is missing or empty.")
    return output_path