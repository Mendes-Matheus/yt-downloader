import yt_dlp
from pathlib import Path
from typing import Dict, Any, Optional, List
import random
import time
import tempfile
import os

class Downloader:
    def __init__(self, pasta_base: str = "downloads"):
        self.pasta_base = Path(pasta_base)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]

        self.temp_dir = Path(tempfile.gettempdir()) / "yt_downloader"
        self.temp_dir.mkdir(exist_ok=True)

    def _get_ydl_opts_base(self, pasta: Path) -> Dict:
        """
        Configurações base com headers e opções de rede
        """
        return {
            'outtmpl': str(pasta / '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            # Headers para evitar bloqueio
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Connection': 'keep-alive',
            },
            # Opções de rede
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'continue_dl': True,
            # Throttling para evitar rate limiting
            'ratelimit': 1048576,  # 1 MB/s
            'throttledratelimit': 524288,  # 512 KB/s
            # Extrator alternativo
            'extractor_retries': 3,
        }

    def baixar_video_temp(self, url: str, qualidade: str = "720p") -> Dict[str, Any]:
        """Baixa vídeo para arquivo temporário com nome FIXO"""
        pasta_temp = self.temp_dir / "videos"
        pasta_temp.mkdir(exist_ok=True)
        
        # Nome temporário FIXO (sem caracteres especiais)
        temp_filename = f"temp_{int(time.time())}.mp4"
        temp_filepath = pasta_temp / temp_filename
        
        opcoes = self._configurar_opcoes_video(qualidade, pasta_temp)
        
        # SOBRESCREVER para usar nome temporário
        opcoes['outtmpl'] = str(temp_filepath)
        
        try:
            print(f"DEBUG - Baixando para arquivo temporário: {temp_filepath}")
            
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not temp_filepath.exists():
                    raise Exception("Arquivo temporário não foi criado")
                
                # Gerar nome FINAL sanitizado
                final_filename = f"{self._sanitize_filename(info['title'])}.mp4"
                final_filepath = pasta_temp / final_filename
                
                print(f"DEBUG - Tentando renomear: {temp_filepath} -> {final_filepath}")
                
                # Renomear o arquivo
                try:
                    temp_filepath.rename(final_filepath)
                    print(f"DEBUG - Arquivo renomeado com sucesso!")
                except Exception as rename_error:
                    print(f"DEBUG - Erro ao renomear: {rename_error}. Usando nome temporário.")
                    final_filepath = temp_filepath
                    final_filename = temp_filename
                
                # Verificação final
                if not final_filepath.exists():
                    raise Exception(f"Arquivo final não existe: {final_filepath}")
                
                file_size = final_filepath.stat().st_size
                print(f"DEBUG - Arquivo final: {final_filepath} ({file_size} bytes)")
                
                return {
                    'status': 'sucesso',
                    'filepath': str(final_filepath),
                    'filename': final_filename,
                    'titulo': info['title'],
                    'tamanho': file_size
                }
                
        except Exception as e:
            # Limpeza em caso de erro
            if temp_filepath.exists():
                try:
                    temp_filepath.unlink()
                except:
                    pass
            raise Exception(f"Erro no download: {str(e)}")

    def baixar_audio_temp(self, url: str) -> Dict[str, Any]:
        """
        Baixa áudio para arquivo temporário e retorna caminho
        """
        pasta_temp = self.temp_dir / "audios"
        pasta_temp.mkdir(exist_ok=True)
        
        opcoes = self._configurar_opcoes_audio(pasta_temp)
        
        try:
            time.sleep(random.uniform(1, 3))
            
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = f"{self._sanitize_filename(info['title'])}.mp3"
                filepath = pasta_temp / filename
                
                return {
                    'status': 'sucesso',
                    'filepath': str(filepath),
                    'filename': filename,
                    'titulo': info['title'],
                    'tamanho': filepath.stat().st_size if filepath.exists() else 0
                }
        except Exception as e:
            raise Exception(f"Erro no download: {str(e)}")

    # Mantenha os outros métodos existentes (obter_info_video, etc.)
    def obter_info_video(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Obtém metadados do vídeo
        """
        try:
            opts = {
                'quiet': True,
                'no_warnings': False,
                'ignoreerrors': True,
                'extract_flat': False,
            }
            opts.update(self._get_ydl_opts_base(Path(".")))
            
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

    def _configurar_opcoes_video(self, qualidade: str, pasta: Path) -> Dict:
        """
        Configura opções para download de vídeo
        """
        opcoes = self._get_ydl_opts_base(pasta)
        
        format_map = {
            "best": 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            "4K": 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best',
            "1080p": 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best',
            "720p": 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best',
            "480p": 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best',
            "360p": 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best'
        }

        opcoes['format'] = format_map.get(qualidade, qualidade)
        return opcoes

    def _configurar_opcoes_audio(self, pasta: Path) -> Dict:
        """
        Configura opções para download de áudio
        """
        opcoes = self._get_ydl_opts_base(pasta)
        opcoes.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
        return opcoes

    def _sanitize_filename(self, filename: str) -> str:
        """
        Remove TODOS os caracteres problemáticos do nome do arquivo
        """
        if not filename or filename.strip() == "":
            return "video_sem_titulo"
        
        # Lista COMPLETA de caracteres problemáticos
        problematic_chars = [
            '<', '>', ':', '"', '/', '\\', '|', '?', '*',  # Sistema de arquivos
            '‘', '’', '“', '”', '`',                       # Aspas variadas
            '⧸', '∕', '⁄', '¬', '¦',                      # Caracteres especiais
            '…', '–', '—', '~', '^',                      # Pontuação especial
            '\n', '\r', '\t',                             # Controle
            '#', '%', '&', '{', '}', '$',                  # Caracteres de formatação
            '!', '@', '+', '=', '[', ']', ';',             # Caracteres especiais
        ]
        
        # Substituir todos os caracteres problemáticos por underscore
        for char in problematic_chars:
            filename = filename.replace(char, '_')
        
        # Também substituir barras comuns (que podem estar escondidas)
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # Remover espaços múltiplos e trim
        filename = ' '.join(filename.split()).strip()
        
        # Se ficou vazio, usar nome padrão
        if not filename:
            filename = "video_sem_titulo"
        
        # Garantir que não comece ou termine com ponto ou espaço
        filename = filename.strip('. ')
        
        # Limitar tamanho
        if len(filename) > 150:
            filename = filename[:147] + "..."
        
        print(f"DEBUG - Nome sanitizado: '{filename}'")
        return filename
    

    def limpar_arquivos_temp(self, idade_maxima_minutos: int = 60):
        """
        Limpa arquivos temporários antigos
        """
        agora = time.time()
        for arquivo in self.temp_dir.rglob('*'):
            if arquivo.is_file():
                if (agora - arquivo.stat().st_mtime) > (idade_maxima_minutos * 60):
                    arquivo.unlink()