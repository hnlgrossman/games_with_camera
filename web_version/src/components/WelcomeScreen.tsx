import React, { useState } from 'react';
import { MovementConfig, defaultConfig, adjustConfigForApp } from '../types/config';

interface Props {
  onStart: (config: MovementConfig) => void;
}

export function WelcomeScreen({ onStart }: Props) {
  const [config, setConfig] = useState<MovementConfig>(defaultConfig);
  const [cameraPermissionGranted, setCameraPermissionGranted] = useState(false);
  const [checkingPermission, setCheckingPermission] = useState(false);

  const handleRequestPermission = async () => {
    setCheckingPermission(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      setCameraPermissionGranted(true);
    } catch (error) {
      console.error('Camera permission denied:', error);
      alert('Camera permission is required to use this application. Please grant permission and refresh the page.');
    }
    setCheckingPermission(false);
  };

  const handleStart = () => {
    const adjustedConfig = adjustConfigForApp(config);
    onStart(adjustedConfig);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Games with Camera
          </h1>
          <p className="text-gray-300 text-lg">
            Web Version - Control games with your body movements!
          </p>
        </div>

        <div className="bg-gray-800 rounded-2xl shadow-2xl p-8">
          {!cameraPermissionGranted ? (
            <div className="text-center">
              <div className="mb-6">
                <svg className="w-24 h-24 mx-auto text-blue-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <h2 className="text-2xl font-semibold mb-2">Camera Permission Required</h2>
                <p className="text-gray-400">
                  This app needs access to your camera to detect your movements.
                </p>
              </div>
              <button
                onClick={handleRequestPermission}
                disabled={checkingPermission}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-8 rounded-lg transition-colors"
              >
                {checkingPermission ? 'Checking...' : 'Grant Camera Access'}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-semibold mb-4">Configure Your Experience</h2>
              </div>

              {/* App Mode Selection */}
              <div>
                <label className="block text-sm font-medium mb-2">Game Mode</label>
                <select
                  value={config.appName}
                  onChange={(e) => setConfig({ ...config, appName: e.target.value as any })}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="original">Original Mode</option>
                  <option value="dance_map">Dance Map</option>
                  <option value="wheel">Wheel Mode</option>
                </select>
              </div>

              {/* Sound Toggle - COMMENTED OUT */}
              {/* <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Enable Sound Effects</label>
                <button
                  onClick={() => setConfig({ ...config, soundEnabled: !config.soundEnabled })}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    config.soundEnabled ? 'bg-blue-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      config.soundEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div> */}

              {/* Effects Toggle */}
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Enable Visual Effects</label>
                <button
                  onClick={() => setConfig({ ...config, effectsEnabled: !config.effectsEnabled })}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    config.effectsEnabled ? 'bg-blue-600' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      config.effectsEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {/* Volume Slider - COMMENTED OUT */}
              {/* {config.soundEnabled && (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Sound Volume: {Math.round(config.soundVolume * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={config.soundVolume * 100}
                    onChange={(e) => setConfig({ ...config, soundVolume: parseInt(e.target.value) / 100 })}
                    className="w-full"
                  />
                </div>
              )} */}

              {/* Start Button */}
              <button
                onClick={handleStart}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 px-8 rounded-lg transition-all transform hover:scale-105"
              >
                Start Detection
              </button>

              {/* Instructions */}
              <div className="mt-6 p-4 bg-gray-700 rounded-lg">
                <h3 className="font-semibold mb-2">How to use:</h3>
                <ul className="text-sm text-gray-300 space-y-1">
                  <li>• Stand back so your full body is visible in the camera</li>
                  <li>• Jump up to trigger the jump action</li>
                  <li>• Step left or right to move</li>
                  <li>• Bend down to trigger the bend action</li>
                  <li>• Wait for calibration to complete before moving</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        <div className="text-center mt-6 text-gray-400 text-sm">
          <p>This application runs entirely in your browser. No data is sent to any server.</p>
        </div>
      </div>
    </div>
  );
} 