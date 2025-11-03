from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from app.models.download_models import AudioRequest
from app.services.audio_service import AudioService

router = APIRouter(prefix="/download", tags=["audio"])

@router.post("/audio")
async def download_audio(request: AudioRequest):
    """Endpoint para download de áudio"""
    try:
        audio_service = AudioService()
        resultado = audio_service.baixar_audio_temp(url=request.url)
        
        if resultado['status'] == 'sucesso' and os.path.exists(resultado['filepath']):
            return FileResponse(
                path=resultado['filepath'],
                filename=resultado['filename'],
                media_type='audio/mpeg',
                headers={
                    'Content-Disposition': f'attachment; filename="{resultado["filename"]}"'
                }
            )
        else:
            raise Exception("Arquivo não encontrado após download")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))