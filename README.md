# YouTube Downloader

Aplicação **FastAPI** com interface web para **baixar vídeos e áudios do YouTube**, totalmente **containerizada com Docker**.

---

## 🚀 Funcionalidades

1. Download de **vídeos** em múltiplas resoluções (360p, 480p, 720p, 1080p, 4K)
2. Download de **áudios** em formato MP3
3. Exibição de **informações do vídeo** (título, canal, duração, visualizações, etc.)
4. Interface web simples e responsiva
5. Logs e barra de progresso em tempo real
6. Sanitização automática de nomes de arquivos
7. Persistência de downloads via volume Docker
8. Limpeza automática de arquivos temporários

---

## 🧩 Tecnologias Utilizadas

* **[FastAPI](https://fastapi.tiangolo.com/)** — backend moderno e performático
* **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — extração e download de vídeos
* **[Docker](https://www.docker.com/)** — ambiente isolado e reprodutível
* **[Jinja2](https://jinja.palletsprojects.com/)** — renderização de templates
* **[Bootstrap 5 + JS Vanilla](https://getbootstrap.com/)** — interface web intuitiva
* **[FFmpeg](https://ffmpeg.org/)** — processamento de áudio e vídeo

---

## 📦 Estrutura do Projeto

```
.
├── app/
│   ├── main.py                 # Inicialização do FastAPI e rotas principais
│   ├── routers/
│   │   ├── video.py            # Endpoint para download de vídeos
│   │   ├── audio.py            # Endpoint para download de áudios
│   │   └── playlist.py         # Endpoint para download de playlists
│   ├── utils/
│   │   └── downloader.py       # Classe principal
│   ├── static/
│   │   └── js/
│   │       └── main.js         # Script da interface web
│   └── templates/
│       └── index.html          # Página principal da aplicação
├── downloads/
├── Dockerfile                  
├── docker-compose.yml          
├── requirements.txt            # Dependências Python
└── README.md                   
```

---

## ⚙️ Como Executar com Docker

### 🧱 1️⃣ Construir e iniciar o container

```bash
docker compose up --build
```

Isso irá:

* Criar a imagem
* Instalar dependências (FastAPI, yt-dlp, Jinja2, etc.)
* Configurar o **FFmpeg** para manipulação de áudio/vídeo
* Iniciar o servidor **Uvicorn** na porta **8000**

---

### 🌐 2️⃣ Acessar a aplicação

Abra no navegador:
👉 [http://localhost:8000](http://localhost:8000)

---

## 🔌 Endpoints Disponíveis

| Método | Rota              | Descrição                         |
| ------ | ----------------- | --------------------------------- |
| `GET`  | `/`               | Interface web principal           |
| `GET`  | `/info?url=`      | Obtém informações do vídeo (JSON) |
| `POST` | `/download/video` | Faz o download de um vídeo (MP4)  |
| `POST` | `/download/audio` | Faz o download de um áudio (MP3)  |

---

## 🧰 Exemplo de Uso via cURL

### 🔹 Obter informações do vídeo

```bash
curl "http://localhost:8000/info?url=https://www.youtube.com/watch?v=XXXXX"
```

### 🔹 Fazer download de áudio

```bash
curl -X POST "http://localhost:8000/download/audio" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=XXXXX"}' \
     --output musica.mp3
```

---

## 🧼 Limpeza Automática

O sistema cria arquivos temporários durante o download e possui um método interno (`limpar_arquivos_temp`) que remove arquivos antigos, evitando o acúmulo de lixo no container.

---

## 🧾 Requisitos de Build (para referência)

**Dockerfile** inclui:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl wget
RUN pip install fastapi uvicorn yt-dlp jinja2 pydantic python-multipart
```

---

## 🧑‍💻 Autor

**Matheus Mendes**

**📧 E-Mail:** [mendes.dev95@gmail.com](mailto:mendes.dev95@gmail.com)

---

## 🐳 Comandos Úteis

| Ação                 | Comando                              |
| -------------------- | ------------------------------------ |
| Subir o container    | `docker compose up`                  |
| Parar o container    | `docker compose down`                |
| Reconstruir a imagem | `docker compose up --build`          |
| Acessar o container  | `docker exec -it yt-downloader bash` |
| Verificar logs       | `docker compose logs -f`             |

---
