from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
QUEST_REPO_PATH = DATA_DIR / "metin2-quest-functions"
ICONS_REPO_PATH = DATA_DIR / "metin2-icons"
