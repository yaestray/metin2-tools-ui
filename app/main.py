from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import quest_index, icons_index
from .config import ICONS_REPO_PATH

app = FastAPI(title="Metin2 Tools UI")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/icons", StaticFiles(directory=ICONS_REPO_PATH), name="icons")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/quests", response_class=HTMLResponse)
async def quests_page(request: Request):
    tree = quest_index.build_tree()
    return templates.TemplateResponse("quests.html",
        {"request": request, "tree": tree, "content_html": None, "current_path": None})

@app.get("/quests/view", response_class=HTMLResponse)
async def quests_view(request: Request, path: str):
    tree = quest_index.build_tree()
    try:
        html = quest_index.get_markdown(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    return templates.TemplateResponse("quests.html",
        {"request": request, "tree": tree, "content_html": html, "current_path": path})

@app.get("/icons", response_class=HTMLResponse)
async def icons_page(request: Request, folder: str = "", q: str = ""):
    all_icons = icons_index.list_icons()
    filtered = [i for i in all_icons if (not folder or i["folder"].startswith(folder)) and (not q or q.lower() in i["name"].lower())]
    return templates.TemplateResponse("icons.html",
        {"request": request, "icons": filtered, "folder": folder, "q": q})
