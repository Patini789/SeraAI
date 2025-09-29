"""load settings.py
start:
tts
memory
embeddings

"""
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from Python.app import App

running = True

if __name__ == '__main__':
    app = App()
    app.run()
    while running:
        time.sleep(1)