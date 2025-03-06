import React from 'react';
import { ToastContainer } from 'react-toastify';
import UploadForm from './components/uploadForm/UploadForm';
import './styles/App.css';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  return (
    <div className="app relative min-h-screen bg-black">
      <div className="relative z-10">
        <UploadForm />
      </div>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
    </div>
  );
}

export default App;