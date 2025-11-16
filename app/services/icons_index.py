from pathlib import Path
from ..config import ICONS_REPO_PATH


def list_icons():
    if not ICONS_REPO_PATH.exists():
        return []
    out = []
    for p in ICONS_REPO_PATH.rglob("*.png"):
        rel = p.relative_to(ICONS_REPO_PATH)
        out.append({
            "name": p.stem,
            "path": str(rel),
            "folder": str(rel.parent) if rel.parent != Path(".") else "",
        })
    # сортировка по имени
    out.sort(key=lambda x: x["name"].lower())
    return out


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