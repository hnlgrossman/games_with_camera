import React, { useRef, useEffect, useState } from 'react';

export function CameraTest() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState('Initializing camera...');

  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 320, height: 240 } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setStatus('Camera working!');
        }
      } catch (err) {
        setStatus('Camera error: ' + (err as Error).message);
      }
    };

    initCamera();

    return () => {
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div style={{ textAlign: 'center', padding: '20px' }}>
      <h2 style={{ color: '#fff' }}>Camera Test</h2>
      <p style={{ color: '#ccc' }}>{status}</p>
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        style={{ 
          width: '320px', 
          height: '240px',
          border: '2px solid #555',
          backgroundColor: '#000'
        }}
      />
    </div>
  );
} 