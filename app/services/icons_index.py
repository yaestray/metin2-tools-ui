from pathlib import Path
from ..config import ICONS_REPO_PATH

def list_icons():
    if not ICONS_REPO_PATH.exists(): return []
    out=[]
    for p in ICONS_REPO_PATH.rglob('*.png'):
        rel=p.relative_to(ICONS_REPO_PATH)
        out.append({"name":p.stem,"path":str(rel),"folder":str(rel.parent) if rel.parent!=Path('.') else ""})
    return out
