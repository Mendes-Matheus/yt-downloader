from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from app.models.download_models import DownloadRequest
from app.services.video_service import VideoService

router = APIRouter(prefix="/download", tags=["video"])

@router.post("/video")
async def download_video(request: DownloadRequest):
    """Endpoint para download de vídeos"""
    try:
        video_service = VideoService()
        resultado = video_service.baixar_video_temp(
            url=request.url,
            qualidade=request.qualidade
        )
        
        if resultado['status'] == 'sucesso' and os.path.exists(resultado['filepath']):
            return FileResponse(
                path=resultado['filepath'],
                filename=resultado['filename'],
                media_type='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{resultado["filename"]}"'
                }
            )
        else:
            raise Exception("Arquivo não encontrado após download")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))