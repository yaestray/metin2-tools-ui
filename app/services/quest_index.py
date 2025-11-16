from pathlib import Path
import markdown
from ..config import QUEST_REPO_PATH

def _scan_dir(base: Path, root: Path):
    out=[]
    for p in sorted(base.iterdir(), key=lambda x:(x.is_file(),x.name.lower())):
        if p.name.startswith('.'): continue
        rel=p.relative_to(root)
        if p.is_dir():
            out.append({"type":"dir","name":p.name,"path":str(rel),"children":_scan_dir(p,root)})
        elif p.suffix.lower() in ['.md','.txt']:
            out.append({"type":"file","name":p.stem,"path":str(rel)})
    return out

def build_tree():
    if not QUEST_REPO_PATH.exists(): return []
    return _scan_dir(QUEST_REPO_PATH, QUEST_REPO_PATH)

def get_markdown(path:str)->str:
    fp = QUEST_REPO_PATH / path
    text = fp.read_text(encoding='utf-8')
    return markdown.markdown(text, extensions=["fenced_code","tables"])
