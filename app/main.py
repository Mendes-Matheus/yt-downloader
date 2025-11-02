from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
from app.routers import video, audio, playlist
from app.utils.downloader import Downloader

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
app.include_router(playlist.router)

@app.get("/", response_class=HTMLResponse)
async def interface_principal(request: Request):
    """
    Interface web principal
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/info")
async def obter_info_video(url: str):
    """
    Endpoint para obter informações do vídeo
    """
    try:
        downloader = Downloader()
        info = downloader.obter_info_video(url)
        return {"status": "sucesso", "dados": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Verificação de dependências ao iniciar
@app.on_event("startup")
async def startup_event():
    try:
        import yt_dlp # verifica dependência em tempo de startup
    except ImportError:
        raise RuntimeError("yt-dlp não está instalado! Execute: pip install yt-dlp")
    # Cria diretórios necessários
    Path("app/static").mkdir(exist_ok=True)
    Path("app/templates").mkdir(exist_ok=True)