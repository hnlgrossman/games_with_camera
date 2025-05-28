import React, { useRef, useCallback, useEffect, useState } from 'react';
import { Results, drawConnectors, drawLandmarks, POSE_CONNECTIONS } from '../utils/mediapipe';
import { usePoseDetection } from '../hooks/usePoseDetection';
import { MovementAnalyzer } from '../services/movementAnalyzer';
// import { SoundManager } from '../services/soundManager';
import { MovementConfig } from '../types/config';
import { Movement } from '../types/constants';

interface Props {
  config: MovementConfig;
  onMovementDetected?: (movement: Movement, data: any) => void;
}

export function MovementDetector({ config, onMovementDetected }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [movementAnalyzer] = useState(() => new MovementAnalyzer(config));
  // const [soundManager] = useState(() => new SoundManager({
  //   enabled: config.soundEnabled,
  //   volume: config.soundVolume,
  // }));
  const [detectedMovement, setDetectedMovement] = useState<Movement | null>(null);
  const [effectActive, setEffectActive] = useState(false);
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  // Initialize sound manager - COMMENTED OUT
  // useEffect(() => {
  //   if (config.soundEnabled) {
  //     soundManager.initialize();
  //   }
  // }, [config.soundEnabled, soundManager]);

  // Update FPS
  useEffect(() => {
    const interval = setInterval(() => {
      const currentTime = performance.now();
      const deltaTime = currentTime - lastTimeRef.current;
      const currentFps = Math.round((frameCountRef.current * 1000) / deltaTime);
      setFps(currentFps);
      frameCountRef.current = 0;
      lastTimeRef.current = currentTime;
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleResults = useCallback((results: Results) => {
    frameCountRef.current++;

    if (!canvasRef.current) return;
    const canvasCtx = canvasRef.current.getContext('2d');
    if (!canvasCtx) return;

    // Draw pose landmarks
    if (results.poseLandmarks) {
      drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
        color: '#00FF00',
        lineWidth: 4,
      });
      drawLandmarks(canvasCtx, results.poseLandmarks, {
        color: '#FF0000',
        lineWidth: 2,
        radius: 6,
      });
    }

    // Analyze movement
    const movementData = movementAnalyzer.analyzeFrame(results);
    if (movementData) {
      setDetectedMovement(movementData.movement);
      
      // Play sound - COMMENTED OUT
      // soundManager.playMovementSound(movementData.movement);

      // Trigger effect
      if (config.effectsEnabled) {
        setEffectActive(true);
        setTimeout(() => setEffectActive(false), 500);
      }

      // Call callback
      if (onMovementDetected) {
        onMovementDetected(movementData.movement, {
          confidence: movementData.confidence,
          timestamp: movementData.timestamp,
          fps,
        });
      }

      // Clear movement display after 1 second
      setTimeout(() => setDetectedMovement(null), 1000);
    }
  }, [movementAnalyzer, config.effectsEnabled, onMovementDetected, fps]);

  const { isLoading, error } = usePoseDetection(
    videoRef,
    canvasRef,
    config,
    handleResults
  );

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900 text-white">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Camera Error</h2>
          <p className="text-red-400">{error}</p>
          <p className="mt-4">Please ensure camera permissions are granted and refresh the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen bg-gray-900 overflow-hidden">
      {/* Hidden video element for camera feed */}
      <video
        ref={videoRef}
        className="hidden"
        playsInline
        autoPlay
        muted
      />

      {/* Canvas for rendering */}
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 ${
          effectActive ? 'animate-pulse' : ''
        }`}
        style={{
          maxWidth: '100%',
          maxHeight: '100%',
          border: effectActive ? '4px solid #10B981' : 'none',
        }}
      />

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="text-center text-white">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4" />
            <p className="text-lg">Initializing camera and pose detection...</p>
          </div>
        </div>
      )}

      {/* UI Overlay */}
      <div className="absolute top-0 left-0 right-0 p-4">
        <div className="flex justify-between items-start">
          {/* FPS Counter */}
          <div className="bg-black bg-opacity-50 text-green-400 px-3 py-1 rounded">
            FPS: {fps}
          </div>

          {/* Status indicators */}
          <div className="flex gap-2">
            {/* Sound indicator - COMMENTED OUT */}
            {/* {config.soundEnabled && (
              <div className="bg-black bg-opacity-50 text-white px-3 py-1 rounded flex items-center gap-2">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Sound ON
              </div>
            )} */}
            {config.effectsEnabled && (
              <div className="bg-black bg-opacity-50 text-white px-3 py-1 rounded flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                Effects ON
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Movement display */}
      {detectedMovement && (
        <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2">
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full shadow-2xl animate-bounce">
            <p className="text-2xl font-bold uppercase tracking-wider">
              {detectedMovement.replace('_', ' ')}
            </p>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!isLoading && !detectedMovement && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-center">
          <p className="text-gray-400 text-sm">
            Stand back so your full body is visible • Move to trigger actions
          </p>
        </div>
      )}
    </div>
  );
} 