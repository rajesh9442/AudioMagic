import React, { useState, useRef, useEffect } from "react";
import { FaPlay, FaPause, FaVolumeUp, FaVolumeMute } from "react-icons/fa";

const AudioPlayer = ({ src }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  // Function to update duration when metadata loads
  const handleLoadedMetadata = () => {
    if (audioRef.current.duration) {
      setDuration(audioRef.current.duration);
    }
  };

  // Function to update current time
  const handleTimeUpdate = () => {
    if (audioRef.current.currentTime) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.addEventListener("loadedmetadata", handleLoadedMetadata);
      audio.addEventListener("timeupdate", handleTimeUpdate);
    }

    return () => {
      if (audio) {
        audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
        audio.removeEventListener("timeupdate", handleTimeUpdate);
      }
    };
  }, []);

  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      const handleCanPlay = () => setIsLoading(false);
      audio.addEventListener('canplay', handleCanPlay);
      return () => audio.removeEventListener('canplay', handleCanPlay);
    }
  }, []);

  // Reset player when src changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.load(); // Reload audio
      setIsPlaying(false);
      setCurrentTime(0);
      setDuration(0);
    }
  }, [src]);

  const togglePlay = () => {
    if (!src) return; // Prevent playing if no source
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch((err) => console.error("Error playing audio:", err));
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeSliderChange = (e) => {
    if (!duration) return;
    const time = (e.nativeEvent.offsetX / progressRef.current.offsetWidth) * duration;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioRef.current.volume = newVolume;
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (isMuted) {
      audioRef.current.volume = volume;
      setIsMuted(false);
    } else {
      audioRef.current.volume = 0;
      setIsMuted(true);
    }
  };

  const formatTime = (time) => {
    if (isNaN(time) || time === Infinity) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  return (
    <div className="audio-player">
      {src ? (
        <>
          <audio ref={audioRef} src={src} />

          <div className="audio-controls">
            <button className="play-pause-btn" onClick={togglePlay}>
              {isPlaying ? <FaPause /> : <FaPlay />}
            </button>

            <span className="time-display">{formatTime(currentTime)}</span>

            <div className="time-slider" ref={progressRef} onClick={handleTimeSliderChange}>
              <div className="time-slider-inner" style={{ width: `${(currentTime / duration) * 100}%` }} />
            </div>

            <span className="time-display">{formatTime(duration)}</span>

            <div className="volume-control">
              <button className="volume-btn" onClick={toggleMute}>
                {isMuted ? <FaVolumeMute /> : <FaVolumeUp />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="volume-slider"
              />
            </div>
          </div>
        </>
      ) : (
        <p className="error-message">No audio file selected.</p>
      )}
    </div>
  );
};

export default AudioPlayer;