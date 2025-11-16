from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any, Optional
import json

from ..config import ICONS_REPO_PATH


def _human_title(name) -> str:
    if isinstance(name, dict):
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
    manifest_path = ICONS_REPO_PATH / "manifest.json"
    if not manifest_path.is_file():
        return []

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    groups = []

    if isinstance(raw, dict):
        if isinstance(raw.get("groups"), list):
            groups = raw["groups"]
        elif isinstance(raw.get("folders"), list):
            groups = raw["folders"]
        else:
            tmp = []
            for k, v in raw.items():
                if isinstance(v, dict):
                    g = dict(v)
                    g.setdefault("id", k)
                    tmp.append(g)
            groups = tmp

    elif isinstance(raw, list):
        groups = raw

    else:
        return []

    result = []
    for g in groups:
        if not isinstance(g, dict):
            continue

        gid = g.get("id") or g.get("key") or g.get("slug") or g.get("name")
        if isinstance(gid, dict):
            gid = next(iter(gid.values()), None)
        if not gid:
            continue

        title = _human_title(
            g.get("title") or g.get("label") or g.get("name") or gid
        )

        prefix = (
            g.get("prefix") or g.get("path") or g.get("folder")
            or g.get("dir") or ""
        )
        if prefix is None:
            prefix = ""
        prefix = str(prefix)

        raw_items = (
            g.get("items") or g.get("icons") or g.get("list")
            or g.get("names") or []
        )
        items = []
        if isinstance(raw_items, list):
            for it in raw_items:
                if isinstance(it, dict):
                    nm = it.get("name") or it.get("id") or it.get("icon")
                    if nm:
                        items.append(str(nm))
                elif isinstance(it, str):
                    items.append(it)

        result.append(
            {
                "id": str(gid),
                "title": title,
                "prefix": prefix,
                "items": items,
            }
        )

    seen = set()
    uniq = []
    for g in result:
        if g["id"] in seen:
            continue
        seen.add(g["id"])
        uniq.append(g)

    uniq.sort(key=lambda x: x["title"].lower())
    return uniq


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