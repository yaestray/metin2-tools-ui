from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services import quest_index, icons_index
from .config import ICONS_REPO_PATH

app = FastAPI(title="Metin2 Tools UI")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
##app.mount("/icons", StaticFiles(directory=ICONS_REPO_PATH), name="icons")

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
async def icons_page(
    request: Request,
    folder: str = "",
    q: str = "",
    page: int = Query(1, ge=1),
):
    all_icons = icons_index.list_icons()
    filtered = [
        i for i in all_icons
        if (not folder or (i["folder"] and i["folder"].startswith(folder)))
        and (not q or q.lower() in i["name"].lower())
    ]
    pagination = icons_index.paginated_icons(filtered, page=page, page_size=60)
    return templates.TemplateResponse(
        "icons.html",
        {
            "request": request,
            "icons": pagination["items"],
            "folder": folder,
            "q": q,
            "page": pagination["page"],
            "pages": pagination["pages"],
            "total": pagination["total"],
        },
    )

@app.get("/icons/raw/{path:path}", name="icon_file")
async def icon_file(path: str):
    fp = ICONS_REPO_PATH / path
    if not fp.is_file():
        raise HTTPException(status_code=404, detail="Icon not found")

    ext = fp.suffix.lower()
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".tga":
        # браузер тгу не отображает, но скачивание ок
        media_type = "application/octet-stream"
    else:
        media_type = "application/octet-stream"

    return FileResponse(fp, media_type=media_type, filename=fp.name)

@app.get("/icons/file")
async def icon_file(path: str):
    fp = ICONS_REPO_PATH / path
    if not fp.is_file():
        raise HTTPException(status_code=404, detail="Icon not found")

    ext = fp.suffix.lower()
    if ext == ".png":
        media_type = "image/png"
    elif ext == ".tga":
        # браузеры tga не умеют, но для скачивания норм
        media_type = "application/octet-stream"
    else:
        media_type = "application/octet-stream"

    return FileResponse(fp, media_type=media_type, filename=fp.name)

@app.get("/quests/search", response_class=HTMLResponse)
async def quests_search(request: Request, q: str = Query("", description="Query")):
    tree = quest_index.build_tree()
    results = quest_index.search(q) if q else []
    return templates.TemplateResponse(
        "quests_search.html",
        {
            "request": request,
            "tree": tree,
            "query": q,
            "results": results,
        },
    )
