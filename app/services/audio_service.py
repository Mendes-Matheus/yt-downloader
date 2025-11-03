import yt_dlp
from pathlib import Path
from typing import Dict, Any
import time
import random

from app.services.download_service import BaseDownloadService
from app.utils.config_utils import DownloadConfig

class AudioService(BaseDownloadService):
    def __init__(self):
        super().__init__()
        self.audio_temp_dir = self.config.temp_dir / "audios"

    def _configurar_opcoes_audio(self, pasta: Path) -> Dict:
        """Configura opções para download de áudio"""
        opcoes = self.config.get_base_ydl_opts(pasta)
        opcoes.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        return opcoes

    def baixar_audio_temp(self, url: str) -> Dict[str, Any]:
        """Baixa áudio para arquivo temporário"""
        self.audio_temp_dir.mkdir(exist_ok=True)
        
        opcoes = self._configurar_opcoes_audio(self.audio_temp_dir)
        
        try:
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{self.file_utils.sanitize_filename(info['title'])}.mp3"
                filepath = self.audio_temp_dir / filename
                
                return {
                    'status': 'sucesso',
                    'filepath': str(filepath),
                    'filename': filename,
                    'titulo': info['title'],
                    'tamanho': filepath.stat().st_size if filepath.exists() else 0
                }
        except Exception as e:
            raise Exception(f"Erro no download: {str(e)}")