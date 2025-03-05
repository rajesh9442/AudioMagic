import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

export const SparklesCore = ({
  id,
  background,
  minSize,
  maxSize,
  speed,
  particleDensity,
  className,
  particleColor,
}) => {
  const particlesInit = useCallback(async (engine) => {
    await loadFull(engine);
  }, []);

  const particlesConfig = {
    background: {
      color: background,
    },
    fullScreen: false,
    particles: {
      color: {
        value: particleColor || "#ffffff",
      },
      move: {
        direction: "none",
        enable: true,
        outModes: {
          default: "bounce",
        },
        random: false,
        speed: speed || 2,
        straight: false,
      },
      number: {
        density: {
          enable: true,
          area: particleDensity || 800,
        },
        value: 80,
      },
      opacity: {
        value: 0.5,
      },
      shape: {
        type: "circle",
      },
      size: {
        value: { min: minSize || 1, max: maxSize || 3 },
      },
    },
    detectRetina: true,
  };

  return (
    <Particles
      id={id || "tsparticles"}
      init={particlesInit}
      options={particlesConfig}
      className={className}
    />
  );
};