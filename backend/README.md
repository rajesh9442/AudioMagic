# AudioMagic Backend Service

A FastAPI-based backend service for audio processing that separates vocals from music and creates cat versions of songs.

## Features

- 🎵 Vocal and Music Separation using Demucs
- 😺 Cat Version Generator (replaces vocals with meows)
- 🎥 YouTube Video Processing
- 🔄 File Upload Support
- 🧹 Automatic Temporary File Cleanup

## Prerequisites

- Python 3.10 or higher
- FFmpeg installed and available in system PATH
- CUDA-compatible GPU (optional, for faster processing)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AudioMagic/backend
```

2. Create and activate virtual environment:
```bash
python -m venv myenv
# Windows
myenv\Scripts\activate
# Linux/Mac
source myenv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg:
- Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Linux: `sudo apt-get install ffmpeg`
- Mac: `brew install ffmpeg`

## Project Structure

```
backend/
├── api/                    # API routes and controllers
├── core/                   # Core processing logic
│   ├── audio_processor.py  # Audio separation
│   └── utils.py           # Utility functions
├── data/                   # Static data files
│   └── cat/               # Cat sound samples
├── versions/              # Processing versions
│   └── cat_version.py    # Cat version generator
└── app.py                # Main FastAPI application
```

## API Endpoints

### POST /process
Process audio files or YouTube links.

**Parameters:**
- `file`: Audio/video file upload (optional)
- `youtube_link`: YouTube URL (optional)
- `mode`: Processing mode ("Vocal and Music" or "Cat Version")

**Response:**
```json
{
    "vocals_link": "path/to/vocals.mp3",
    "music_link": "path/to/accompaniment.mp3"
}
```

### GET /download/{file_path}
Download processed files.

### POST /cleanup
Force cleanup of temporary files.

## Environment Variables

Create a `.env` file with:
```
TEMP_FILE_CLEANUP_DELAY=900  # Cleanup delay in seconds
```

## Running the Server

Development:
```bash
uvicorn app:app --reload
```

Production:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
