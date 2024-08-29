import logging
from typing import Callable, Set
from input_events import KeyCode, InputEvent
from key_chord import KeyChord
from input_backend.base import InputBackend
from input_backend.evdev_backend import EvdevBackend
from input_backend.pynput_backend import PynputBackend
from utils import ConfigManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s')

class KeyListener:
    def __init__(self):
        self.backends = []
        self.active_backend = None
        self.key_chord = None
        self.callbacks = {
            "on_activate": [],
            "on_deactivate": []
        }
        try:
            self.load_activation_keys()
            self.initialize_backends()
            self.select_backend_from_config()
            logging.info(f"Current activation key combination: {self.key_chord.keys}")
        except Exception as e:
            logging.error(f"Error initializing KeyListener: {e}")
            raise

    def initialize_backends(self):
        backend_classes = [EvdevBackend, PynputBackend]
        try:
            self.backends = [backend_class() for backend_class in backend_classes if backend_class.is_available()]
            logging.info(f"Initialized backends: {[b.__class__.__name__ for b in self.backends]}")
        except Exception as e:
            logging.error(f"Error initializing backends: {e}")
            raise

    def select_backend_from_config(self):
        try:
            preferred_backend = ConfigManager.get_config_value('recording_options', 'input_backend')
            logging.info(f"Preferred backend from config: {preferred_backend}")

            if preferred_backend == 'auto':
                self.select_active_backend()
            else:
                backend_map = {
                    'evdev': EvdevBackend,
                    'pynput': PynputBackend
                }

                if preferred_backend in backend_map:
                    try:
                        self.set_active_backend(backend_map[preferred_backend])
                    except ValueError as e:
                        logging.warning(f"Preferred backend '{preferred_backend}' is not available. Falling back to auto selection. Error: {e}")
                        self.select_active_backend()
                else:
                    logging.warning(f"Unknown backend '{preferred_backend}'. Falling back to auto selection.")
                    self.select_active_backend()
            
            logging.info(f"Selected backend: {self.active_backend.__class__.__name__}")
        except Exception as e:
            logging.error(f"Error selecting backend from config: {e}")
            raise

    def select_active_backend(self):
        if not self.backends:
            raise RuntimeError("No supported input backend found")
        self.active_backend = self.backends[0]
        self.active_backend.on_input_event = self.on_input_event

    def set_active_backend(self, backend_class):
        new_backend = next((b for b in self.backends if isinstance(b, backend_class)), None)
        if new_backend:
            if self.active_backend:
                self.stop()
            self.active_backend = new_backend
            self.active_backend.on_input_event = self.on_input_event
            self.start()
        else:
            raise ValueError(f"Backend {backend_class.__name__} is not available")

    def update_backend(self):
        self.select_backend_from_config()

    def start(self):
        if self.active_backend:
            self.active_backend.start()
        else:
            raise RuntimeError("No active backend selected")

    def stop(self):
        if self.active_backend:
            self.active_backend.stop()

    def load_activation_keys(self):
        key_combination = ConfigManager.get_config_value('recording_options', 'activation_key')
        keys = self.parse_key_combination(key_combination)
        self.set_activation_keys(keys)

    def parse_key_combination(self, combination_string: str) -> Set[KeyCode | frozenset[KeyCode]]:
        keys = set()
        key_map = {
            'CTRL': frozenset({KeyCode.CTRL_LEFT, KeyCode.CTRL_RIGHT}),
            'SHIFT': frozenset({KeyCode.SHIFT_LEFT, KeyCode.SHIFT_RIGHT}),
            'ALT': frozenset({KeyCode.ALT_LEFT, KeyCode.ALT_RIGHT}),
            'META': frozenset({KeyCode.META_LEFT, KeyCode.META_RIGHT}),
        }

        for key in combination_string.upper().split('+'):
            key = key.strip()
            if key in key_map:
                keys.add(key_map[key])
            else:
                try:
                    keycode = KeyCode[key]
                    keys.add(keycode)
                except KeyError:
                    print(f"Unknown key: {key}")
        return keys

    def set_activation_keys(self, keys: Set[KeyCode]):
        self.key_chord = KeyChord(keys)

    def on_input_event(self, event):
        if not self.key_chord or not self.active_backend:
            return

        key, event_type = event

        try:
            was_active = self.key_chord.is_active()
            is_active = self.key_chord.update(key, event_type)

            if not was_active and is_active:
                logging.info(f"Activation key combination triggered: {self.key_chord.keys}")
                self._trigger_callbacks("on_activate")
            elif was_active and not is_active:
                logging.info(f"Deactivation of key combination: {self.key_chord.keys}")
                self._trigger_callbacks("on_deactivate")
        except Exception as e:
            logging.error(f"Error processing input event: {e}")

    def add_callback(self, event: str, callback: Callable):
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str):
        for callback in self.callbacks.get(event, []):
            callback()

    def update_activation_keys(self):
        self.load_activation_keys()