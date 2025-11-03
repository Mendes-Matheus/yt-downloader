// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    configurarEventos();
});

function configurarEventos() {
    // Alternar entre vídeo e áudio
    document.querySelectorAll('input[name="tipo"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('qualidadeContainer').style.display = 
                this.value === 'video' ? 'block' : 'none';
        });
    });

    // Buscar informações ao digitar URL
    document.getElementById('url').addEventListener('blur', function() {
        if (this.value.trim()) {
            buscarInformacoesVideo(this.value);
        }
    });

    // Formulário de download
    document.getElementById('downloadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        iniciarDownload();
    });
}

// Funções de Arquivos
async function carregarArquivos() {
    try {
        const response = await fetch(`/arquivos?pasta=${encodeURIComponent(pastaAtual)}`);
        const data = await response.json();
        renderizarArquivos(data.arquivos);
    } catch (error) {
        console.error('Erro ao carregar arquivos:', error);
    }
}

function renderizarArquivos(arquivos) {
    const container = document.getElementById('arquivosList');
    
    if (arquivos.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhum arquivo baixado</p>';
        return;
    }

    // Ordenar por data de modificação (mais recentes primeiro)
    arquivos.sort((a, b) => b.data_modificacao - a.data_modificacao);
    
    container.innerHTML = arquivos.slice(0, 10).map(arquivo => `
        <div class="mb-2 p-2 border rounded">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-file-${arquivo.nome.endsWith('.mp3') ? 'audio' : 'video'} me-1 text-primary"></i>
                    <small class="d-block">${arquivo.nome}</small>
                </div>
            </div>
            <small class="text-muted">${formatarTamanho(arquivo.tamanho)}</small>
        </div>
    `).join('');
}

function formatarTamanho(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Funções de Download
async function iniciarDownload() {
    const url = document.getElementById('url').value.trim();
    const tipo = document.querySelector('input[name="tipo"]:checked').value;
    const qualidade = document.getElementById('qualidade').value;

    if (!url) {
        mostrarMensagem('error', 'Por favor, insira uma URL do YouTube');
        return;
    }

    mostrarLoading(true);
    mostrarProgresso(true);
    adicionarLog('Iniciando download...');

    try {
        const endpoint = tipo === 'video' ? '/download/video' : '/download/audio';
        const body = {
            url: url,
            ...(tipo === 'video' && { qualidade: qualidade })
        };

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro no download');
        }

        // Extrai o nome do arquivo do header Content-Disposition
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'download.' + (tipo === 'video' ? 'mp4' : 'mp3');
        
        if (contentDisposition) {
            // Tenta diferentes padrões de regex
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(contentDisposition);
            
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
                // Decodifica caracteres especiais se necessário
                filename = decodeURIComponent(filename);
            }
        }

        // Criar blob e fazer download
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

        adicionarLog('Download concluído! O arquivo foi salvo como: ' + filename);
        mostrarMensagem('success', 'Download concluído! Verifique sua pasta de downloads.');
        
    } catch (error) {
        mostrarMensagem('error', 'Erro no download: ' + error.message);
        adicionarLog(`Erro: ${error.message}`);
    } finally {
        mostrarLoading(false);
        setTimeout(() => mostrarProgresso(false), 5000);
    }
}

// Funções de Informações do Vídeo
async function buscarInformacoesVideo(url) {
    try {
        // CORRIGIDO: Mudar de /info?url= para /info/video?url=
        const response = await fetch(`/info/video?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (response.ok) {
            exibirInformacoesVideo(data.dados);
        } else {
            throw new Error(data.detail);
        }
    } catch (error) {
        console.error('Erro ao buscar informações:', error);
        // Opcional: esconder o card de informações em caso de erro
        document.getElementById('videoInfoCard').style.display = 'none';
    }
}

function exibirInformacoesVideo(info) {
    const card = document.getElementById('videoInfoCard');
    const content = document.getElementById('videoInfoContent');
    
    content.innerHTML = `
        <h6>${info.titulo}</h6>
        <p class="mb-1"><strong>Canal:</strong> ${info.canal}</p>
        <p class="mb-1"><strong>Duração:</strong> ${formatarDuracao(info.duracao)}</p>
        <p class="mb-1"><strong>Visualizações:</strong> ${info.visualizacoes?.toLocaleString() || 'N/A'}</p>
        <p class="mb-0"><strong>Upload:</strong> ${info.data_upload}</p>
    `;
    
    card.style.display = 'block';
}

function formatarDuracao(segundos) {
    if (!segundos) return 'N/A';
    
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segs = segundos % 60;

    if (horas > 0) {
        return `${horas}:${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
    } else {
        return `${minutos}:${segs.toString().padStart(2, '0')}`;
    }
}

// Funções de UI
function mostrarLoading(mostrar) {
    document.getElementById('loadingSpinner').style.display = mostrar ? 'block' : 'none';
}

function mostrarProgresso(mostrar) {
    document.getElementById('progressCard').style.display = mostrar ? 'block' : 'none';
    if (mostrar) {
        document.getElementById('logMessages').innerHTML = '';
        atualizarProgresso(0);
    }
}

function atualizarProgresso(percentual) {
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = percentual + '%';
    progressBar.textContent = percentual + '%';
}

function adicionarLog(mensagem) {
    const logContainer = document.getElementById('logMessages');
    const timestamp = new Date().toLocaleTimeString();
    logContainer.innerHTML += `<div>${timestamp} - ${mensagem}</div>`;
    logContainer.scrollTop = logContainer.scrollHeight;
}

function mostrarMensagem(tipo, mensagem) {
    // Implementação simples de notificação
    const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 1000; min-width: 300px;';
    alert.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function atualizarContadorArquivos() {
    const total = pastasDisponiveis.reduce((acc, pasta) => acc + pasta.quantidade_arquivos, 0);
    document.getElementById('totalArquivos').textContent = total;
}