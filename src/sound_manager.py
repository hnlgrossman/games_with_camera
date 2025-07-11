import pygame
import threading
import os
from pathlib import Path
from src.constants import (
    STEP_RIGHT, STEP_LEFT, JUMP, BEND,
    FORWARD, BACKWARD,
    JUMP_SOUND_MOVEMENTS
)
import sys



class SoundManager:
    """Manages sound playback for movement commands"""
    
    def __init__(self, volume=0.7):
        # Ensure pygame is initialized
        if not pygame.get_init():
            pygame.init()
        
        # Ensure pygame mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100)
        
        # Determine base path for resources
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a PyInstaller bundle
            bundle_dir = Path(sys._MEIPASS)
        else:
            # Running as a normal script (adjust if your script is run from a different CWD)
            # Assuming moves_voices is in the project root, and script is run from project root
            # or that this file (sound_manager.py) is in src/ and moves_voices is at root
            # For direct script execution, if this file is src/sound_manager.py,
            # and moves_voices is at the project root:
            # bundle_dir = Path(__file__).parent.parent
            # For simplicity with PyInstaller, often easier if data files are relative to EXE.
            # If moves_voices is intended to be next to the script OR in CWD for script:
            bundle_dir = Path(".")


        # Sound file paths
        self.sound_dir = bundle_dir / "moves_voices"
        
        # Set volume (0.0 to 1.0)
        self.volume = min(1.0, max(0.0, volume))  # Clamp between 0 and 1
        pygame.mixer.music.set_volume(self.volume)
        
        # Load base sounds
        self.base_sounds = {
            STEP_LEFT: self._load_sound("left.mp3"),
            STEP_RIGHT: self._load_sound("right.mp3"),
            JUMP: self._load_sound("up.mp3"),  # Used for JUMP and FORWARD movements
            BEND: self._load_sound("down.mp3"),
            FORWARD: self._load_sound("forward.mp3"),
            BACKWARD: self._load_sound("backward.mp3")
        }
        
        # Create the full sounds dictionary with mappings
        self.sounds = {}
        
        # Add base sounds
        self.sounds.update(self.base_sounds)
        
        # Add FORWARD movements to use the "up" sound from JUMP
        for movement in JUMP_SOUND_MOVEMENTS:
            if movement != JUMP:  # JUMP is already in the base_sounds
                self.sounds[movement] = self.base_sounds[JUMP]
        
        # Print loaded sounds status
        for movement, sound in self.sounds.items():
            if sound:
                print(f"Loaded sound for: {movement}")
                # Set volume for each individual sound
                sound.set_volume(self.volume)
            else:
                print(f"Failed to load sound for: {movement}")
        
    def _load_sound(self, filename):
        """Load a sound file"""
        file_path = self.sound_dir / filename
        if not file_path.exists():
            print(f"Warning: Sound file not found: {file_path}")
            return None
        
        try:
            return pygame.mixer.Sound(str(file_path))
        except pygame.error as e:
            print(f"Error loading sound {filename}: {e}")
            return None
    
    def play_movement_sound(self, movement_type):
        """Play sound for the given movement type at 2x speed, non-blocking
        
        Args:
            movement_type: The type of movement (STEP_LEFT, STEP_RIGHT, etc)
        """
        # Get the appropriate sound
        if movement_type in self.sounds and self.sounds[movement_type]:
            # Play sound in a separate thread to not block main program
            threading.Thread(
                target=self._play_sound, 
                args=(self.sounds[movement_type],), 
                daemon=True
            ).start()
        else:
            print(f"No sound available for movement: {movement_type}")
    
    def _play_sound(self, sound):
        """Play a sound at 2x speed"""
        try:
            # In pygame, we can't directly set the playback speed
            # Instead, we need to create a channel and play the sound there
            
            # Get an available channel
            channel = pygame.mixer.find_channel(True)
            if channel:
                # Set the channel's playback speed - using pygame 2.0+ features if available
                try:
                    # This is the 2x speed setting
                    # Note: Not all pygame versions support this directly
                    if hasattr(channel, 'set_source_frequency'):
                        # For newer pygame versions
                        original_freq = 44100  # Standard frequency
                        channel.set_source_frequency(original_freq * 2)  # Double speed (2x)
                    
                    # Play the sound on this channel
                    channel.play(sound)
                except (AttributeError, NotImplementedError):
                    # Fallback for older pygame versions that don't support frequency manipulation
                    sound.play()
                    print("2x speed not supported in this pygame version, playing at normal speed")
            else:
                # Fallback if no channel is available
                sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
            # Fallback - just play the sound normally
            try:
                sound.play()
            except:
                pass 
    
    def set_volume(self, volume):
        """Set the volume for sound playback
        
        Args:
            volume: Volume level between 0.0 and 1.0
        """
        self.volume = min(1.0, max(0.0, volume))  # Clamp between 0 and 1
        pygame.mixer.music.set_volume(self.volume)
        
        # Also update volume for all loaded sounds
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume) 