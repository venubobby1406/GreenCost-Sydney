import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from backend.app.rag.store import ingest

if __name__ == "__main__":
    print(ingest("--force" in sys.argv))
