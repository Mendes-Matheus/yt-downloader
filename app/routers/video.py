from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from app.utils.downloader import Downloader

router = APIRouter(prefix="/download", tags=["video"])

class VideoRequest(BaseModel):
    url: str
    qualidade: str = "720p"

@router.post("/video")
async def download_video(request: VideoRequest):
    """
    Endpoint para download de vídeos - retorna arquivo para download pelo navegador
    """
    try:
        downloader = Downloader()
        resultado = downloader.baixar_video_temp(
            url=request.url,
            qualidade=request.qualidade
        )
        
        if resultado['status'] == 'sucesso' and os.path.exists(resultado['filepath']):
            filename = resultado['filename']
            
            return FileResponse(
                path=resultado['filepath'],
                filename=filename,
                media_type='video/mp4',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
        else:
            raise Exception("Arquivo não encontrado após download")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))