"""
Main application entry point for WhisperWriter.

This file initializes the main application, sets up the GUI, and manages the overall
flow of the program. It coordinates between different components such as the key listener,
transcription, and input simulation.
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from app_manager import WhisperWriterAppManager
from utils import ConfigManager

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join('assets', 'ww-logo.png')))

    ConfigManager.initialize()

    manager = WhisperWriterAppManager(app)
    manager.run()

if __name__ == '__main__':
    main()
