import React, { useState, useEffect } from 'react';
import { MinimalMovementDetector } from './components/MinimalMovementDetector';
import { CameraTest } from './components/CameraTest';
import { WheelMode } from './components/WheelMode';

type Mode = 'movement' | 'camera' | 'wheel';

function MinimalApp() {
  const [mediaPipeReady, setMediaPipeReady] = useState(false);
  const [currentMode, setCurrentMode] = useState<Mode>('wheel'); // Default to wheel mode

  useEffect(() => {
    // Check if MediaPipe is loaded
    const checkInterval = setInterval(() => {
      if (window.Pose && window.drawConnectors) {
        setMediaPipeReady(true);
        clearInterval(checkInterval);
      }
    }, 100);

    return () => clearInterval(checkInterval);
  }, []);

  if (!mediaPipeReady) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: '#1a1a1a',
        color: '#fff'
      }}>
        Loading MediaPipe...
      </div>
    );
  }

  return (
    <div style={{ 
      backgroundColor: '#1a1a1a', 
      minHeight: '100vh',
      paddingTop: '50px'
    }}>
      <h1 style={{ 
        textAlign: 'center', 
        color: '#fff',
        marginBottom: '20px'
      }}>
        Movement Detection - {currentMode === 'wheel' ? 'Wheel Mode' : currentMode === 'camera' ? 'Camera Test' : 'Jump Detection'}
      </h1>
      
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button 
          onClick={() => setCurrentMode('wheel')}
          style={{
            padding: '10px 20px',
            backgroundColor: currentMode === 'wheel' ? '#666' : '#444',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            margin: '0 5px'
          }}
        >
          Wheel Mode
        </button>
        <button 
          onClick={() => setCurrentMode('movement')}
          style={{
            padding: '10px 20px',
            backgroundColor: currentMode === 'movement' ? '#666' : '#444',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            margin: '0 5px'
          }}
        >
          Jump Detection
        </button>
        <button 
          onClick={() => setCurrentMode('camera')}
          style={{
            padding: '10px 20px',
            backgroundColor: currentMode === 'camera' ? '#666' : '#444',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            margin: '0 5px'
          }}
        >
          Camera Test
        </button>
      </div>

      {currentMode === 'wheel' && <WheelMode />}
      {currentMode === 'movement' && <MinimalMovementDetector />}
      {currentMode === 'camera' && <CameraTest />}
    </div>
  );
}

export default MinimalApp; 