export interface MovementConfig {
  minDetectionConfidence: number;
  minTrackingConfidence: number;
  requiredStableFramesPerFps: number;
  numFramesToCheckPerFps: number;
  jumpThreshold: number;
  stepThreshold: number;
  bendThreshold: number;
  cooldownPeriod: number;
  stabilityThreshold: number;
  stabilityMovesThreshold: {
    jump: number;
    bend: number;
  };
  visibilityThreshold: number;
  soundEnabled: boolean;
  soundVolume: number;
  appName: 'original' | 'dance_map' | 'wheel';
  allowMultipleMovements: boolean;
  effectsEnabled: boolean;
  straightPoseXSpreadThreshold: number;
  stillnessThreshold: number;
  minBaseHeightThreshold: number;
}

export const defaultConfig: MovementConfig = {
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5,
  requiredStableFramesPerFps: 4,
  numFramesToCheckPerFps: 5,
  jumpThreshold: 0.012,
  stepThreshold: 0.04,
  bendThreshold: 0.06,
  cooldownPeriod: 1.0,
  stabilityThreshold: 0.028,
  stabilityMovesThreshold: {
    jump: 0.01,
    bend: 0.01,
  },
  visibilityThreshold: 0.5,
  soundEnabled: false,
  soundVolume: 0.7,
  appName: 'original',
  allowMultipleMovements: false,
  effectsEnabled: true,
  straightPoseXSpreadThreshold: 0.15,
  stillnessThreshold: 0.03,
  minBaseHeightThreshold: 0.4,
};

export function adjustConfigForApp(config: MovementConfig): MovementConfig {
  const adjustedConfig = { ...config };
  
  if (config.appName === 'original') {
    adjustedConfig.numFramesToCheckPerFps = 5;
  } else if (config.appName === 'dance_map') {
    adjustedConfig.numFramesToCheckPerFps = 3;
    adjustedConfig.allowMultipleMovements = true;
  } else if (config.appName === 'wheel') {
    adjustedConfig.allowMultipleMovements = true;
  }
  
  return adjustedConfig;
} 