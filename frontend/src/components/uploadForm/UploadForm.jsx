import React, { useState } from "react";
import AudioPlayer from "./AudioPlayer";
import "./UploadForm.css";

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [youtubeLink, setYoutubeLink] = useState("");
  const [processingType, setProcessingType] = useState("");
  const [originalAudio, setOriginalAudio] = useState("");
  const [extractedAudio, setExtractedAudio] = useState("");
  const [originalVideo, setOriginalVideo] = useState("");
  const [vocalsAudio, setVocalsAudio] = useState("");
  const [musicAudio, setMusicAudio] = useState("");
  const [meowAudio, setMeowAudio] = useState("");
  const [vocalsVideo, setVocalsVideo] = useState("");
  const [musicVideo, setMusicVideo] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeTab, setActiveTab] = useState("Original");
  const [isProcessed, setIsProcessed] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setYoutubeLink("");

    if (file) {
      const fileURL = URL.createObjectURL(file);
      setOriginalAudio(fileURL);
    } else {
      setOriginalAudio("");
    }
  
    setProcessingType("");
    setErrorMessage("");
    resetProcessedData();
  };

  const handleYoutubeLinkChange = (e) => {
    const link = e.target.value;
    setYoutubeLink(link);
    setSelectedFile(null);
    setOriginalAudio("");
  
    setProcessingType("");
    setErrorMessage("");
    resetProcessedData();
  };
  

  const resetProcessedData = () => {
    setVocalsAudio("");
    setMusicAudio("");
    setMeowAudio("");
    setVocalsVideo("");
    setMusicVideo("");
    setExtractedAudio("");
    setOriginalVideo("");
    setIsProcessed(false);
    setActiveTab("Original");
  };

  const handleDropdownChange = (e) => {
    setProcessingType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile && !youtubeLink) {
      // setErrorMessage("Please select a file or enter a YouTube link.");
      return;
    }

    if (!processingType) {
      // setErrorMessage("Please select a processing type.");
      return;
    }

    if (youtubeLink && processingType !== "Vocal and Music") {
      setErrorMessage("Only 'Vocal and Music' is supported for YouTube links.");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setIsProcessed(false);
    resetProcessedData();

    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    } else {
      formData.append("youtube_link", youtubeLink);
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
        setExtractedAudio(`http://localhost:8000/download/${data.extracted_audio}`);
        setOriginalVideo(`http://localhost:8000/download/${data.original_video}`);
        setActiveTab("Original");
        setIsProcessed(true);
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
      <h1 className="title">Audio Magic</h1>

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

          {selectedFile && <p>Selected File: {selectedFile.name}</p>}

          {originalAudio && (
            <div className="audio-preview">
              <h3>Original File</h3>
              <AudioPlayer src={originalAudio} />
            </div>
          )}
        </div>

        {(selectedFile || youtubeLink) && (
          <div className="dropdown-section">
            <label>Choose Processing Type: </label>
            <select value={processingType} onChange={handleDropdownChange}>
              <option value="">-- Select Option --</option>
              <option value="Vocal and Music">Vocal and Music</option>
            </select>
          </div>
        )}

        <button
          type="submit"
          className="process-button"
          disabled={isLoading || !processingType || (!selectedFile && !youtubeLink)}
        >
          {isLoading ? "Processing..." : "Process"}
        </button>
      </form>

      {errorMessage && <p className="error-message">Error: {errorMessage}</p>}

      {isProcessed && youtubeLink && processingType === "Vocal and Music" && (
        <div className="tab-container">
          <button
            className={`tab-button ${activeTab === "Original" ? "active" : ""}`}
            onClick={() => setActiveTab("Original")}
          >
            Original
          </button>
          <button
            className={`tab-button ${activeTab === "Vocals" ? "active" : ""}`}
            onClick={() => setActiveTab("Vocals")}
          >
            Vocals
          </button>
          <button
            className={`tab-button ${activeTab === "Music" ? "active" : ""}`}
            onClick={() => setActiveTab("Music")}
          >
            Music
          </button>
        </div>
      )}

      <div className="processed-audio-section">
        {youtubeLink && processingType === "Vocal and Music" ? (
          <>
            {activeTab === "Original" && (originalVideo || extractedAudio) && (
              <div className="audio-box">
                <h3>🎬 Original</h3>
                {extractedAudio && (
                  <AudioPlayer src={extractedAudio} />
                )}
                {originalVideo && (
                  <video controls src={originalVideo}></video>
                )}
              </div>
            )}

            {activeTab === "Vocals" && (vocalsAudio || vocalsVideo) && (
              <div className="audio-box">
                <h3>🎤 Vocals</h3>
                <AudioPlayer src={vocalsAudio} />
                <video controls src={vocalsVideo}></video>
              </div>
            )}

            {activeTab === "Music" && (musicAudio || musicVideo) && (
              <div className="audio-box">
                <h3>🎵 Music</h3>
                <AudioPlayer src={musicAudio} />
                <video controls src={musicVideo}></video>
              </div>
            )}
          </>
        ) : (
          <>
            {vocalsAudio && (
              <div className="audio-box">
                <h3>🎤 Vocals</h3>
                <AudioPlayer src={vocalsAudio} />
              </div>
            )}

            {musicAudio && (
              <div className="audio-box">
                <h3>🎵 Music</h3>
                <AudioPlayer src={musicAudio} />
              </div>
            )}
          </>
        )}

        {processingType === "Cat Version" && meowAudio && (
          <div className="audio-box">
            <h3>🐱 Cat Version</h3>
            <AudioPlayer src={meowAudio} />
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;