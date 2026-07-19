from pathlib import Path


__version__ = (Path(__file__).parent / ".version").read_text().strip()

__all__ = ['__version__']
