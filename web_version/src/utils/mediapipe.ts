// MediaPipe wrapper to handle module loading issues
// We don't import the modules here, they're loaded via script tags in index.html

// Re-export the global objects that MediaPipe creates
export const Pose = (window as any).Pose;
export const Camera = (window as any).Camera;
export const drawConnectors = (window as any).drawConnectors;
export const drawLandmarks = (window as any).drawLandmarks;
export const POSE_CONNECTIONS = (window as any).POSE_CONNECTIONS;

// Type definitions
export interface Results {
  image: HTMLCanvasElement | HTMLVideoElement;
  poseLandmarks?: any[];
  poseWorldLandmarks?: any[];
  segmentationMask?: any;
} 