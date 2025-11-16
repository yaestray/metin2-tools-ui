from pathlib import Path
import markdown
from ..config import QUEST_REPO_PATH


def _scan_dir(base: Path, root: Path):
    out = []
    for p in sorted(base.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name.startswith('.'):
            continue
        rel = p.relative_to(root)
        if p.is_dir():
            out.append({
                "type": "dir",
                "name": p.name,
                "path": str(rel),
                "children": _scan_dir(p, root),
            })
        elif p.suffix.lower() in [".md", ".txt"]:
            out.append({
                "type": "file",
                "name": p.stem,
                "path": str(rel),
            })
    return out


def build_tree():
    if not QUEST_REPO_PATH.exists():
        return []
    return _scan_dir(QUEST_REPO_PATH, QUEST_REPO_PATH)


def get_markdown(path: str) -> str:
    fp = QUEST_REPO_PATH / path
    text = fp.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=["fenced_code", "tables"])


def search(query: str, limit: int = 50):
    """
    Простейший поиск:
    - по имени файла
    - по содержимому (case-insensitive)
    """
    if not QUEST_REPO_PATH.exists():
        return []

    q = query.lower().strip()
    if not q:
        return []

    results = []
    for fp in QUEST_REPO_PATH.rglob("*"):
        if not fp.is_file():
            continue
        if fp.suffix.lower() not in [".md", ".txt"]:
            continue

        rel = fp.relative_to(QUEST_REPO_PATH)
        name = fp.stem

        # матч по имени
        score = 0
        if q in name.lower():
            score += 2

        # матч по содержимому (первые 4–8KB, чтобы не читать гигабайты)
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        if q in text.lower():
            score += 1

        if score > 0:
            # небольшой сниппет из текста
            idx = text.lower().find(q)
            snippet = ""
            if idx != -1:
                start = max(idx - 40, 0)
                end = min(idx + 40, len(text))
                snippet = text[start:end].replace("\n", " ")
            results.append({
                "path": str(rel),
                "name": name,
                "score": score,
                "snippet": snippet,
            })

    # сортируем по score и имени
    results.sort(key=lambda r: (-r["score"], r["name"].lower()))
    return results[:limit]