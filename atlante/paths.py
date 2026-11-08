from pathlib import Path
import os
import sys

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))

def user_dir():
    path = Path(os.environ.get('ATLANTE_DATA_DIR', str(Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'AtlanteFormule')))
    path.mkdir(parents=True, exist_ok=True)
    return path
