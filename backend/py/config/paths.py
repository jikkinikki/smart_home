from pathlib import Path

# backend/ folder (this file is backend/py/config/paths.py)
BACKEND_DIR = Path(__file__).resolve().parents[2]

# smart_home/ folder. The tinytuya wizard's files (tinytuya.json, devices.json, snapshot.json) live here.
PROJECT_DIR = BACKEND_DIR.parent

JSON_DIR = BACKEND_DIR / "json"

DATA_DIR = BACKEND_DIR / "data"
DB_PATH = DATA_DIR / "smart_home.db"
