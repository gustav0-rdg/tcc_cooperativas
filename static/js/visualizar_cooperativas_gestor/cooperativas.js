let paginaAtual = 1;
let totalCooperativas = 0;
let totalExibido = 0;
let filtrosAtivos = {};
const itemsPorPagina = 10;
let cooperativaModalInstance = null; 

document.addEventListener('DOMContentLoaded', function() {
    inicializarEstadoDosFiltros();

    const modalEl = document.getElementById('cooperativaModal');
    if (modalEl) {
        cooperativaModalInstance = new bootstrap.Modal(modalEl);
    }

    inicializarEventos();
    
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    totalExibido = parseInt(loadMoreBtn.dataset.totalExibido || 0);
    totalCooperativas = parseInt(loadMoreBtn.dataset.totalGeral || 0);
    atualizarBotaoCarregarMais();
});

function inicializarEstadoDosFiltros() {
    const params = new URLSearchParams(window.location.search);
    filtrosAtivos = {
        q: params.get('q') || '',
        status: params.get('status') || null,
        atividade: params.get('atividade') || null
    };
    if (filtrosAtivos.q) {
        document.getElementById('searchInput').value = filtrosAtivos.q;
    }
    atualizarTagsFiltros();
}

function inicializarEventos() {
    const container = document.getElementById('cooperativasContainer');

    container.addEventListener('click', function(e) {
        const blockButton = e.target.closest('.btn-block');
        const card = e.target.closest('.coop-card');

        if (blockButton) {
            e.preventDefault(); 
            toggleBloqueioCooperativa(blockButton); 
            return; 
        } 
        
        if (card) {
            
            // Preenche o modal
            preencherModalDetalhes(card); 
            
            if (cooperativaModalInstance) {
                cooperativaModalInstance.show();
            }
        }
    });

    const searchForm = document.getElementById('searchForm');
    searchForm.addEventListener('submit', handleSearch);

    const filterItems = document.querySelectorAll('.filter-item');
    filterItems.forEach(item => {
        item.addEventListener('click', handleFilter);
    });

    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.addEventListener('click', carregarMais);
}

function preencherModalDetalhes(cardElement) {
    const coop = cardElement.dataset;
    if (!coop) return;

    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalBody.innerHTML = '<div class="spinner-border text-success" role="status"><span class="visually-hidden">Carregando...</span></div>';
    modalTitle.textContent = coop.nome;

    const statusMap = {
        'aprovado': 'Aprovado',
        'aguardando': 'Aguardando Aprovação',
        'bloqueado': 'Bloqueado'
    };
    const statusText = statusMap[coop.status] || 'Indefinido';
    const statusClass = `status-${coop.status}`;

    const isAtivo = (coop.ativo === 'true' || coop.ativo === 'True');
    const activityText = isAtivo ? 'Ativo (últimos 2 meses)' : 'Inativo (mais de 2 meses)';
    const activityColor = isAtivo ? 'var(--verde-principal)' : 'var(--vermelho)';

    modalBody.innerHTML = `
        <div class="detail-section">
            <h6 class="detail-title">Informações Gerais</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">CNPJ</span>
                    <span class="detail-value">${coop.cnpj}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Status</span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Data de Cadastro</span>
                    <span class="detail-value">${coop.dataCadastro}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Último Acesso</span>
                    <span class="detail-value">${coop.ultimoAcesso}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Atividade</span>
                    <span class="detail-value" style="color: ${activityColor}; font-weight: 700;">
                        ${activityText}
                    </span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Contato</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Telefone</span>
                    <span class="detail-value">${coop.telefone}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Email</span>
                    <span class="detail-value">${coop.email}</span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Endereço</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Logradouro</span>
                    <span class="detail-value">${coop.endereco}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Cidade/Estado</span>
                    <span class="detail-value">${coop.cidade} - ${coop.estado}</span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Estatísticas</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Total de Vendas</span>
                    <span class="detail-value">${coop.totalVendas} vendas registradas</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Materiais Vendidos</span>
                    <span class="detail-value">${parseFloat(coop.materiaisVendidos).toLocaleString('pt-BR')} kg</span>
                </div>
            </div>
        </div>
    `;
}

function toggleBloqueioCooperativa(buttonElement) {
    const userId = buttonElement.dataset.userId;
    const coopNome = buttonElement.dataset.coopNome;
    const acao = buttonElement.dataset.acao;

    const titulo = acao === 'bloquear' ? 'Bloquear Cooperativa' : 'Desbloquear Cooperativa';
    const texto = acao === 'bloquear' 
        ? `Tem certeza que deseja bloquear o acesso de <strong>${coopNome}</strong>?`
        : `Tem certeza que deseja desbloquear o acesso de <strong>${coopNome}</strong>?`;
    const confirmButtonText = acao === 'bloquear' ? 'Sim, bloquear' : 'Sim, desbloquear';
    const icon = acao === 'bloquear' ? 'warning' : 'question';
    const confirmButtonColor = acao === 'bloquear' ? 'var(--vermelho)' : 'var(--verde-principal)';

    Swal.fire({
        title: titulo,
        html: texto,
        icon: icon,
        showCancelButton: true,
        confirmButtonColor: confirmButtonColor,
        cancelButtonColor: '#6c757d',
        confirmButtonText: confirmButtonText,
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    }).then((result) => {

        if (result.isConfirmed) {
            
            const url = `/api/usuarios/alterar-status/${userId}`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': localStorage.getItem('session_token')
                },
                body: {
                    'novo-status': (acao === 'bloquear' ? 'bloqueado' : 'ativo')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'Sucesso!',
                        text: data.message || 'Ação realizada com sucesso.',
                        icon: 'success',
                        confirmButtonColor: 'var(--verde-principal)',
                        confirmButtonText: 'OK'
                    }).then(() => {
                        location.reload(); 
                    });
                } else {
                    throw new Error(data.message || 'Erro ao realizar a ação.');
                }
            })
            .catch(error => {
                Swal.fire(
                    'Erro!',
                    error.message || 'Não foi possível completar a ação.',
                    'error'
                );
            });
        }
    });
}

async function carregarMais() {
    paginaAtual++;
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    loadMoreBtn.disabled = true;
    loadMoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Carregando...';

    const params = new URLSearchParams(window.location.search);
    params.set('page', paginaAtual);
    
    const url = `/gestores/cooperativas/load?${params.toString()}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro ao carregar mais cooperativas.');

        const newCardsHtml = await response.text();
        
        if (newCardsHtml.trim() === "") {
            totalCooperativas = totalExibido;
            loadMoreBtn.style.display = 'none';
        } else {
            const container = document.getElementById('cooperativasContainer');
            container.insertAdjacentHTML('beforeend', newCardsHtml);
            
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = newCardsHtml;
            const novosCardsCount = tempDiv.children.length;
            totalExibido += novosCardsCount;
            
            loadMoreBtn.disabled = false;
            loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Carregar mais cooperativas';
        }

    } catch (error) {
        console.error(error);
        loadMoreBtn.innerHTML = 'Erro ao carregar';
    } finally {
        atualizarContador();
        atualizarBotaoCarregarMais();
    }
}

function handleSearch(e) {
    e.preventDefault();
    const searchTerm = document.getElementById('searchInput').value;
    const params = new URLSearchParams(window.location.search);

    if (searchTerm.trim()) {
        params.set('q', searchTerm.trim());
    } else {
        params.delete('q');
    }
    params.delete('page');
    window.location.search = params.toString();
}

function handleFilter(e) {
    e.preventDefault();
    const filterType = e.currentTarget.dataset.filter;
    const filterValue = e.currentTarget.dataset.value;
    const params = new URLSearchParams(window.location.search);

    if (filterValue === 'todos') {
        params.delete(filterType);
    } else {
        params.set(filterType, filterValue);
    }
    params.delete('page');
    window.location.search = params.toString();
}

function removerFiltro(tipo) {
    const params = new URLSearchParams(window.location.search);
    params.delete(tipo);
    params.delete('page');
    window.location.search = params.toString();
}

function atualizarContador() {
    const counter = document.getElementById('resultsCount');
    if (counter) {
        counter.textContent = `Mostrando ${totalExibido} de ${totalCooperativas} cooperativa${totalCooperativas !== 1 ? 's' : ''}`;
    }
}

function atualizarBotaoCarregarMais() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (totalExibido >= totalCooperativas) {
        loadMoreBtn.style.display = 'none';
    } else {
        loadMoreBtn.style.display = 'inline-block';
    }
}

function atualizarTagsFiltros() {
    const container = document.getElementById('activeFilters');
    container.innerHTML = '';

    if (filtrosAtivos.status) {
        const statusText = {
            'aprovado': 'Aprovados',
            'aguardando': 'Aguardando',
            'bloqueado': 'Bloqueados'
        }[filtrosAtivos.status];

        container.innerHTML += `
            <span class="filter-tag">
                ${statusText}
                <i class="fas fa-times remove-filter" onclick="removerFiltro('status')"></i>
            </span>
        `;
    }

    if (filtrosAtivos.atividade) {
        const atividadeText = filtrosAtivos.atividade === 'ativo' ? 'Ativos' : 'Inativos';
        container.innerHTML += `
            <span class="filter-tag">
                ${atividadeText}
                <i class="fas fa-times remove-filter" onclick="removerFiltro('atividade')"></i>
            </span>
        `;
    }
}