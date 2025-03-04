from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from core.audio_processor import AudioProcessor
from versions.cat_version import CatVersion
from fastapi.responses import FileResponse
import os
import re
import subprocess
import yt_dlp
import shutil
import time
import uuid
from datetime import datetime, timedelta
import threading
import logging
import asyncio

router = APIRouter()

processor = AudioProcessor()
cat_processor = CatVersion()

TEMP_FILES = {}  # Store temp file paths with their creation time
CLEANUP_DELAY = 900  # Time in seconds to keep files ( 15 min)

def sanitize_filename(filename):
    """Sanitize filename to avoid issues with special characters."""
    return re.sub(r'[\\/*?:"<>|()&]', '_', filename)

def create_request_temp_folder():
    """Creates a unique temp folder for each request."""
    request_id = str(uuid.uuid4())
    temp_folder = f"temp/{request_id}"
    os.makedirs(temp_folder, exist_ok=True)
    return temp_folder

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

def cleanup_temp_folder(folder_path):
    """Cleanup temp folder after processing."""
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        
        # Clean up tracking dictionary
        paths_to_remove = [k for k, v in TEMP_FILES.items() if v['folder'] == folder_path]
        for path in paths_to_remove:
            TEMP_FILES.pop(path, None)

def schedule_cleanup(folder_path, delay=CLEANUP_DELAY):
    """Schedule folder cleanup after delay."""
    def delayed_cleanup():
        time.sleep(delay)
        cleanup_temp_folder(folder_path)

    cleanup_thread = threading.Thread(target=delayed_cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()

def track_temp_file(file_path, folder_path):
    """Track temporary file for cleanup."""
    normalized_path = os.path.normpath(file_path)
    TEMP_FILES[normalized_path] = {
        'created': datetime.now(),
        'folder': folder_path
    }
    logging.debug(f"Tracked file: {normalized_path}")

@router.post("/process")
async def process_file(
    file: UploadFile = File(None), 
    youtube_link: str = Form(None), 
    mode: str = Form(...)
):
    temp_folder = create_request_temp_folder()
    try:
        # 🔄 Handle file upload or YouTube download
        if youtube_link:
            video_path = await asyncio.to_thread(download_youtube_video, youtube_link, temp_folder)
            audio_path = await asyncio.to_thread(extract_audio, video_path, temp_folder)

            # Track the downloaded and extracted files
            track_temp_file(video_path, temp_folder)
            track_temp_file(audio_path, temp_folder)

        elif file:
            safe_filename = sanitize_filename(file.filename)
            file_path = os.path.join(temp_folder, safe_filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            audio_path = file_path
            track_temp_file(audio_path, temp_folder)
        else:
            raise HTTPException(status_code=400, detail="No file or YouTube link provided.")

        # 🎵 Process audio
        tracks = await asyncio.to_thread(processor.process_audio, audio_path, temp_folder)

        # Process based on mode and track all output files
        response = None
        if mode == "Vocal and Music":
            response = await handle_vocal_music_mode(tracks, youtube_link, video_path if youtube_link else None, audio_path, temp_folder)
        elif mode == "Cat Version":
            response = await asyncio.to_thread(handle_cat_version_mode, tracks, temp_folder)
            if os.path.exists(response["final_meow_music"]):
                track_temp_file(response["final_meow_music"], temp_folder)

        # Schedule cleanup
        schedule_cleanup(temp_folder)
        return response

    except HTTPException as http_err:
        if os.path.exists(temp_folder):
            cleanup_temp_folder(temp_folder)
        raise http_err
    except Exception as e:
        if os.path.exists(temp_folder):
            cleanup_temp_folder(temp_folder)
        raise HTTPException(status_code=500, detail=str(e))


async def merge_audio_with_video(audio_path, video_path, output_name, temp_folder):
    """Merges audio with video asynchronously."""
    output_path = os.path.join(temp_folder, output_name)
    command = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-map", "0:v:0", "-map", "1:a:0", 
        "-c:v", "copy", 
        "-c:a", "aac", 
        "-shortest", output_path
    ]
    await asyncio.to_thread(run_ffmpeg, command)
    validate_file_exists(output_path, "Merged video file is missing or empty.")
    return output_path

async def handle_vocal_music_mode(tracks, youtube_link, video_path, audio_path, temp_folder):
    """Handles Vocal and Music mode logic asynchronously."""
    if youtube_link:
        vocals_video, music_video = await asyncio.gather(
            asyncio.to_thread(merge_audio_with_video, tracks["vocals"], video_path, "vocals_video.mp4", temp_folder),
            asyncio.to_thread(merge_audio_with_video, tracks["accompaniment"], video_path, "music_video.mp4", temp_folder)
        )

        # Track all files that need to be downloadable, including the original video
        files_to_track = {
            "vocals_video": vocals_video,
            "music_video": music_video,
            "vocals_link": tracks["vocals"],
            "music_link": tracks["accompaniment"],
            "extracted_audio": audio_path,
            "original_video": video_path
        }

        # Track each file asynchronously
        await asyncio.gather(
            *[asyncio.to_thread(track_temp_file, path, temp_folder) for path in files_to_track.values() if isinstance(path, str) and os.path.exists(path)]
        )

        return files_to_track
    else:
        # Track the separated audio files
        for path in [tracks["vocals"], tracks["accompaniment"]]:
            if isinstance(path, str) and os.path.exists(path):
                track_temp_file(path, temp_folder)

        return {
            "vocals_link": tracks["vocals"],
            "music_link": tracks["accompaniment"]
        }
    
def handle_cat_version_mode(tracks, temp_folder):
    """Handles Cat Version mode logic."""
    meow_vocal_path = os.path.join(temp_folder, "meow_vocal_adjusted.wav")
    final_meow_music = os.path.join(temp_folder, "final_meow_music.wav")

    cat_processor.generate_meow_vocals(tracks["vocals"], meow_vocal_path)
    validate_file_exists(meow_vocal_path, "Meow vocal generation failed.")

    cat_processor.merge_meow_with_instrumental(tracks["accompaniment"], meow_vocal_path, final_meow_music)
    validate_file_exists(final_meow_music, "Final meow music generation failed.")

    return {"final_meow_music": final_meow_music}

@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    # Normalize path separators for comparison
    file_path = os.path.normpath(file_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found at path: {file_path}")
    
    # Check if file is in our tracking system
    if file_path not in TEMP_FILES:
        raise HTTPException(status_code=404, detail=f"File not found in tracking system or expired: {file_path}")
    
    return FileResponse(
        file_path,
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
    )

def download_youtube_video(youtube_url, temp_folder):
    """Downloads YouTube video and returns its path."""
    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'noplaylist': True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if not info:
                raise ValueError("Link doesn't exist")
            
            video_title = info['title'].split()[0]
            video_title = "".join(c for c in video_title if c.isalnum())
            timestamp = int(time.time())
            output_template = os.path.join(temp_folder, f"{video_title}_{timestamp}.%(ext)s")
            video_path = os.path.join(temp_folder, f"{video_title}_{timestamp}.mp4")
            
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': output_template,
                'merge_output_format': 'mp4',
                'noplaylist': True  # Ensure only the video is downloaded, not the playlist
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                ydl2.download([youtube_url])
            
            if not os.path.exists(video_path):
                print(f"Expected video at: {video_path}")
                print(f"Contents of temp folder: {os.listdir(temp_folder)}")
                raise ValueError(f"Download failed - video not found at {video_path}")
                
            return video_path
            
    except yt_dlp.utils.DownloadError as e:
        print(f"YouTube download error: {str(e)}")
        raise ValueError(f"Failed to download video: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in download_youtube_video: {str(e)}")
        raise ValueError(f"Download failed: {str(e)}")

def extract_audio(video_path, temp_folder):
    """Extracts audio from video using FFmpeg."""
    audio_output = os.path.join(temp_folder, f"{os.path.basename(video_path)}.wav")
    command = ["ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_output]
    run_ffmpeg(command)
    validate_file_exists(audio_output, "Extracted audio is missing or empty.")
    return audio_output

def merge_audio_with_video(audio_path, video_path, output_name, temp_folder):
    """Merges audio with video."""
    output_path = os.path.join(temp_folder, output_name)
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

def cleanup_expired_files():
    """Clean up expired temporary files."""
    current_time = datetime.now()
    expired_files = [
        (path, data) for path, data in TEMP_FILES.items()
        if (current_time - data['created']) > timedelta(seconds=CLEANUP_DELAY)
    ]
    
    for path, data in expired_files:
        if os.path.exists(data['folder']):
            shutil.rmtree(data['folder'])
        TEMP_FILES.pop(path, None)

@router.post("/cleanup")
async def force_cleanup():
    """Force cleanup of expired files."""
    cleanup_expired_files()
    return {"message": "Cleanup completed"}