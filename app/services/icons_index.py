from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional
import json

from ..config import ICONS_REPO_PATH

def _human_title(name) -> str:
    """Берём человекочитаемое название группы."""
    if isinstance(name, dict):
        # локализованный вариант {"ru": "Книги", ...}
        if "ru" in name and isinstance(name["ru"], str):
            return name["ru"]
        for v in name.values():
            if isinstance(v, str):
                return v
        return str(name)
    if name is None:
        return ""
    return str(name)


def _load_manifest() -> List[Dict[str, Any]]:
    """
    Ожидаемый формат:

    {
      "books": {
        "name": {"ru": "Книги"},
        "icons": {
          "27620": {...},
          "30008": {...}
        }
      },
      "food": { ... }
    }

    Превращаем в:

    [
      {
        "id": "books",
        "title": "Книги",
        "items": ["27620", "30008", ...]
      },
      ...
    ]
    """
    manifest_path = ICONS_REPO_PATH / "manifest.json"
    if not manifest_path.is_file():
        return []

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(raw, dict):
        return []

    groups: List[Dict[str, Any]] = []

    for gid, g in raw.items():
        if not isinstance(g, dict):
            continue

        title = _human_title(g.get("name") or g.get("title") or gid)

        icons_obj = g.get("icons") or {}
        if not isinstance(icons_obj, dict):
            icons_obj = {}

        # Ключи icons — это ID, они же имя файла без расширения
        items = sorted(str(icon_id) for icon_id in icons_obj.keys())

        groups.append(
            {
                "id": str(gid),     # "books"
                "title": title,     # "Книги"
                "items": items,     # ["27620", "30008", ...]
            }
        )

    groups.sort(key=lambda x: x["title"].lower())
    return groups


_manifest_folders_cache: Optional[List[Dict[str, Any]]] = None


def get_manifest_folders() -> List[Dict[str, Any]]:
    global _manifest_folders_cache
    if _manifest_folders_cache is None:
        _manifest_folders_cache = _load_manifest()
    return _manifest_folders_cache

def list_icons():
    if not ICONS_REPO_PATH.exists():
        return []

    by_name = defaultdict(
        lambda: {"name": "", "folder": "", "png_path": None, "tga_path": None}
    )

    for fp in ICONS_REPO_PATH.rglob("*"):
        if not fp.is_file():
            continue

        ext = fp.suffix.lower()
        if ext not in [".png", ".tga"]:
            continue

        rel = fp.relative_to(ICONS_REPO_PATH)
        stem = fp.stem
        folder = str(rel.parent) if rel.parent != Path(".") else ""

        item = by_name[stem]
        item["name"] = stem
        item["folder"] = folder

        if ext == ".png":
            item["png_path"] = str(rel)
        elif ext == ".tga":
            item["tga_path"] = str(rel)

    icons = list(by_name.values())
    icons.sort(key=lambda x: x["name"].lower())
    return icons


def paginated_icons(all_icons, page: int, page_size: int = 60):
    total = len(all_icons)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": all_icons[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, (total + page_size - 1) // page_size),
    }