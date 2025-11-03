from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.routers import video, audio, info

app = FastAPI(
    title="YouTube Downloader API",
    description="API para download de vídeos e áudios do YouTube",
    version="1.0.0"
)

# Configurar diretórios estáticos e templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Registrar routers
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(info.router)

@app.get("/", response_class=HTMLResponse)
async def interface_principal(request: Request):
    """Interface web principal"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """Verificação de dependências ao iniciar"""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("yt-dlp não está instalado! Execute: pip install yt-dlp")
    
    # Cria diretórios necessários
    Path("app/static").mkdir(exist_ok=True)
    Path("app/templates").mkdir(exist_ok=True)
    print("✓ Diretórios verificados")