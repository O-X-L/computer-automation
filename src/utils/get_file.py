import sys
from pathlib import Path


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = Path(__file__).parent.parent

    p = Path(base_path)
    if not isinstance(relative_path, list):
        relative_path = [relative_path]

    for d in relative_path:
        p = p / d

    return p
