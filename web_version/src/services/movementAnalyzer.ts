import { Results } from '../utils/mediapipe';
import { MovementConfig } from '../types/config';
import { Movement, MOVEMENTS, POSE_LANDMARKS } from '../types/constants';

interface MovementData {
  movement: Movement;
  confidence: number;
  timestamp: number;
}

export class MovementAnalyzer {
  private config: MovementConfig;
  private frameHistory: Results[] = [];
  private lastMovementTime: number = 0;
  private baseHeight: number | null = null;
  private calibrationFrames: Results[] = [];
  private isCalibrated: boolean = false;
  
  constructor(config: MovementConfig) {
    this.config = config;
  }

  public analyzeFrame(results: Results): MovementData | null {
    if (!results.poseLandmarks) return null;

    // Add to frame history
    this.frameHistory.push(results);
    if (this.frameHistory.length > this.config.numFramesToCheckPerFps) {
      this.frameHistory.shift();
    }

    // Calibration phase
    if (!this.isCalibrated) {
      this.calibrationFrames.push(results);
      if (this.calibrationFrames.length >= 30) {
        this.calibrateBaseHeight();
        this.isCalibrated = true;
      }
      return null;
    }

    // Check for movements
    const currentTime = Date.now();
    if (currentTime - this.lastMovementTime < this.config.cooldownPeriod * 1000) {
      return null;
    }

    // Check visibility
    const avgVisibility = this.getAverageVisibility(results.poseLandmarks);
    if (avgVisibility < this.config.visibilityThreshold) {
      return null;
    }

    // Detect movements
    const movement = this.detectMovement();
    if (movement) {
      this.lastMovementTime = currentTime;
      return {
        movement,
        confidence: 1.0,
        timestamp: currentTime,
      };
    }

    return null;
  }

  private calibrateBaseHeight(): void {
    const validHeights: number[] = [];

    for (const frame of this.calibrationFrames) {
      if (!frame.poseLandmarks) continue;

      const nose = frame.poseLandmarks[POSE_LANDMARKS.NOSE];
      const leftFoot = frame.poseLandmarks[POSE_LANDMARKS.LEFT_FOOT_INDEX];
      const rightFoot = frame.poseLandmarks[POSE_LANDMARKS.RIGHT_FOOT_INDEX];

      if (this.isPoseStraight(frame.poseLandmarks) && this.isStill(frame.poseLandmarks)) {
        const footY = Math.max(leftFoot.y, rightFoot.y);
        const height = footY - nose.y;
        
        if (height > this.config.minBaseHeightThreshold) {
          validHeights.push(height);
        }
      }
    }

    if (validHeights.length > 0) {
      this.baseHeight = validHeights.reduce((a, b) => a + b) / validHeights.length;
      console.log('MovementAnalyzer: Base height calibrated:', this.baseHeight);
    } else {
      // Fallback calibration
      const allHeights = this.calibrationFrames
        .filter(f => f.poseLandmarks)
        .map(f => {
          const nose = f.poseLandmarks![POSE_LANDMARKS.NOSE];
          const leftFoot = f.poseLandmarks![POSE_LANDMARKS.LEFT_FOOT_INDEX];
          const rightFoot = f.poseLandmarks![POSE_LANDMARKS.RIGHT_FOOT_INDEX];
          const footY = Math.max(leftFoot.y, rightFoot.y);
          return footY - nose.y;
        });

      if (allHeights.length > 0) {
        this.baseHeight = allHeights.reduce((a, b) => a + b) / allHeights.length;
        console.log('MovementAnalyzer: Base height calibrated (fallback):', this.baseHeight);
      }
    }
  }

  private isPoseStraight(landmarks: any[]): boolean {
    const shoulders = [
      landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
      landmarks[POSE_LANDMARKS.RIGHT_SHOULDER],
    ];
    const hips = [
      landmarks[POSE_LANDMARKS.LEFT_HIP],
      landmarks[POSE_LANDMARKS.RIGHT_HIP],
    ];
    const knees = [
      landmarks[POSE_LANDMARKS.LEFT_KNEE],
      landmarks[POSE_LANDMARKS.RIGHT_KNEE],
    ];

    const keyPoints = [...shoulders, ...hips, ...knees];
    const xCoords = keyPoints.map(p => p.x);
    const xSpread = Math.max(...xCoords) - Math.min(...xCoords);

    return xSpread < this.config.straightPoseXSpreadThreshold;
  }

  private isStill(landmarks: any[]): boolean {
    if (this.frameHistory.length < 2) return false;

    const prevFrame = this.frameHistory[this.frameHistory.length - 2];
    if (!prevFrame.poseLandmarks) return false;

    const currentNose = landmarks[POSE_LANDMARKS.NOSE];
    const prevNose = prevFrame.poseLandmarks[POSE_LANDMARKS.NOSE];

    const movement = Math.sqrt(
      Math.pow(currentNose.x - prevNose.x, 2) +
      Math.pow(currentNose.y - prevNose.y, 2)
    );

    return movement < this.config.stillnessThreshold;
  }

  private getAverageVisibility(landmarks: any[]): number {
    const visibilities = landmarks.map(l => l.visibility || 0);
    return visibilities.reduce((a, b) => a + b) / visibilities.length;
  }

  private detectMovement(): Movement | null {
    if (this.frameHistory.length < this.config.requiredStableFramesPerFps) {
      return null;
    }

    // Check for jump
    if (this.checkJump()) {
      return MOVEMENTS.JUMP;
    }

    // Check for bend
    if (this.checkBend()) {
      return MOVEMENTS.BEND;
    }

    // Check for steps
    const stepDirection = this.checkStep();
    if (stepDirection === 'left') {
      return MOVEMENTS.STEP_LEFT;
    } else if (stepDirection === 'right') {
      return MOVEMENTS.STEP_RIGHT;
    }

    return null;
  }

  private checkJump(): boolean {
    if (!this.baseHeight) return false;

    const recentFrames = this.frameHistory.slice(-this.config.requiredStableFramesPerFps);
    let jumpDetected = 0;

    for (const frame of recentFrames) {
      if (!frame.poseLandmarks) continue;

      const nose = frame.poseLandmarks[POSE_LANDMARKS.NOSE];
      const leftFoot = frame.poseLandmarks[POSE_LANDMARKS.LEFT_FOOT_INDEX];
      const rightFoot = frame.poseLandmarks[POSE_LANDMARKS.RIGHT_FOOT_INDEX];

      const currentHeight = Math.max(leftFoot.y, rightFoot.y) - nose.y;
      const heightChange = (this.baseHeight - currentHeight) / this.baseHeight;

      if (heightChange > this.config.jumpThreshold) {
        jumpDetected++;
      }
    }

    return jumpDetected >= this.config.requiredStableFramesPerFps * 0.7;
  }

  private checkBend(): boolean {
    const recentFrames = this.frameHistory.slice(-this.config.requiredStableFramesPerFps);
    let bendDetected = 0;

    for (const frame of recentFrames) {
      if (!frame.poseLandmarks) continue;

      const nose = frame.poseLandmarks[POSE_LANDMARKS.NOSE];
      const leftHip = frame.poseLandmarks[POSE_LANDMARKS.LEFT_HIP];
      const rightHip = frame.poseLandmarks[POSE_LANDMARKS.RIGHT_HIP];
      const leftKnee = frame.poseLandmarks[POSE_LANDMARKS.LEFT_KNEE];
      const rightKnee = frame.poseLandmarks[POSE_LANDMARKS.RIGHT_KNEE];

      const avgHipY = (leftHip.y + rightHip.y) / 2;
      const avgKneeY = (leftKnee.y + rightKnee.y) / 2;

      // Check if knees are bent (closer to hips)
      const kneeBend = avgKneeY - avgHipY;
      const noseToKneeDistance = avgKneeY - nose.y;

      if (kneeBend < this.config.bendThreshold && noseToKneeDistance < 0.5) {
        bendDetected++;
      }
    }

    return bendDetected >= this.config.requiredStableFramesPerFps * 0.7;
  }

  private checkStep(): 'left' | 'right' | null {
    if (this.frameHistory.length < 2) return null;

    const currentFrame = this.frameHistory[this.frameHistory.length - 1];
    const prevFrame = this.frameHistory[0];

    if (!currentFrame.poseLandmarks || !prevFrame.poseLandmarks) return null;

    const currentLeftFoot = currentFrame.poseLandmarks[POSE_LANDMARKS.LEFT_FOOT_INDEX];
    const currentRightFoot = currentFrame.poseLandmarks[POSE_LANDMARKS.RIGHT_FOOT_INDEX];
    const prevLeftFoot = prevFrame.poseLandmarks[POSE_LANDMARKS.LEFT_FOOT_INDEX];
    const prevRightFoot = prevFrame.poseLandmarks[POSE_LANDMARKS.RIGHT_FOOT_INDEX];

    const leftMovement = Math.abs(currentLeftFoot.x - prevLeftFoot.x);
    const rightMovement = Math.abs(currentRightFoot.x - prevRightFoot.x);

    if (leftMovement > this.config.stepThreshold && leftMovement > rightMovement) {
      return currentLeftFoot.x < prevLeftFoot.x ? 'left' : 'right';
    } else if (rightMovement > this.config.stepThreshold && rightMovement > leftMovement) {
      return currentRightFoot.x < prevRightFoot.x ? 'left' : 'right';
    }

    return null;
  }

  public reset(): void {
    this.frameHistory = [];
    this.lastMovementTime = 0;
    this.baseHeight = null;
    this.calibrationFrames = [];
    this.isCalibrated = false;
  }
} 