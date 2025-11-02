from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.utils.downloader import Downloader

router = APIRouter(tags=["playlist"])

class PlaylistRequest(BaseModel):
    url: str
    pasta_destino: str = "downloads"
    tipo: str = "video"  # "video" ou "audio"

@router.post("/playlist")
async def download_playlist(request: PlaylistRequest):
    """
    Endpoint para download de playlists
    """
    try:
        downloader = Downloader()
        resultado = downloader.baixar_playlist(
            url=request.url,
            pasta_destino=request.pasta_destino,
            tipo=request.tipo
        )
        return {"status": "sucesso", "dados": resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/playlist/info")
async def obter_info_playlist(url: str):
    """
    Endpoint para obter informações da playlist
    """
    try:
        downloader = Downloader()
        info = downloader.obter_info_playlist(url)
        return {"status": "sucesso", "dados": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))