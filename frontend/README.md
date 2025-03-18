# Audio Magic Frontend

Audio Magic is a web application that allows users to process audio files and YouTube videos by separating vocals from music or converting them into unique audio experiences.

## Features

- Audio file upload and processing
- YouTube video link processing 
- Separate vocals from music
- Real-time audio playback with waveform visualization
- Responsive design for desktop and mobile devices
- Video preview for YouTube processing

## Tech Stack

- React 18
- Vite
- TailwindCSS
- WaveSurfer.js
- React Icons
- React Toastify

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn

## Setup

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:
```bash
npm install
```
4. Create a `.env` file in the root directory:
```
VITE_API_URL=http://localhost:8000
```

## Development

To start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Build

To create a production build:

```bash
npm run build
```

## Usage

1. Upload an audio file or paste a YouTube link
2. Select the processing type:
   - Vocal and Music: Separates the audio into vocals and instrumental tracks
3. Click "Process" to start the conversion
4. Once processing is complete, you can:
   - Play/pause the audio
   - Adjust volume
   - View waveform visualization
   - Download processed tracks

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── uploadForm/
│   │       ├── AudioPlayer.jsx
│   │       ├── UploadForm.css
│   │       └── UploadForm.jsx
│   ├── styles/
│   │   └── App.css
│   ├── App.jsx
│   └── main.jsx
├── public/
├── .env
└── package.json
```

## License

This project is licensed under the MIT License.
