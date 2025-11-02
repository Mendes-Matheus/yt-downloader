from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from app.utils.downloader import Downloader

router = APIRouter(prefix="/download", tags=["audio"])

class AudioRequest(BaseModel):
    url: str

@router.post("/audio")
async def download_audio(request: AudioRequest):
    """
    Endpoint para download de áudio - retorna arquivo para download pelo navegador
    """
    try:
        downloader = Downloader()
        resultado = downloader.baixar_audio_temp(url=request.url)
        
        if resultado['status'] == 'sucesso' and os.path.exists(resultado['filepath']):
            filename = resultado['filename']
            
            return FileResponse(
                path=resultado['filepath'],
                filename=filename,
                media_type='audio/mpeg',
                headers={
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
            )
        else:
            raise Exception("Arquivo não encontrado após download")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))