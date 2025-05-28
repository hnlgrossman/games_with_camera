# Minimal Movement Detector

This is a bare-bones, performance-optimized version of the movement detector.

## Features
- Ultra-fast performance (320x240 resolution, lowest model complexity)
- Simple jump detection
- Minimal UI
- No external dependencies beyond MediaPipe

## To Run

1. Make sure you're in the `web_version` directory
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Open http://localhost:3000
5. Allow camera access when prompted
6. Jump to see detection!

## Performance Optimizations
- Resolution: 320x240 (vs 640x480)
- Model complexity: 0 (lowest)
- No landmark smoothing
- No segmentation
- Direct canvas rendering
- Minimal React re-renders

## Browser Console Warnings
The OpenGL warning (`OpenGL error checking is disabled`) is normal and doesn't affect functionality. It's MediaPipe using hardware acceleration.

The Chrome extension error you saw is from a browser extension (likely Loom) and not from this application. 