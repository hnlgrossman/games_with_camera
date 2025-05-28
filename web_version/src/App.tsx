import React, { useState, useCallback, useEffect } from 'react';
import { WelcomeScreen } from './components/WelcomeScreen';
import { MovementDetector } from './components/MovementDetector';
import { MovementConfig } from './types/config';
import { Movement } from './types/constants';

function App() {
  const [config, setConfig] = useState<MovementConfig | null>(null);
  const [movementHistory, setMovementHistory] = useState<Array<{ movement: Movement; timestamp: number }>>([]);
  const [mediaPipeLoaded, setMediaPipeLoaded] = useState(false);

  useEffect(() => {
    // Check if MediaPipe is loaded
    const checkMediaPipe = () => {
      if ((window as any).Pose && (window as any).Camera) {
        setMediaPipeLoaded(true);
      } else {
        setTimeout(checkMediaPipe, 100);
      }
    };
    checkMediaPipe();
  }, []);

  const handleStart = useCallback((selectedConfig: MovementConfig) => {
    setConfig(selectedConfig);
  }, []);

  const handleMovementDetected = useCallback((movement: Movement, data: any) => {
    console.log('Movement detected:', movement, data);
    setMovementHistory(prev => [...prev.slice(-9), { movement, timestamp: Date.now() }]);
  }, []);

  if (!mediaPipeLoaded) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4" />
          <p className="text-lg">Loading MediaPipe libraries...</p>
        </div>
      </div>
    );
  }

  if (!config) {
    return <WelcomeScreen onStart={handleStart} />;
  }

  return (
    <div className="relative">
      <MovementDetector
        config={config}
        onMovementDetected={handleMovementDetected}
      />

      {/* Movement History Display */}
      <div className="absolute top-20 left-4 bg-black bg-opacity-50 rounded-lg p-4 max-w-xs">
        <h3 className="text-white font-semibold mb-2">Movement History</h3>
        <div className="space-y-1">
          {movementHistory.length === 0 ? (
            <p className="text-gray-400 text-sm">No movements detected yet</p>
          ) : (
            movementHistory.map((item, index) => (
              <div key={index} className="text-gray-300 text-sm">
                {new Date(item.timestamp).toLocaleTimeString()} - {item.movement.replace('_', ' ')}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Back Button */}
      <button
        onClick={() => setConfig(null)}
        className="absolute top-4 right-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Exit
      </button>
    </div>
  );
}

export default App; 