import React, { useState, useEffect, useCallback, useMemo } from "react";
import AudioPlayer from "./AudioPlayer";
import "./UploadForm.css";
import { toast } from 'react-toastify';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  // Memoize regex pattern
  const youtubeRegex = useMemo(() => /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/, []);

  // Fix the file URL creation and add cleanup
  useEffect(() => {
    let fileURL = '';
    if (selectedFile) {
      try {
        fileURL = URL.createObjectURL(selectedFile); // Fixed from 'file' to 'selectedFile'
        setOriginalAudio(fileURL);
      } catch (error) {
        console.error("Error creating object URL:", error);
        setErrorMessage("Error loading the selected file");
      }
    }
    
    return () => {
      if (fileURL) {
        URL.revokeObjectURL(fileURL);
      }
    };
  }, [selectedFile]);

  // Optimize file handling with useCallback
  const handleFileChange = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (e.g., 100MB limit)
      if (file.size > 100 * 1024 * 1024) {
        setErrorMessage("File size should be less than 100MB");
        return;
      }
      
      // Validate file type
      if (!file.type.startsWith('audio/')) {
        setErrorMessage("Please select a valid audio file");
        return;
      }
    }
    
    setSelectedFile(file || null);
    setYoutubeLink("");
    setProcessingType("");
    setErrorMessage("");
    resetProcessedData();
  }, []);

  // Optimize YouTube link validation
  const validateYoutubeLink = useCallback((link) => {
    if (!link) return false;
    return youtubeRegex.test(link);
  }, [youtubeRegex]);

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

  // Optimize form submission with error handling
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();

    if (!selectedFile && !youtubeLink) {
      toast.error("Please select a file or enter a YouTube link");
      return;
    }

    if (!processingType) {
      toast.error("Please select a processing type");
      return;
    }

    // Validate YouTube URL only when submitting
    if (youtubeLink && !youtubeRegex.test(youtubeLink)) {
      toast.error("Please enter a valid YouTube URL");
      return;
    }

    setErrorMessage("");
    setIsLoading(true);
    setIsProcessed(false);
    resetProcessedData();

    const formData = new FormData();
    try {
      if (selectedFile) {
        formData.append("file", selectedFile);
      } else {
        formData.append("youtube_link", youtubeLink);
      }
      formData.append("mode", processingType);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000); // 5 minutes timeout

      const response = await fetch(`${API_URL}/process`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Server error");
      }

      const data = await response.json();

      // Use try-catch for URL construction
      try {
        if (youtubeLink && processingType === "Vocal and Music") {
          setVocalsVideo(`${API_URL}/download/${data.vocals_video}`);
          setMusicVideo(`${API_URL}/download/${data.music_video}`);
          setVocalsAudio(`${API_URL}/download/${data.vocals_link}`);
          setMusicAudio(`${API_URL}/download/${data.music_link}`);
          setExtractedAudio(`${API_URL}/download/${data.extracted_audio}`);
          setOriginalVideo(`${API_URL}/download/${data.original_video}`);
          setActiveTab("Original");
          setIsProcessed(true);
        } else if (processingType === "Cat Version") {
          setMeowAudio(`${API_URL}/download/${data.final_meow_music}`);
        } else {
          setVocalsAudio(`${API_URL}/download/${data.vocals_link}`);
          setMusicAudio(`${API_URL}/download/${data.music_link}`);
        }
      } catch (error) {
        console.error("Error processing response data:", error);
        setErrorMessage("Error processing server response");
      }
    } catch (error) {
      console.error("Error:", error);
      if (error.name === 'AbortError') {
        toast.error("Request timed out. Please try again.");
      } else {
        toast.error(error.message || "An unexpected error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile, youtubeLink, processingType, API_URL, youtubeRegex]);

  // Clean up URLs on unmount
  useEffect(() => {
    return () => {
      [vocalsVideo, musicVideo, vocalsAudio, musicAudio, extractedAudio, originalVideo, meowAudio]
        .forEach(url => {
          if (url && url.startsWith('blob:')) {
            URL.revokeObjectURL(url);
          }
        });
    };
  }, [vocalsVideo, musicVideo, vocalsAudio, musicAudio, extractedAudio, originalVideo, meowAudio]);

  // Memoize the form rendering to prevent unnecessary re-renders
  const renderForm = useMemo(() => (
    <form onSubmit={handleSubmit} className="upload-form">
      <div className="file-input-section">
        <label className="file-label">
          <input 
            type="file" 
            accept="audio/*" 
            onChange={handleFileChange} 
            disabled={isLoading} 
          />
        </label>

        <span className="or-text">OR</span>

        <input
          type="text"
          placeholder="Paste YouTube link here"
          value={youtubeLink}
          onChange={handleYoutubeLinkChange}
          className="youtube-input"
          disabled={isLoading}
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
          <select 
            value={processingType} 
            onChange={handleDropdownChange} 
            disabled={isLoading}
            aria-label="Processing type selection"
          >
            <option value="">-- Select Option --</option>
            <option value="Vocal and Music">Vocal and Music</option>
            {/* Cat Version option hidden but functionality remains in code */}
          </select>
        </div>
      )}

      <button
        type="submit"
        className="process-button"
        disabled={isLoading || !processingType || (!selectedFile && !youtubeLink)}
        aria-busy={isLoading}
      >
        {isLoading ? "Processing..." : "Process"}
      </button>
    </form>
  ), [handleSubmit, isLoading, processingType, selectedFile, youtubeLink]);

  return (
    <div className="app-container">
      <h1 className="title">Audio Magic</h1>
      {renderForm}
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