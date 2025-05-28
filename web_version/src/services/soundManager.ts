import { Movement, MOVEMENTS, JUMP_SOUND_MOVEMENTS } from '../types/constants';

interface SoundConfig {
  enabled: boolean;
  volume: number;
}

export class SoundManager {
  private sounds: Map<string, HTMLAudioElement> = new Map();
  private config: SoundConfig;
  private isInitialized: boolean = false;

  constructor(config: SoundConfig) {
    this.config = config;
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Load sound files
      const soundFiles = {
        jump: '/sounds/jump.mp3',
        step: '/sounds/step.mp3',
        bend: '/sounds/bend.mp3',
      };

      for (const [key, path] of Object.entries(soundFiles)) {
        const audio = new Audio(path);
        audio.volume = this.config.volume;
        audio.preload = 'auto';
        
        // Create a promise that resolves when the audio is loaded
        await new Promise((resolve, reject) => {
          audio.addEventListener('canplaythrough', resolve, { once: true });
          audio.addEventListener('error', reject, { once: true });
          audio.load();
        });

        this.sounds.set(key, audio);
      }

      this.isInitialized = true;
      console.log('SoundManager: Sounds loaded successfully');
    } catch (error) {
      console.error('SoundManager: Failed to load sounds:', error);
    }
  }

  public playMovementSound(movement: Movement): void {
    if (!this.config.enabled || !this.isInitialized) return;

    let soundKey: string;

    // Map movement to sound
    if (JUMP_SOUND_MOVEMENTS.includes(movement as any)) {
      soundKey = 'jump';
    } else if (movement === MOVEMENTS.STEP_LEFT || movement === MOVEMENTS.STEP_RIGHT) {
      soundKey = 'step';
    } else if (movement === MOVEMENTS.BEND || movement === MOVEMENTS.BACKWARD) {
      soundKey = 'bend';
    } else {
      return; // No sound for this movement
    }

    const sound = this.sounds.get(soundKey);
    if (sound) {
      // Clone and play to allow overlapping sounds
      const clone = sound.cloneNode() as HTMLAudioElement;
      clone.volume = this.config.volume;
      clone.play().catch(error => {
        console.error(`SoundManager: Failed to play ${soundKey} sound:`, error);
      });
    }
  }

  public setVolume(volume: number): void {
    this.config.volume = Math.max(0, Math.min(1, volume));
    this.sounds.forEach(sound => {
      sound.volume = this.config.volume;
    });
  }

  public setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
  }

  public getConfig(): SoundConfig {
    return { ...this.config };
  }
} 