import React, { useState } from "react";
import "./UploadForm.css"; // Import CSS for styling

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalAudio, setOriginalAudio] = useState("");
  const [vocalsAudio, setVocalsAudio] = useState("");
  const [musicAudio, setMusicAudio] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Handle file selection & set preview
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);

    if (file) {
      const fileURL = URL.createObjectURL(file);
      setOriginalAudio(fileURL);
    }
  };

  // Handle form submission to upload and process the audio file
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setErrorMessage("Please select a file to upload.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setVocalsAudio("");
    setMusicAudio("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process file");
      }

      const data = await response.json();
      setVocalsAudio(`http://localhost:8000/download/${data.vocals_link}`);
      setMusicAudio(`http://localhost:8000/download/${data.music_link}`);
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Title */}
      <h1 className="title">Audio Magic</h1>

      {/* File Input Section */}
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="file-input-section">
          <label className="file-label">
            <input type="file" accept="audio/*" onChange={handleFileChange} />
          </label>

          {/* Play Original Audio */}
          {originalAudio && (
            <div className="audio-preview">
              <audio controls src={originalAudio}></audio>
            </div>
          )}
        </div>

        {/* Process Audio Button */}
        <button type="submit" className="process-button" disabled={isLoading}>
          {isLoading ? "Processing..." : "Process Audio"}
        </button>
      </form>

      {errorMessage && <p className="error-message">Error: {errorMessage}</p>}

      {/* Processed Audio Section */}
      <div className="processed-audio-section">
        {/* Play Processed Vocals */}
        {vocalsAudio && (
          <div className="audio-box">
            <h3>Vocals</h3>
            <audio controls src={vocalsAudio}></audio>
          </div>
        )}

        {/* Play Processed Music */}
        {musicAudio && (
          <div className="audio-box">
            <h3>Music</h3>
            <audio controls src={musicAudio}></audio>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;
