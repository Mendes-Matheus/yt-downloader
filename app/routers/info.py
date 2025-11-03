from fastapi import APIRouter, HTTPException

from app.services.download_service import BaseDownloadService

router = APIRouter(prefix="/info", tags=["info"])

@router.get("/video")
async def obter_info_video(url: str):
    """Endpoint para obter informações do vídeo"""
    try:
        download_service = BaseDownloadService()
        info = download_service.obter_info_video(url)
        return {"status": "sucesso", "dados": info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))