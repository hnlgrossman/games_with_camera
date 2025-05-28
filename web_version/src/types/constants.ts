// MediaPipe Pose landmark indices
export const POSE_LANDMARKS = {
  NOSE: 0,
  LEFT_EYE_INNER: 1,
  LEFT_EYE: 2,
  LEFT_EYE_OUTER: 3,
  RIGHT_EYE_INNER: 4,
  RIGHT_EYE: 5,
  RIGHT_EYE_OUTER: 6,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  LEFT_MOUTH: 9,
  RIGHT_MOUTH: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_PINKY: 17,
  RIGHT_PINKY: 18,
  LEFT_INDEX: 19,
  RIGHT_INDEX: 20,
  LEFT_THUMB: 21,
  RIGHT_THUMB: 22,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,
  RIGHT_HEEL: 30,
  LEFT_FOOT_INDEX: 31,
  RIGHT_FOOT_INDEX: 32,
} as const;

// Movement types
export const MOVEMENTS = {
  STEP_RIGHT: 'step_right',
  STEP_LEFT: 'step_left',
  JUMP: 'jump',
  BEND: 'bend',
  FORWARD: 'forward',
  BACKWARD: 'backward',
  FORWARD_RIGHT: 'forward_right',
  FORWARD_LEFT: 'forward_left',
} as const;

export type Movement = typeof MOVEMENTS[keyof typeof MOVEMENTS];

// Sound mappings
export const JUMP_SOUND_MOVEMENTS = [
  MOVEMENTS.JUMP,
  MOVEMENTS.FORWARD_RIGHT,
  MOVEMENTS.FORWARD_LEFT,
] as const; 