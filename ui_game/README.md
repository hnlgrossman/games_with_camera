# Obstacle Course Game

A simple obstacle course game built with Pygame where the player needs to avoid obstacles.

## Project Structure

The project is organized in a modular way to support maintainability and extensibility:

- `main.py`: Entry point that initializes and runs the game
- `constants.py`: Defines all game constants (colors, dimensions, etc.)
- `player.py`: Player class implementation
- `obstacle.py`: Obstacle class with different shapes
- `course.py`: Course class that manages a game level
- `course_factory.py`: Factory class for creating different courses
- `game_engine.py`: Main game loop and logic
- `game.py`: Legacy entry point that now imports from main.py

## Features

- Multiple courses with different difficulty levels
- Different obstacle types (rectangle, circle, triangle)
- Score and time tracking
- Easy switching between courses during gameplay

## Controls

- Use left/right arrow keys to move between lanes
- Press 'C' to change courses
- Press 'ESC' to quit

## How to Run

```bash
python -m ui_game.game
```

or

```bash
python -m ui_game.main
```

## Course Levels

1. **Easy Course**: Simple rectangular obstacles at slow speed
2. **Medium Course**: Rectangle and circle obstacles at medium speed
3. **Hard Course**: All obstacle types at faster speeds
4. **Extreme Course**: All obstacle types at very high speeds 