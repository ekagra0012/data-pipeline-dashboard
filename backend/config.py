"""backend/config.py — Centralised configuration."""
import os
import pathlib

# Root of the project (one level above this file)
_PROJECT_ROOT = pathlib.Path(__file__).parent.parent

# DATA_DIR: path to processed CSVs — override via DATA_DIR env var
DATA_DIR = pathlib.Path(os.environ.get("DATA_DIR", str(_PROJECT_ROOT / "data" / "processed")))

# FRONTEND_DIR: path to built React app — override via FRONTEND_DIR env var
FRONTEND_DIR = pathlib.Path(os.environ.get("FRONTEND_DIR", str(_PROJECT_ROOT / "frontend" / "dist")))
