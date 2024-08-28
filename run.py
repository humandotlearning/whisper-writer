"""
Launcher script for WhisperWriter.

This script sets up the environment and launches the main application.
It loads environment variables and runs the main.py script.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

print('Starting WhisperWriter...')
load_dotenv()
subprocess.run([sys.executable, os.path.join('src', 'main.py')])
