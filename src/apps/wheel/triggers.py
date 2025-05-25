from typing import Dict, Any
from .constants import START_RIGHT, START_LEFT, END_RIGHT, END_LEFT
from pynput.keyboard import Key, Controller

keyboard = Controller()

def movement_callback(movement: str, data: Dict[str, Any]) -> None:
    print(f"Movement+++++++++: {movement}")
    if movement == START_RIGHT:
        print("START_RIGHT")
        keyboard.press(Key.right)
    elif movement == START_LEFT:
        print("START_LEFT")
        keyboard.press(Key.left)
    elif movement == END_RIGHT:
        print("END_RIGHT")
        keyboard.release(Key.right)
    elif movement == END_LEFT:
        print("END_LEFT")
        keyboard.release(Key.left)
        
