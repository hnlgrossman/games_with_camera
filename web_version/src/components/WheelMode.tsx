import React, { useRef, useEffect, useState } from 'react';

declare global {
  interface Window {
    Pose: any;
    drawConnectors: any;
    drawLandmarks: any;
    POSE_CONNECTIONS: any;
  }
}

interface WheelSection {
  id: string;
  angle: number;
  color: string;
  label: string;
}

export function WheelMode() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState('Initializing...');
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const poseRef = useRef<any>(null);
  const lastMovementTime = useRef(0);

  // Define wheel sections (angles in degrees, 0 is right, counter-clockwise)
  const sections: WheelSection[] = [
    { id: 'up', angle: -90, color: '#4CAF50', label: 'UP' },
    { id: 'right', angle: 0, color: '#2196F3', label: 'RIGHT' },
    { id: 'down', angle: 90, color: '#FF9800', label: 'DOWN' },
    { id: 'left', angle: 180, color: '#9C27B0', label: 'LEFT' },
  ];

  const drawWheel = (ctx: CanvasRenderingContext2D) => {
    const centerX = 320 / 2;
    const centerY = 240 / 2;
    const radius = 80;

    // Draw wheel sections
    sections.forEach((section, index) => {
      const startAngle = (section.angle - 45) * Math.PI / 180;
      const endAngle = (section.angle + 45) * Math.PI / 180;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.closePath();
      
      ctx.fillStyle = selectedSection === section.id 
        ? section.color 
        : section.color + '40'; // Add transparency when not selected
      ctx.fill();
      
      // Draw section label
      const labelAngle = section.angle * Math.PI / 180;
      const labelX = centerX + Math.cos(labelAngle) * (radius * 0.6);
      const labelY = centerY + Math.sin(labelAngle) * (radius * 0.6);
      
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 16px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(section.label, labelX, labelY);
    });

    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
    ctx.fillStyle = '#333';
    ctx.fill();
  };

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
          modelComplexity: 0,
          smoothLandmarks: false,
          enableSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        let previousNosePos = { x: 0, y: 0 };
        let frameCount = 0;

        pose.onResults((results: any) => {
          if (!canvasRef.current) return;
          const ctx = canvasRef.current.getContext('2d');
          if (!ctx) return;

          frameCount++;
          
          // Clear and draw video
          ctx.clearRect(0, 0, 320, 240);
          
          if (results.image) {
            ctx.drawImage(results.image, 0, 0, 320, 240);
          }

          // Draw wheel overlay
          ctx.save();
          ctx.globalAlpha = 0.7;
          drawWheel(ctx);
          ctx.restore();

          if (results.poseLandmarks) {
            const nose = results.poseLandmarks[0];
            const currentTime = Date.now();
            
            // Calculate movement direction
            if (previousNosePos.x > 0 && currentTime - lastMovementTime.current > 500) {
              const deltaX = nose.x - previousNosePos.x;
              const deltaY = nose.y - previousNosePos.y;
              const threshold = 0.03;

              let detectedMovement = null;

              if (Math.abs(deltaY) > Math.abs(deltaX)) {
                if (deltaY < -threshold) {
                  detectedMovement = 'up';
                  setStatus('UP!');
                } else if (deltaY > threshold) {
                  detectedMovement = 'down';
                  setStatus('DOWN!');
                }
              } else {
                if (deltaX < -threshold) {
                  detectedMovement = 'left';
                  setStatus('LEFT!');
                } else if (deltaX > threshold) {
                  detectedMovement = 'right';
                  setStatus('RIGHT!');
                }
              }

              if (detectedMovement) {
                setSelectedSection(detectedMovement);
                lastMovementTime.current = currentTime;
                setTimeout(() => {
                  setStatus('Ready');
                  setSelectedSection(null);
                }, 1000);
              }
            }
            
            previousNosePos = { x: nose.x, y: nose.y };

            // Draw minimal skeleton
            window.drawConnectors(ctx, results.poseLandmarks, window.POSE_CONNECTIONS, {
              color: '#00FF00',
              lineWidth: 2,
            });
          }
          
          if (frameCount === 1) {
            setStatus('Ready');
          }
        });

        poseRef.current = pose;

        const processFrame = async () => {
          if (videoRef.current && poseRef.current && videoRef.current.readyState === 4) {
            await poseRef.current.send({ image: videoRef.current });
          }
          animationId = requestAnimationFrame(processFrame);
        };

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
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '50%',
        transform: 'translateX(-50%)',
        color: '#fff',
        fontSize: '14px',
        backgroundColor: 'rgba(0,0,0,0.7)',
        padding: '5px 10px',
        borderRadius: '5px'
      }}>
        Move in any direction!
      </div>
    </div>
  );
} 