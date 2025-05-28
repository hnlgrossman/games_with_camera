import { useEffect, useRef, useState, useCallback } from 'react';
import { Pose, Camera, Results } from '../utils/mediapipe';
import { MovementConfig } from '../types/config';

export function usePoseDetection(
  videoRef: React.RefObject<HTMLVideoElement>,
  canvasRef: React.RefObject<HTMLCanvasElement>,
  config: MovementConfig,
  onResults: (results: Results) => void
) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const poseRef = useRef<any | null>(null);
  const cameraRef = useRef<any | null>(null);
  const isCleaningUp = useRef(false);

  const cleanup = useCallback(() => {
    isCleaningUp.current = true;
    
    // Stop camera first
    if (cameraRef.current) {
      try {
        cameraRef.current.stop();
      } catch (e) {
        console.warn('Error stopping camera:', e);
      }
      cameraRef.current = null;
    }
    
    // Stop video stream
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => {
        try {
          track.stop();
        } catch (e) {
          console.warn('Error stopping track:', e);
        }
      });
      videoRef.current.srcObject = null;
    }
    
    // Close pose last
    if (poseRef.current) {
      try {
        poseRef.current.close();
      } catch (e) {
        console.warn('Error closing pose:', e);
      }
      poseRef.current = null;
    }
  }, [videoRef]);

  useEffect(() => {
    let mounted = true;
    isCleaningUp.current = false;

    const initializePose = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Wait for refs to be available
        let refAttempts = 0;
        while ((!videoRef.current || !canvasRef.current) && refAttempts < 10 && mounted) {
          await new Promise(resolve => setTimeout(resolve, 100));
          refAttempts++;
        }

        if (!mounted || isCleaningUp.current) return;

        if (!videoRef.current || !canvasRef.current) {
          throw new Error('Video or canvas element not found');
        }

        // Wait for MediaPipe to be loaded
        let attempts = 0;
        while (!Pose || !Camera) {
          if (!mounted || isCleaningUp.current) return;
          if (attempts > 20) {
            throw new Error('MediaPipe failed to load. Please refresh the page.');
          }
          await new Promise(resolve => setTimeout(resolve, 100));
          attempts++;
        }

        if (!mounted || isCleaningUp.current) return;

        // Get camera stream first
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
              width: 640, 
              height: 480,
              facingMode: 'user'
            } 
          });
          
          if (!mounted || isCleaningUp.current) {
            stream.getTracks().forEach(track => track.stop());
            return;
          }
          
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            
            // Wait for video to be ready
            await new Promise<void>((resolve, reject) => {
              if (!videoRef.current) {
                reject(new Error('Video element lost'));
                return;
              }
              
              const video = videoRef.current;
              
              const handleLoadedMetadata = () => {
                video.removeEventListener('loadedmetadata', handleLoadedMetadata);
                video.removeEventListener('error', handleError);
                resolve();
              };
              
              const handleError = () => {
                video.removeEventListener('loadedmetadata', handleLoadedMetadata);
                video.removeEventListener('error', handleError);
                reject(new Error('Video failed to load'));
              };
              
              video.addEventListener('loadedmetadata', handleLoadedMetadata);
              video.addEventListener('error', handleError);
              
              // Timeout after 5 seconds
              setTimeout(() => {
                video.removeEventListener('loadedmetadata', handleLoadedMetadata);
                video.removeEventListener('error', handleError);
                reject(new Error('Video load timeout'));
              }, 5000);
            });
          }
        } catch (err) {
          throw new Error('Failed to access camera. Please ensure camera permissions are granted.');
        }

        if (!mounted || isCleaningUp.current) return;

        // Initialize MediaPipe Pose
        const pose = new Pose({
          locateFile: (file: string) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
          },
        });

        if (!mounted || isCleaningUp.current) {
          pose.close();
          return;
        }

        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: config.minDetectionConfidence,
          minTrackingConfidence: config.minTrackingConfidence,
        });

        pose.onResults((results: Results) => {
          if (!mounted || isCleaningUp.current || !canvasRef.current) return;

          const canvasCtx = canvasRef.current.getContext('2d');
          if (!canvasCtx) return;

          canvasCtx.save();
          canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          
          // Draw the video frame
          canvasCtx.drawImage(
            results.image,
            0,
            0,
            canvasRef.current.width,
            canvasRef.current.height
          );

          // Call the onResults callback
          onResults(results);

          canvasCtx.restore();
        });

        poseRef.current = pose;

        if (!mounted || isCleaningUp.current) return;

        // Initialize MediaPipe camera
        if (videoRef.current) {
          const camera = new Camera(videoRef.current, {
            onFrame: async () => {
              if (!mounted || isCleaningUp.current || !poseRef.current || !videoRef.current) return;
              
              try {
                await poseRef.current.send({ image: videoRef.current });
              } catch (err) {
                if (!isCleaningUp.current) {
                  console.error('Error sending frame to pose:', err);
                }
              }
            },
            width: 640,
            height: 480,
          });

          cameraRef.current = camera;
          
          if (!mounted || isCleaningUp.current) return;
          
          await camera.start();
        }

        if (mounted && !isCleaningUp.current) {
          setIsLoading(false);
        }
      } catch (err) {
        if (mounted && !isCleaningUp.current) {
          console.error('Error initializing pose detection:', err);
          setError(err instanceof Error ? err.message : 'Failed to initialize pose detection');
          setIsLoading(false);
        }
      }
    };

    // Add a small delay to ensure page is fully loaded
    const timeoutId = setTimeout(initializePose, 500);

    // Cleanup
    return () => {
      mounted = false;
      clearTimeout(timeoutId);
      cleanup();
    };
  }, [videoRef, canvasRef, config.minDetectionConfidence, config.minTrackingConfidence, onResults, cleanup]);

  return { isLoading, error };
} 