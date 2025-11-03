import yt_dlp
from pathlib import Path
from typing import Dict, Any, Optional
import time
import random

from app.utils.config_utils import DownloadConfig
from app.utils.file_utils import FileUtils

class BaseDownloadService:
    def __init__(self):
        self.config = DownloadConfig()
        self.file_utils = FileUtils()

    def obter_info_video(self, url: str) -> Optional[Dict[str, Any]]:
        """Obtém metadados do vídeo"""
        try:
            opts = {
                'quiet': True,
                'no_warnings': False,
                'ignoreerrors': True,
                'extract_flat': False,
            }
            opts.update(self.config.get_base_ydl_opts(Path(".")))
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'titulo': info.get('title', 'N/A'),
                    'duracao': info.get('duration', 0),
                    'canal': info.get('uploader', 'N/A'),
                    'visualizacoes': info.get('view_count', 0),
                    'data_upload': info.get('upload_date', 'N/A'),
                    'thumbnail': info.get('thumbnail', 'N/A'),
                    'descricao': info.get('description', '')[:500] + '...' if info.get('description') else 'N/A'
                }
        except Exception as e:
            raise Exception(f"Erro ao obter informações: {str(e)}")