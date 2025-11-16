from pathlib import Path
from collections import defaultdict
from ..config import ICONS_REPO_PATH


def list_icons():
    if not ICONS_REPO_PATH.exists():
        return []

    by_name = defaultdict(lambda: {
        "name": "",
        "folder": "",
        "png_path": None,
        "tga_path": None,
    })

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

    # если у иконки вообще нет PNG — можно либо фильтровать, либо оставить (без превью)
    # я предлагаю оставить всё, но сортировать по имени
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