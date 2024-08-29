import logging
from input_backend.base import InputBackend
from input_events import KeyCode, InputEvent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s')

class PynputBackend(InputBackend):
    @classmethod
    def is_available(cls) -> bool:
        try:
            import pynput
            return True
        except ImportError:
            logging.warning("Pynput is not available")
            return False

    def __init__(self):
        self.keyboard_listener = None
        self.mouse_listener = None
        self.keyboard = None
        self.mouse = None
        self.key_map = None
        logging.info("Initialized PynputBackend")

    def start(self):
        """Start listening for keyboard and mouse events."""
        try:
            if self.keyboard is None or self.mouse is None:
                from pynput import keyboard, mouse
                self.keyboard = keyboard
                self.mouse = mouse
                self.key_map = self._create_key_map()

            self.keyboard_listener = self.keyboard.Listener(
                on_press=self._on_keyboard_press,
                on_release=self._on_keyboard_release
            )
            self.mouse_listener = self.mouse.Listener(
                on_click=self._on_mouse_click
            )
            self.keyboard_listener.start()
            self.mouse_listener.start()
            logging.info("Started PynputBackend")
        except Exception as e:
            logging.error(f"Error starting PynputBackend: {e}")
            raise

    def stop(self):
        """Stop listening for keyboard and mouse events."""
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            logging.info("Stopped PynputBackend")
        except Exception as e:
            logging.error(f"Error stopping PynputBackend: {e}")

    def _translate_key_event(self, native_event) -> tuple[KeyCode | None, InputEvent]:
        """Translate a pynput event to our internal event representation."""
        try:
            pynput_key, is_press = native_event
            key_code = self._get_key_code(pynput_key)
            event_type = InputEvent.KEY_PRESS if is_press else InputEvent.KEY_RELEASE
            return key_code, event_type
        except Exception as e:
            logging.error(f"Error translating key event: {e}")
            return None, InputEvent.KEY_PRESS

    def _get_key_code(self, pynput_key) -> KeyCode | None:
        """Get the corresponding KeyCode for a pynput key."""
        if isinstance(pynput_key, self.keyboard.KeyCode):
            if pynput_key.char:
                return self.key_map.get(self.keyboard.KeyCode.from_char(pynput_key.char.lower()))
            elif pynput_key.vk:
                return self.key_map.get(self.keyboard.KeyCode.from_vk(pynput_key.vk))
        return self.key_map.get(pynput_key)

    def _on_keyboard_press(self, key):
        """Handle keyboard press events."""
        try:
            translated_event = self._translate_key_event((key, True))
            if translated_event[0] is not None:
                logging.debug(f"Pynput keyboard press: key={translated_event[0]}")
                self.on_input_event(translated_event)
        except Exception as e:
            logging.error(f"Error handling keyboard press event: {e}")

    def _on_keyboard_release(self, key):
        """Handle keyboard release events."""
        try:
            translated_event = self._translate_key_event((key, False))
            if translated_event[0] is not None:
                logging.debug(f"Pynput keyboard release: key={translated_event[0]}")
                self.on_input_event(translated_event)
        except Exception as e:
            logging.error(f"Error handling keyboard release event: {e}")

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        try:
            translated_event = self._translate_key_event((button, pressed))
            logging.debug(f"Pynput mouse click: button={translated_event[0]}, pressed={pressed}")
            self.on_input_event(translated_event)
        except Exception as e:
            logging.error(f"Error handling mouse click event: {e}")

    def _create_key_map(self):
        """Create a mapping from pynput keys to our internal KeyCode enum."""
        try:
            return {
                # Modifier keys
                self.keyboard.Key.ctrl_l: KeyCode.CTRL_LEFT,
                self.keyboard.Key.ctrl_r: KeyCode.CTRL_RIGHT,
                self.keyboard.Key.shift_l: KeyCode.SHIFT_LEFT,
                self.keyboard.Key.shift_r: KeyCode.SHIFT_RIGHT,
                self.keyboard.Key.alt_l: KeyCode.ALT_LEFT,
                self.keyboard.Key.alt_r: KeyCode.ALT_RIGHT,
                self.keyboard.Key.cmd_l: KeyCode.META_LEFT,
                self.keyboard.Key.cmd_r: KeyCode.META_RIGHT,

                # Function keys
                self.keyboard.Key.f1: KeyCode.F1,
                self.keyboard.Key.f2: KeyCode.F2,
                self.keyboard.Key.f3: KeyCode.F3,
                self.keyboard.Key.f4: KeyCode.F4,
                self.keyboard.Key.f5: KeyCode.F5,
                self.keyboard.Key.f6: KeyCode.F6,
                self.keyboard.Key.f7: KeyCode.F7,
                self.keyboard.Key.f8: KeyCode.F8,
                self.keyboard.Key.f9: KeyCode.F9,
                self.keyboard.Key.f10: KeyCode.F10,
                self.keyboard.Key.f11: KeyCode.F11,
                self.keyboard.Key.f12: KeyCode.F12,
                self.keyboard.Key.f13: KeyCode.F13,
                self.keyboard.Key.f14: KeyCode.F14,
                self.keyboard.Key.f15: KeyCode.F15,
                self.keyboard.Key.f16: KeyCode.F16,
                self.keyboard.Key.f17: KeyCode.F17,
                self.keyboard.Key.f18: KeyCode.F18,
                self.keyboard.Key.f19: KeyCode.F19,
                self.keyboard.Key.f20: KeyCode.F20,

                # Number keys
                self.keyboard.KeyCode.from_char('1'): KeyCode.ONE,
                self.keyboard.KeyCode.from_char('2'): KeyCode.TWO,
                self.keyboard.KeyCode.from_char('3'): KeyCode.THREE,
                self.keyboard.KeyCode.from_char('4'): KeyCode.FOUR,
                self.keyboard.KeyCode.from_char('5'): KeyCode.FIVE,
                self.keyboard.KeyCode.from_char('6'): KeyCode.SIX,
                self.keyboard.KeyCode.from_char('7'): KeyCode.SEVEN,
                self.keyboard.KeyCode.from_char('8'): KeyCode.EIGHT,
                self.keyboard.KeyCode.from_char('9'): KeyCode.NINE,
                self.keyboard.KeyCode.from_char('0'): KeyCode.ZERO,

                # Letter keys
                self.keyboard.KeyCode.from_char('a'): KeyCode.A,
                self.keyboard.KeyCode.from_char('b'): KeyCode.B,
                self.keyboard.KeyCode.from_char('c'): KeyCode.C,
                self.keyboard.KeyCode.from_char('d'): KeyCode.D,
                self.keyboard.KeyCode.from_char('e'): KeyCode.E,
                self.keyboard.KeyCode.from_char('f'): KeyCode.F,
                self.keyboard.KeyCode.from_char('g'): KeyCode.G,
                self.keyboard.KeyCode.from_char('h'): KeyCode.H,
                self.keyboard.KeyCode.from_char('i'): KeyCode.I,
                self.keyboard.KeyCode.from_char('j'): KeyCode.J,
                self.keyboard.KeyCode.from_char('k'): KeyCode.K,
                self.keyboard.KeyCode.from_char('l'): KeyCode.L,
                self.keyboard.KeyCode.from_char('m'): KeyCode.M,
                self.keyboard.KeyCode.from_char('n'): KeyCode.N,
                self.keyboard.KeyCode.from_char('o'): KeyCode.O,
                self.keyboard.KeyCode.from_char('p'): KeyCode.P,
                self.keyboard.KeyCode.from_char('q'): KeyCode.Q,
                self.keyboard.KeyCode.from_char('r'): KeyCode.R,
                self.keyboard.KeyCode.from_char('s'): KeyCode.S,
                self.keyboard.KeyCode.from_char('t'): KeyCode.T,
                self.keyboard.KeyCode.from_char('u'): KeyCode.U,
                self.keyboard.KeyCode.from_char('v'): KeyCode.V,
                self.keyboard.KeyCode.from_char('w'): KeyCode.W,
                self.keyboard.KeyCode.from_char('x'): KeyCode.X,
                self.keyboard.KeyCode.from_char('y'): KeyCode.Y,
                self.keyboard.KeyCode.from_char('z'): KeyCode.Z,

                # Special keys
                self.keyboard.Key.space: KeyCode.SPACE,
                self.keyboard.Key.enter: KeyCode.ENTER,
                self.keyboard.Key.tab: KeyCode.TAB,
                self.keyboard.Key.backspace: KeyCode.BACKSPACE,
                self.keyboard.Key.esc: KeyCode.ESC,
                self.keyboard.Key.insert: KeyCode.INSERT,
                self.keyboard.Key.delete: KeyCode.DELETE,
                self.keyboard.Key.home: KeyCode.HOME,
                self.keyboard.Key.end: KeyCode.END,
                self.keyboard.Key.page_up: KeyCode.PAGE_UP,
                self.keyboard.Key.page_down: KeyCode.PAGE_DOWN,
                self.keyboard.Key.caps_lock: KeyCode.CAPS_LOCK,
                self.keyboard.Key.num_lock: KeyCode.NUM_LOCK,
                self.keyboard.Key.scroll_lock: KeyCode.SCROLL_LOCK,
                self.keyboard.Key.pause: KeyCode.PAUSE,
                self.keyboard.Key.print_screen: KeyCode.PRINT_SCREEN,

                # Arrow keys
                self.keyboard.Key.up: KeyCode.UP,
                self.keyboard.Key.down: KeyCode.DOWN,
                self.keyboard.Key.left: KeyCode.LEFT,
                self.keyboard.Key.right: KeyCode.RIGHT,

                # Numpad keys
                self.keyboard.Key.num_lock: KeyCode.NUM_LOCK,
                self.keyboard.KeyCode.from_vk(96): KeyCode.NUMPAD_0,
                self.keyboard.KeyCode.from_vk(97): KeyCode.NUMPAD_1,
                self.keyboard.KeyCode.from_vk(98): KeyCode.NUMPAD_2,
                self.keyboard.KeyCode.from_vk(99): KeyCode.NUMPAD_3,
                self.keyboard.KeyCode.from_vk(100): KeyCode.NUMPAD_4,
                self.keyboard.KeyCode.from_vk(101): KeyCode.NUMPAD_5,
                self.keyboard.KeyCode.from_vk(102): KeyCode.NUMPAD_6,
                self.keyboard.KeyCode.from_vk(103): KeyCode.NUMPAD_7,
                self.keyboard.KeyCode.from_vk(104): KeyCode.NUMPAD_8,
                self.keyboard.KeyCode.from_vk(105): KeyCode.NUMPAD_9,
                self.keyboard.KeyCode.from_vk(107): KeyCode.NUMPAD_ADD,
                self.keyboard.KeyCode.from_vk(109): KeyCode.NUMPAD_SUBTRACT,
                self.keyboard.KeyCode.from_vk(106): KeyCode.NUMPAD_MULTIPLY,
                self.keyboard.KeyCode.from_vk(111): KeyCode.NUMPAD_DIVIDE,
                self.keyboard.KeyCode.from_vk(110): KeyCode.NUMPAD_DECIMAL,

                # Additional special characters
                self.keyboard.KeyCode.from_char('-'): KeyCode.MINUS,
                self.keyboard.KeyCode.from_char('='): KeyCode.EQUALS,
                self.keyboard.KeyCode.from_char('['): KeyCode.LEFT_BRACKET,
                self.keyboard.KeyCode.from_char(']'): KeyCode.RIGHT_BRACKET,
                self.keyboard.KeyCode.from_char(';'): KeyCode.SEMICOLON,
                self.keyboard.KeyCode.from_char("'"): KeyCode.QUOTE,
                self.keyboard.KeyCode.from_char('`'): KeyCode.BACKQUOTE,
                self.keyboard.KeyCode.from_char('\\'): KeyCode.BACKSLASH,
                self.keyboard.KeyCode.from_char(','): KeyCode.COMMA,
                self.keyboard.KeyCode.from_char('.'): KeyCode.PERIOD,
                self.keyboard.KeyCode.from_char('/'): KeyCode.SLASH,

                # Media keys
                self.keyboard.Key.media_volume_mute: KeyCode.MUTE,
                self.keyboard.Key.media_volume_down: KeyCode.VOLUME_DOWN,
                self.keyboard.Key.media_volume_up: KeyCode.VOLUME_UP,
                self.keyboard.Key.media_play_pause: KeyCode.PLAY_PAUSE,
                self.keyboard.Key.media_next: KeyCode.NEXT_TRACK,
                self.keyboard.Key.media_previous: KeyCode.PREV_TRACK,

                # Mouse buttons
                self.mouse.Button.left: KeyCode.MOUSE_LEFT,
                self.mouse.Button.right: KeyCode.MOUSE_RIGHT,
                self.mouse.Button.middle: KeyCode.MOUSE_MIDDLE,
            }
        except Exception as e:
            logging.error(f"Error creating key map: {e}")
            return {}

    def on_input_event(self, event):
        """
        Callback method to be set by the KeyListener.
        This method is called for each processed input event.
        """
        try:
            pass
        except Exception as e:
            logging.error(f"Error in on_input_event: {e}")
