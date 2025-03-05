import React from 'react';
import UploadForm from './components/uploadForm/UploadForm';
import './styles/App.css';

function App() {
  return (
    <div className="app relative min-h-screen bg-black">
      <div className="relative z-10">
        <UploadForm />
      </div>
    </div>
  );
}

export default App