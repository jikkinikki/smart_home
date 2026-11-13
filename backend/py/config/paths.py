from pathlib import Path

# backend/ folder (this file is backend/py/config/paths.py)
BACKEND_DIR = Path(__file__).resolve().parents[2]

JSON_DIR = BACKEND_DIR / "json"
CHANGE_QUE_DIR = BACKEND_DIR / "change_que"
