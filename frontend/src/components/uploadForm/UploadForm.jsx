import React, { useState } from "react";
import "./UploadForm.css"; // Import CSS for styling

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [youtubeLink, setYoutubeLink] = useState(""); // YouTube link state
  const [processingType, setProcessingType] = useState("");
  const [originalAudio, setOriginalAudio] = useState("");
  const [vocalsAudio, setVocalsAudio] = useState("");
  const [musicAudio, setMusicAudio] = useState("");
  const [meowAudio, setMeowAudio] = useState("");
  const [vocalsVideo, setVocalsVideo] = useState(""); // New: Video with Vocals
  const [musicVideo, setMusicVideo] = useState(""); // New: Video with Music
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Handle file selection & set preview
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setYoutubeLink(""); // Clear YouTube link if file is selected

    if (file) {
      const fileURL = URL.createObjectURL(file);
      setOriginalAudio(fileURL);
    } else {
      setOriginalAudio("");
    }
  };

  // Handle YouTube link input
  const handleYoutubeLinkChange = (e) => {
    const link = e.target.value;
    setYoutubeLink(link);
    setSelectedFile(null); // Clear file if YouTube link is provided
    setOriginalAudio("");  // Clear original audio preview
  };

  // Handle dropdown selection
  const handleDropdownChange = (e) => {
    setProcessingType(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile && !youtubeLink) {
      setErrorMessage("Please select a file or enter a YouTube link.");
      return;
    }

    if (!processingType) {
      setErrorMessage("Please select a processing type.");
      return;
    }

    if (youtubeLink && processingType !== "Vocal and Music") {
      setErrorMessage("Only 'Vocal and Music' is supported for YouTube links.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setVocalsAudio("");
    setMusicAudio("");
    setMeowAudio("");
    setVocalsVideo("");
    setMusicVideo("");

    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    } else {
      formData.append("youtube_link", youtubeLink); // Send YouTube link to backend
    }
    formData.append("mode", processingType);

    console.log("Submitting request with mode:", processingType);

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.detail === "Link doesn't exist") {
          setErrorMessage("Link doesn't exist");
        } else {
          setErrorMessage("An error occurred. Please try again.");
        }
        return;
      }

      const data = await response.json();

      if (youtubeLink && processingType === "Vocal and Music") {
        setVocalsVideo(`http://localhost:8000/download/${data.vocals_video}`);
        setMusicVideo(`http://localhost:8000/download/${data.music_video}`);
        setVocalsAudio(`http://localhost:8000/download/${data.vocals_link}`);
        setMusicAudio(`http://localhost:8000/download/${data.music_link}`);
      } else if (processingType === "Cat Version") {
        setMeowAudio(`http://localhost:8000/download/${data.final_meow_music}`);
      } else {
        setVocalsAudio(`http://localhost:8000/download/${data.vocals_link}`);
        setMusicAudio(`http://localhost:8000/download/${data.music_link}`);
      }
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Title */}
      <h1 className="title">Audio Magic</h1>

      {/* File Input & YouTube Link Section */}
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-section">
          <label className="file-label">
            <input type="file" accept="audio/*" onChange={handleFileChange} />
          </label>

          <span className="or-text">OR</span>

          <input
            type="text"
            placeholder="Paste YouTube link here"
            value={youtubeLink}
            onChange={handleYoutubeLinkChange}
            className="youtube-input"
          />

          {/* Show selected file name if file is chosen */}
          {selectedFile && <p>Selected File: {selectedFile.name}</p>}

          {/* Play Original Audio */}
          {originalAudio && (
            <div className="audio-preview">
              <h3>Original File</h3>
              <audio controls src={originalAudio}></audio>
            </div>
          )}
        </div>

        {/* Dropdown for Processing Type */}
        {(selectedFile || youtubeLink) && (
          <div className="dropdown-section">
            <label>Choose Processing Type: </label>
            <select value={processingType} onChange={handleDropdownChange}>
              <option value="">-- Select Option --</option>
              <option value="Vocal and Music">Vocal and Music</option>
              <option value="Cat Version">Cat Version</option>
            </select>
          </div>
        )}

        {/* Process Audio Button */}
        <button type="submit" className="process-button" disabled={isLoading || !processingType}>
          {isLoading ? "Processing..." : "Process Audio"}
        </button>
      </form>

      {errorMessage && <p className="error-message">Error: {errorMessage}</p>}

      {/* Processed Audio Section */}
      <div className="processed-audio-section">
        {/* Play Processed Vocals & Music for "Vocal and Music" Mode */}
        {(processingType === "Vocal and Music") && (
          <>
            {/* Vocals Section */}
            {(vocalsAudio || vocalsVideo) && (
              <div className="audio-box">
                <h3>🎤 Vocals</h3>
                {vocalsAudio && (
                  <>
                    <audio controls src={vocalsAudio}></audio>
                  </>
                )}
                {vocalsVideo && (
                  <>
                    <video controls width="500" src={vocalsVideo}></video>
                  </>
                )}
              </div>
            )}

            {/* Music Section */}
            {(musicAudio || musicVideo) && (
              <div className="audio-box">
                <h3>🎵 Music</h3>
                {musicAudio && (
                  <>
                    <audio controls src={musicAudio}></audio>
                  </>
                )}
                {musicVideo && (
                  <>
                    <video controls width="500" src={musicVideo}></video>
                  </>
                )}
              </div>
            )}
          </>
        )}

        {/* Play Final Meow Version for "Cat Version" Mode */}
        {processingType === "Cat Version" && meowAudio && (
          <div className="audio-box">
            <h3>🐱 Cat Version</h3>
            <audio controls src={meowAudio}></audio>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;