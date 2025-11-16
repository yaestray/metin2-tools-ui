from pathlib import Path
from collections import defaultdict
import json
from typing import List, Dict, Any, Optional

from ..config import ICONS_REPO_PATH


def _load_manifest() -> List[Dict[str, Any]]:
    """
    Читает manifest.json из репозитория иконок и приводит к
    нормализованному виду:
    [
      {"id": "...", "title": "...", "prefix": "..."},
      ...
    ]

    Код максимально терпимый к разным схемам manifest.json.
    """
    manifest_path = ICONS_REPO_PATH / "manifest.json"
    if not manifest_path.is_file():
        return []

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    # если это словарь с ключами "folders" или "groups"
    if isinstance(raw, dict):
        if "folders" in raw and isinstance(raw["folders"], list):
            items = raw["folders"]
        elif "groups" in raw and isinstance(raw["groups"], list):
            items = raw["groups"]
        else:
            # Может быть мапа id -> объект
            items = []
            for k, v in raw.items():
                if isinstance(v, dict):
                    v = dict(v)
                    v.setdefault("id", k)
                    items.append(v)
    elif isinstance(raw, list):
        items = raw
    else:
        return []

    folders: List[Dict[str, Any]] = []
    for itm in items:
        if not isinstance(itm, dict):
            continue

        # пробуем вытащить базовые поля из разных вариантов
        prefix = (
            itm.get("path")
            or itm.get("folder")
            or itm.get("prefix")
            or itm.get("dir")
            or itm.get("name")
        )
        if not prefix:
            continue

        fid = itm.get("id") or prefix
        title = itm.get("title") or itm.get("name") or itm.get("label") or fid

        folders.append(
            {
                "id": str(fid),
                "title": str(title),
                "prefix": str(prefix),
            }
        )

    # убираем дубли по id, сортируем по title
    seen = set()
    norm: List[Dict[str, Any]] = []
    for f in folders:
        if f["id"] in seen:
            continue
        seen.add(f["id"])
        norm.append(f)

    norm.sort(key=lambda x: x["title"].lower())
    return norm


_manifest_folders_cache: Optional[List[Dict[str, Any]]] = None


def get_manifest_folders() -> List[Dict[str, Any]]:
    global _manifest_folders_cache
    if _manifest_folders_cache is None:
        _manifest_folders_cache = _load_manifest()
    return _manifest_folders_cache


def list_icons():
    """
    Собираем иконки, объединяя PNG/TGA по имени.
    """
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


def paginated_icons(all_icons, page: int = 1, page_size: int = 60):
    total = len(all_icons)
    if page < 1:
        page = 1
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": all_icons[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size if total else 1,
    }