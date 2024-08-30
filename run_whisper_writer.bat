@echo off
:: This script runs the Whisper Writer program

:: Change to the Whisper Writer project directory
cd C:\Users\nithi\Documents\github\github-mine\whisper-writer

:: Activate the Conda environment named 'py310'
:: The 'call' command ensures the script continues after activating the environment
call conda activate py310

:: Run the Python script 'run.py'
python run.py

:: Pause to keep the console window open, allowing you to see any output or errors
pause

:: Note: If you move your Whisper Writer project, update the path in the 'cd' command above