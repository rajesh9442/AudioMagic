import React from 'react';
import UploadForm from './components/uploadForm/UploadForm';
import { SparklesCore } from './components/ui/sparkles';
import './styles/App.css';

function App() {
  return (
    <div className="app relative min-h-screen bg-black">
      <div className="absolute inset-0 w-full h-full">
        <SparklesCore
          id="tsparticlesfullpage"
          background="transparent"
          minSize={0.6}
          maxSize={1.4}
          particleDensity={100}
          className="w-full h-full"
          particleColor="#FFFFFF"
          speed={1}
        />
      </div>
      <div className="relative z-10">
        <UploadForm />
      </div>
    </div>
  );
}

export default App