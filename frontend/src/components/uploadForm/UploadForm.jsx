import React, { useState } from "react";
import "./UploadForm.css"; // Import CSS for styling

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [processingType, setProcessingType] = useState(""); // Dropdown selection
  const [originalAudio, setOriginalAudio] = useState("");
  const [vocalsAudio, setVocalsAudio] = useState("");
  const [musicAudio, setMusicAudio] = useState("");
  const [meowAudio, setMeowAudio] = useState(""); // For Cat Version
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

  // Handle dropdown selection
  const handleDropdownChange = (e) => {
    setProcessingType(e.target.value);
  };

  // Handle form submission to upload and process the audio file
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setErrorMessage("Please select a file to upload.");
      return;
    }

    if (!processingType) {
      setErrorMessage("Please select a processing type.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setVocalsAudio("");
    setMusicAudio("");
    setMeowAudio("");

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("mode", processingType); // Send dropdown selection to backend

    console.log("Submitting request with mode:", processingType); // Debugging log

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || JSON.stringify(errorData));
      }

      const data = await response.json();

      // Handle response based on mode selection
      if (processingType === "Cat Version") {
        setMeowAudio(`http://localhost:8000/download/${data.final_meow_music}`);
      } else {
        setVocalsAudio(`http://localhost:8000/download/${data.vocals_link}`);
        setMusicAudio(`http://localhost:8000/download/${data.music_link}`);
      }
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
              <h3>Original File</h3>
              <audio controls src={originalAudio}></audio>
            </div>
          )}
        </div>

        {/* Dropdown for Processing Type (Only shown after file upload) */}
        {selectedFile && (
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
        {processingType === "Vocal and Music" && vocalsAudio && musicAudio && (
          <>
            <div className="audio-box">
              <h3>Vocals</h3>
              <audio controls src={vocalsAudio}></audio>
            </div>

            <div className="audio-box">
              <h3>Music</h3>
              <audio controls src={musicAudio}></audio>
            </div>
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
