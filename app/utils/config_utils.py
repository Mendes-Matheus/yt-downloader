from pathlib import Path
import tempfile
import random
import os
from typing import Dict

class DownloadConfig:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        self.temp_dir = Path(tempfile.gettempdir()) / "yt_downloader"
        self.temp_dir.mkdir(exist_ok=True)
        self.project_root = Path(__file__).resolve().parents[2]
        self.cookie_file = self._resolve_cookie_file()
        self.js_runtime = (os.getenv("YT_DLP_JS_RUNTIME", "node").strip().lower() or "node")
        self.enable_remote_ejs = os.getenv("YT_DLP_REMOTE_EJS", "1").strip() not in {"0", "false", "False"}
        self.visitor_data = os.getenv("YT_DLP_VISITOR_DATA", "").strip()

    def _resolve_cookie_file(self) -> Path | None:
        cookie_file = os.getenv("YT_DLP_COOKIEFILE")

        if not cookie_file:
            docker_cookie_file = Path("/app/cookies.txt")
            if docker_cookie_file.exists():
                return docker_cookie_file

            local_cookie_file = self.project_root / "cookies.txt"
            return local_cookie_file

        candidate = Path(cookie_file).expanduser()
        if not candidate.is_absolute():
            candidate = self.project_root / candidate
        return candidate

    def has_valid_cookie_file(self) -> bool:
        if not self.cookie_file or not self.cookie_file.exists() or self.cookie_file.stat().st_size <= 0:
            return False

        try:
            lines = self.cookie_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            if not lines or lines[0].strip() != "# Netscape HTTP Cookie File":
                return False

            # YouTube auth requires cookies for youtube domains, not only a generic Netscape header.
            has_youtube_cookie = any(
                ".youtube.com" in line or "youtube.com" in line
                for line in lines
                if line and not line.startswith("#")
            )
            return has_youtube_cookie
        except Exception:
            return False

    def describe_cookie_source(self) -> str:
        if self.cookie_file:
            return f"arquivo de cookies em '{self.cookie_file}'"

        return "nenhuma fonte de cookies configurada"

    def get_base_ydl_opts(self, pasta: Path) -> Dict:
        opts = {
            'outtmpl': str(pasta / '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'http_headers': {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Connection': 'keep-alive',
            },
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'continue_dl': True,
            'ratelimit': 1048576,
            'throttledratelimit': 524288,
            'extractor_retries': 3,
            'js_runtimes': {self.js_runtime: {}},
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            },
        }

        if self.enable_remote_ejs:
            opts['remote_components'] = {'ejs:github'}

        if self.visitor_data:
            opts['extractor_args']['youtube']['visitor_data'] = [self.visitor_data]

        if self.has_valid_cookie_file():
            opts['cookiefile'] = str(self.cookie_file)

        return opts
