"""
WhisperWriter application manager.

This file contains the WhisperWriterAppManager class, which is responsible for
initializing and managing the main components of the application, including
the GUI windows, key listener, and transcription process.
"""

import os
import signal
import sys
import time
import logging
from PyQt5.QtCore import QObject, QProcess
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

from key_listener import KeyListener
from result_thread import ResultThread
from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.status_window import StatusWindow
from transcription import create_local_model
from input_simulation import InputSimulator
from utils import ConfigManager
from audioplayer import AudioPlayer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperWriterAppManager(QObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        try:
            self.setup_signal_handler()
            self.init_windows()
            self.init_components()
            self.create_tray_icon()
            logging.info("WhisperWriterAppManager initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing WhisperWriterAppManager: {e}")
            raise

    def setup_signal_handler(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C) gracefully."""
        print("\nReceived Ctrl+C. Closing WhisperWriter...")
        self.exit_app()

    def init_windows(self):
        self.settings_window = SettingsWindow()
        self.settings_window.settings_closed.connect(self.on_settings_closed)
        self.settings_window.settings_saved.connect(self.restart_app)

        if ConfigManager.config_file_exists():
            self.main_window = MainWindow()
            self.main_window.openSettings.connect(self.settings_window.show)
            self.main_window.startListening.connect(self.start_listening)
            self.main_window.closeApp.connect(self.exit_app)
            self.main_window.show()
        else:
            print('No valid configuration file found. Opening settings window...')
            self.settings_window.show()

    def init_components(self):
        self.input_simulator = InputSimulator()
        self.key_listener = KeyListener()
        self.key_listener.add_callback("on_activate", self.on_activation)
        self.key_listener.add_callback("on_deactivate", self.on_deactivation)

        model_options = ConfigManager.get_config_section('model_options')
        self.local_model = create_local_model() if not model_options.get('use_api') else None

        self.result_thread = None

        if not ConfigManager.get_config_value('misc', 'hide_status_window'):
            self.status_window = StatusWindow()

    def create_tray_icon(self):
        """Create the system tray icon and its context menu."""
        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join('assets', 'ww-logo.png')), self.app)

        tray_menu = QMenu()

        show_action = QAction('WhisperWriter Main Menu', self.app)
        show_action.triggered.connect(self.main_window.show)
        tray_menu.addAction(show_action)

        settings_action = QAction('Open Settings', self.app)
        settings_action.triggered.connect(self.settings_window.show)
        tray_menu.addAction(settings_action)

        exit_action = QAction('Exit', self.app)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def on_settings_closed(self):
        """If settings is closed without saving on first run, initialize the components with default values."""
        if not ConfigManager.config_file_exists():
            QMessageBox.information(
                self.settings_window,
                'Using Default Values',
                'Settings closed without saving. Default values are being used.'
            )
            self.init_components()
            self.main_window = MainWindow()
            self.main_window.openSettings.connect(self.settings_window.show)
            self.main_window.startListening.connect(self.start_listening)
            self.main_window.closeApp.connect(self.exit_app)
            self.main_window.show()

    def start_listening(self):
        """Start listening for the activation key combination."""
        try:
            self.key_listener.start()
            logging.info("Started listening for activation key combination")
        except Exception as e:
            logging.error(f"Error starting key listener: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to start listening: {e}")

    def on_activation(self):
        """Called when the activation key combination is pressed."""
        try:
            logging.info("Activation key combination triggered")
            if self.result_thread and self.result_thread.isRunning():
                recording_mode = ConfigManager.get_config_value('recording_options', 'recording_mode')
                if recording_mode == 'press_to_toggle':
                    logging.info("Stopping recording (press_to_toggle mode)")
                    self.result_thread.stop_recording()
                elif recording_mode == 'continuous':
                    logging.info("Stopping result thread (continuous mode)")
                    self.stop_result_thread()
                return

            logging.info("Starting result thread")
            self.start_result_thread()
        except Exception as e:
            logging.error(f"Error handling activation: {e}")

    def on_deactivation(self):
        """Called when the activation key combination is released."""
        recording_mode = ConfigManager.get_config_value('recording_options', 'recording_mode')
        if recording_mode == 'hold_to_record':
            if self.result_thread and self.result_thread.isRunning():
                logging.info("Stopping recording (hold_to_record mode)")
                self.result_thread.stop_recording()

    def start_result_thread(self):
        """Start the result thread to record audio and transcribe it."""
        if self.result_thread and self.result_thread.isRunning():
            return

        self.result_thread = ResultThread(self.local_model)
        if not ConfigManager.get_config_value('misc', 'hide_status_window'):
            self.result_thread.statusSignal.connect(self.status_window.updateStatus)
            self.status_window.closeSignal.connect(self.stop_result_thread)
        self.result_thread.resultSignal.connect(self.on_transcription_complete)
        self.result_thread.start()

    def stop_result_thread(self):
        """Stop the result thread."""
        if self.result_thread and self.result_thread.isRunning():
            self.result_thread.stop()

    def on_transcription_complete(self, result):
        """When the transcription is complete, type the result and start listening for the activation key again."""
        self.input_simulator.typewrite(result)

        if ConfigManager.get_config_value('misc', 'noise_on_completion'):
            AudioPlayer(os.path.join('assets', 'beep.wav')).play(block=True)

        if ConfigManager.get_config_value('recording_options', 'recording_mode') == 'continuous':
            self.start_result_thread()
        else:
            self.key_listener.start()

    def restart_app(self):
        """Restart the application to apply new settings."""
        self.exit_app()
        QProcess.startDetached(sys.executable, sys.argv)

    def exit_app(self):
        """Exit the application."""
        try:
            if hasattr(self, 'key_listener'):
                self.key_listener.stop()
            if hasattr(self, 'input_simulator'):
                self.input_simulator.cleanup()
            self.app.quit()
            logging.info("Application exited")
        except Exception as e:
            logging.error(f"Error exiting application: {e}")
            sys.exit(1)

    def run(self):
        """Run the application."""
        sys.exit(self.app.exec_())