import logging
from typing import Set
from input_events import KeyCode, InputEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s')

class KeyChord:
    def __init__(self, keys: Set[KeyCode | frozenset[KeyCode]]):
        self.keys = keys
        self.pressed_keys: Set[KeyCode] = set()
        logging.info(f"Initialized KeyChord with keys: {keys}")

    def update(self, key: KeyCode, event_type: InputEvent) -> bool:
        try:
            if event_type == InputEvent.KEY_PRESS:
                self.pressed_keys.add(key)
            elif event_type == InputEvent.KEY_RELEASE:
                self.pressed_keys.discard(key)

            logging.debug(f"Current pressed keys: {self.pressed_keys}")
            logging.debug(f"Required keys: {self.keys}")

            is_active = self.is_active()
            logging.debug(f"KeyChord active: {is_active}")
            return is_active
        except Exception as e:
            logging.error(f"Error updating KeyChord: {e}")
            return False

    def is_active(self) -> bool:
        try:
            for key in self.keys:
                if isinstance(key, frozenset):
                    if not any(k in self.pressed_keys for k in key):
                        return False
                elif key not in self.pressed_keys:
                    return False
            return len(self.pressed_keys) == len(self.keys)  # Ensure all required keys are pressed
        except Exception as e:
            logging.error(f"Error checking if KeyChord is active: {e}")
            return False