import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent  # Data files are in e:\CalAI
DB_PATH = BASE_DIR / "parcelpilot.db"
INDEX_PATH = BASE_DIR / "retrieval" / "bm25_index.pkl"
DOC_CHUNKS_PATH = BASE_DIR / "retrieval" / "doc_chunks.pkl"

# Snapshot time from README for reference
DATASET_SNAPSHOT_TIME = "2026-08-16 11:00 Asia/Kolkata"
