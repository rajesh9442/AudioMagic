import React, { useState } from "react";

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [mode, setMode] = useState("music"); // default mode is "music"
  const [downloadLink, setDownloadLink] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // Handle file selection
  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  // Handle mode selection using a dropdown
  const handleModeChange = (e) => {
    setMode(e.target.value);
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
    setDownloadLink("");

    // Create FormData and append file and selected mode
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("mode", mode);

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
      // Construct the full download URL (adjust the port/hostname if needed)
      setDownloadLink(`http://localhost:8000/download/${data.download_link}`);
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Audio Magic</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Choose Audio File:&nbsp;
            <input type="file" accept="audio/*" onChange={handleFileChange} />
          </label>
        </div>
        <div style={{ marginTop: "1em" }}>
          <label htmlFor="mode-select">Select Processing Mode:&nbsp;</label>
          <select id="mode-select" value={mode} onChange={handleModeChange}>
            <option value="music">Music</option>
            <option value="vocals">Vocal</option>
          </select>
        </div>
        <div style={{ marginTop: "1em" }}>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Processing..." : "Process Audio"}
          </button>
        </div>
      </form>

      {errorMessage && <p style={{ color: "red" }}>Error: {errorMessage}</p>}

      {downloadLink && (
        <div style={{ marginTop: "1em" }}>
          <p>Processing complete! Download your file below:</p>
          <a href={downloadLink} download>
            Download Processed Audio
          </a>
        </div>
      )}
    </div>
  );
};

export default UploadForm;
