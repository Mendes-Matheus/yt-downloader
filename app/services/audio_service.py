import time
import random
from pathlib import Path
from typing import Dict, Any

import yt_dlp

from app.services.download_service import BaseDownloadService

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

        temp_basename = f"temp_{int(time.time())}"
        temp_mp3_path = self.audio_temp_dir / f"{temp_basename}.mp3"

        opcoes = self._configurar_opcoes_audio(self.audio_temp_dir)
        opcoes['outtmpl'] = str(self.audio_temp_dir / f"{temp_basename}.%(ext)s")
        
        try:
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=True)

                if not temp_mp3_path.exists():
                    raise Exception("Arquivo MP3 temporario nao foi criado")

                final_filename = f"{self.file_utils.sanitize_filename(info['title'])}.mp3"
                final_filepath = self.audio_temp_dir / final_filename

                try:
                    temp_mp3_path.rename(final_filepath)
                except Exception:
                    final_filepath = temp_mp3_path
                    final_filename = temp_mp3_path.name

                if not final_filepath.exists():
                    raise Exception(f"Arquivo final nao existe: {final_filepath}")

                return {
                    'status': 'sucesso',
                    'filepath': str(final_filepath),
                    'filename': final_filename,
                    'titulo': info['title'],
                    'tamanho': final_filepath.stat().st_size
                }
        except Exception as e:
            if temp_mp3_path.exists():
                try:
                    temp_mp3_path.unlink()
                except Exception:
                    pass
            raise Exception(f"Erro no download: {self.formatar_erro_download(e)}")
