# Games with Camera - Web Version

A web-based movement detection application that uses your camera to detect body movements and trigger game actions. Built with React, TypeScript, and MediaPipe Pose.

## Features

- **Real-time pose detection** using MediaPipe Pose
- **Movement detection** for jump, bend, step left/right
- **Multiple game modes**: Original, Dance Map, and Wheel
- **Sound effects** for movements (temporarily disabled)
- **Visual effects** on movement detection
- **Fully client-side** - no server required, all processing happens in your browser
- **Privacy-focused** - no data is sent to any server

## Setup

1. Install dependencies:
```bash
npm install
```

2. ~~Add sound files~~ (Sound is temporarily disabled):
   - ~~Create a `public/sounds` directory~~
   - ~~Add the following sound files (MP3 format):~~
     - ~~`jump.mp3` - for jump movements~~
     - ~~`step.mp3` - for step movements~~
     - ~~`bend.mp3` - for bend movements~~

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:3000`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

1. **Grant camera permissions** when prompted
2. **Configure your preferences**:
   - Choose game mode
   - ~~Enable/disable sound effects~~ (temporarily disabled)
   - Enable/disable visual effects
   - ~~Adjust sound volume~~ (temporarily disabled)
3. **Position yourself** so your full body is visible in the camera
4. **Wait for calibration** (the system calibrates your base height)
5. **Start moving!**
   - Jump up for jump action
   - Step left or right for movement
   - Bend down for bend action

## Browser Requirements

- Modern browser with WebRTC support (Chrome, Firefox, Edge, Safari)
- Camera/webcam access
- JavaScript enabled

## Technical Details

- **React 18** with TypeScript for the UI
- **MediaPipe Pose** for skeletal tracking
- **Tailwind CSS** for styling
- **Vite** for fast development and building
- **Zustand** for state management (if needed for future features)

## Movement Detection Algorithm

The application uses a sophisticated movement detection algorithm that:
- Calibrates your base height when you're standing still
- Tracks landmark positions over multiple frames
- Detects movements based on position changes relative to your calibrated height
- Implements cooldown periods to prevent false positives
- Requires stable detection across multiple frames for accuracy

## Privacy

This application runs entirely in your browser. No video data, images, or pose information is sent to any server. All processing happens locally on your device.

## Troubleshooting

**Camera not working?**
- Ensure you've granted camera permissions
- Check if another application is using the camera
- Try refreshing the page

**Movements not detected?**
- Stand further back so your full body is visible
- Ensure good lighting
- Wait for the calibration phase to complete
- Try adjusting the detection thresholds in the code

**Performance issues?**
- Close other browser tabs
- Ensure you're using a modern browser
- Try reducing the video resolution in the code

## Note

Sound functionality is temporarily disabled in this version. The visual feedback and movement detection work normally. 