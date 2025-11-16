from pathlib import Path, PurePosixPath
from collections import defaultdict
from typing import List, Dict, Any, Optional
import json

from ..config import ICONS_REPO_PATH


def _human_title(name) -> str:
    if isinstance(name, dict):
        # локализованные заголовки вида {"ru": "Книги", "en": "Books"}
        if "ru" in name and isinstance(name["ru"], str):
            return name["ru"]
        for v in name.values():
            if isinstance(v, str):
                return v
        return str(name)
    if name is None:
        return ""
    return str(name)


def _extract_icon_names(obj: Any) -> List[str]:
    """
    Рекурсивно обходит объект группы manifest'а и вытаскивает
    все строки, в которых встречаются *.png / *.tga.
    Возвращает список имён иконок БЕЗ расширения.
    """
    names = set()

    def visit(x: Any):
        if isinstance(x, str):
            for ext in (".png", ".tga"):
                if ext in x:
                    try:
                        stem = PurePosixPath(x).stem
                    except Exception:
                        stem = x.rsplit(ext, 1)[0]
                    if stem:
                        names.add(stem)
        elif isinstance(x, dict):
            for v in x.values():
                visit(v)
        elif isinstance(x, list):
            for v in x:
                visit(v)

    visit(obj)
    return sorted(names)


def _load_manifest() -> List[Dict[str, Any]]:
    """
    Читает manifest.json и превращает его в список групп вида:

    [
      {
        "id": "books",
        "title": "Книги",
        "items": ["icon_book1", "icon_book2", ...]
      },
      ...
    ]

    Не делаем никаких предположений о структуре, кроме того,
    что на верхнем уровне dict {id: group_obj}.
    Внутри group_obj рекурсивно ищем строки с *.png / *.tga.
    """
    manifest_path = ICONS_REPO_PATH / "manifest.json"
    if not manifest_path.is_file():
        return []

    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(raw, dict):
        # если когда-нибудь сделаешь другой формат — можно будет расширить
        return []

    groups: List[Dict[str, Any]] = []

    for gid, g in raw.items():
        if not isinstance(g, dict):
            continue

        title = _human_title(
            g.get("title") or g.get("label") or g.get("name") or gid
        )

        items = _extract_icon_names(g)

        groups.append(
            {
                "id": str(gid),     # то самое "books", "food", ...
                "title": title,     # "Книги", "Еда" и т.п.
                "items": items,     # список stem'ов иконок
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