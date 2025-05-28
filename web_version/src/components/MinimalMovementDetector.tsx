import React, { useRef, useEffect, useState } from 'react';

declare global {
  interface Window {
    Pose: any;
    Camera: any;
    drawConnectors: any;
    drawLandmarks: any;
    POSE_CONNECTIONS: any;
  }
}

export function MinimalMovementDetector() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState('Initializing...');
  const poseRef = useRef<any>(null);
  const lastJumpTime = useRef(0);

  useEffect(() => {
    let animationId: number;

    const init = async () => {
      try {
        // Get camera
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { width: 320, height: 240 } 
        });
        
        if (!videoRef.current) return;
        videoRef.current.srcObject = stream;

        // Wait for video to be ready
        await new Promise<void>((resolve) => {
          if (videoRef.current) {
            videoRef.current.onloadedmetadata = () => {
              videoRef.current!.play();
              resolve();
            };
          }
        });

        // Initialize pose with minimal settings
        const pose = new window.Pose({
          locateFile: (file: string) => 
            `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });

        pose.setOptions({
          modelComplexity: 0, // Lowest complexity
          smoothLandmarks: false,
          enableSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        let previousNoseY = 0;
        let frameCount = 0;

        pose.onResults((results: any) => {
          if (!canvasRef.current) return;
          const ctx = canvasRef.current.getContext('2d');
          if (!ctx) return;

          frameCount++;
          
          // Clear and draw video
          ctx.clearRect(0, 0, 320, 240);
          
          // Draw the image from results, not from video element
          if (results.image) {
            ctx.drawImage(results.image, 0, 0, 320, 240);
          }

          if (results.poseLandmarks) {
            // Simple jump detection - just check nose movement
            const nose = results.poseLandmarks[0];
            const currentTime = Date.now();
            
            if (previousNoseY > 0) {
              const movement = previousNoseY - nose.y;
              
              // Simple jump detection
              if (movement > 0.05 && currentTime - lastJumpTime.current > 1000) {
                setStatus('JUMP!');
                lastJumpTime.current = currentTime;
                setTimeout(() => setStatus('Ready'), 500);
              }
            }
            
            previousNoseY = nose.y;

            // Draw minimal skeleton
            window.drawConnectors(ctx, results.poseLandmarks, window.POSE_CONNECTIONS, {
              color: '#00FF00',
              lineWidth: 2,
            });
          }
          
          // Update status to show it's working
          if (frameCount === 1) {
            setStatus('Ready');
          }
        });

        poseRef.current = pose;

        // Process frames using requestAnimationFrame
        const processFrame = async () => {
          if (videoRef.current && poseRef.current && videoRef.current.readyState === 4) {
            await poseRef.current.send({ image: videoRef.current });
          }
          animationId = requestAnimationFrame(processFrame);
        };

        // Start processing
        processFrame();

      } catch (err) {
        console.error('Initialization error:', err);
        setStatus('Error: ' + (err as Error).message);
      }
    };

    init();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (poseRef.current) {
        try {
          poseRef.current.close();
        } catch (e) {
          console.warn('Error closing pose:', e);
        }
      }
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div style={{ 
      position: 'relative', 
      width: '320px', 
      height: '240px',
      margin: '20px auto',
      backgroundColor: '#333',
      border: '2px solid #555'
    }}>
      <video
        ref={videoRef}
        style={{ display: 'none' }}
        autoPlay
        muted
        playsInline
        width={320}
        height={240}
      />
      <canvas
        ref={canvasRef}
        width={320}
        height={240}
        style={{ display: 'block' }}
      />
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        color: '#00FF00',
        fontSize: '20px',
        fontWeight: 'bold',
        textShadow: '2px 2px 4px rgba(0,0,0,0.8)'
      }}>
        {status}
      </div>
    </div>
  );
} 