const sessionToken = localStorage.getItem('session_token');

window.CooperativasApp = (function () {
    const API_GET_ALL = '/api/cooperativas/get-all';
    const ITEMS_PER_PAGE = 10;

    let state = {
        all: [],             // Registros da API
        filtered: [],        // Após filtros
        page: 1,
        itemsPerPage: ITEMS_PER_PAGE,
        filtros: { q: null, status: null, atividade: null, aprovacao: null }
    };

    // Elementos DOM
    let el = {
        container: null,
        mostrandoLabel: null,
        totalLabel: null,
        searchForm: null,
        searchInput: null,
        activeFilters: null,
        loadMoreBtn: null,
        modalEl: null
    };

    function safeFormatarCNPJ(cnpj) {
        try {
            const s = String(cnpj || '').replace(/\D/g, '');
            if (s.length !== 14) return String(cnpj || '');
            return s.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
        } catch { return String(cnpj || ''); }
    }

    function toCapitalize(s) {
        if (!s) return '';
        s = String(s);
        return s.charAt(0).toUpperCase() + s.slice(1);
    }

    function formatarTelefone(tel) {
        if (!tel) return '';
        tel = String(tel).replace(/\D/g, '');
        if (tel.length === 11) return tel.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        if (tel.length === 10) return tel.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        return tel;
    }

    function formatarData(input) {
        if (!input) return 'Não registrado';
        const d = new Date(input);
        if (isNaN(d.getTime())) {
            // Timestamp em segundos
            const num = Number(input);
            if (!isNaN(num)) return formatarData(new Date(num * 1000).toString());
            return 'Data inválida';
        }
        const agora = new Date();
        const dia = String(d.getDate()).padStart(2, '0');
        const mes = String(d.getMonth() + 1).padStart(2, '0');
        const ano = d.getFullYear();
        const dataFormatada = `${dia}/${mes}/${ano}`;
        const diffDias = Math.floor((agora - d) / (1000 * 60 * 60 * 24));
        const tempo = diffDias === 0 ? '(Hoje)' : diffDias === 1 ? '(há 1 dia)' : `(há ${diffDias} dias)`;
        return `${dataFormatada} ${tempo}`;
    }

    async function fetchCooperativas() {
        const headers = { 'Content-Type': 'application/json' };
        if (sessionToken) headers['Authorization'] = sessionToken;

        const res = await fetch(API_GET_ALL, { method: 'POST', headers, body: JSON.stringify({}) });

        const ct = res.headers.get('content-type') || '';
        if (!ct.includes('application/json')) {
            const text = await res.text();
            throw new Error(`Resposta inesperada do servidor: ${text.slice(0, 200)}`);
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data?.error || 'Erro ao buscar cooperativas');

        if (Array.isArray(data)) return data;
        if (Array.isArray(data.dados_cooperativas)) return data.dados_cooperativas;
        if (Array.isArray(data)) return data;
        return [];
    }

    function aplicarFiltros(resetPage = true) {
        const q = state.filtros.q;
        const status = state.filtros.status;
        const atividade = state.filtros.atividade;
        const aprovacao = state.filtros.aprovacao;
        
        let arr = [...state.all];
        
        if (q && q.trim()) {
            const termo = q.trim().toLowerCase();
            const numerico = termo.replace(/\D/g, '');
            const usarBuscaCnpj = numerico.length > 0;
        
            arr = arr.filter(coop => {
            const nome = String(coop.razao_social || '').toLowerCase();
            const fantasia = String(coop.nome_fantasia || '').toLowerCase();
        
            const matchNome = nome.includes(termo);
            const matchFantasia = fantasia.includes(termo);
        
            let matchCnpj = false;
            if (usarBuscaCnpj) {
                const cnpjClean = String(coop.cnpj || '').replace(/\D/g, '');
                matchCnpj = cnpjClean.includes(numerico);
            }
        
            return usarBuscaCnpj ? (matchNome || matchFantasia || matchCnpj) : (matchNome || matchFantasia);
            });
        }
        
        if (status && status !== 'todos') {
            arr = arr.filter(coop => String(coop.status) === String(status));
        }
        
        if (atividade && atividade !== 'todos') {
            const agora = new Date();
            arr = arr.filter(coop => {
            if (!coop.ultima_atualizacao) return atividade === 'inativo';
            const ultima = new Date(coop.ultima_atualizacao);
            const dias = (agora - ultima) / (1000 * 60 * 60 * 24);
            return atividade === 'ativo' ? dias <= 60 : dias > 60;
            });
        }
        
        if (aprovacao && aprovacao !== 'todos') {
            arr = arr.filter(coop => {
            const ap = coop.aprovado;
            if (aprovacao === 'true' || aprovacao === 'aprovado') return ap === 1 || ap === true;
            if (aprovacao === 'null' || aprovacao === 'aguardando-aprovacao') return ap === null || ap === undefined;
            if (aprovacao === 'false' || aprovacao === 'reprovado') return ap === 0 || ap === false;
            return true;
            });
        }
        
        state.filtered = arr;
        if (resetPage) state.page = 1;
    }

    function renderCards(sliceArr, append = false) {
        const html = sliceArr.map(coop => {
            const ultimoAcesso = coop.ultima_atualizacao || coop.data_cadastro || '';
            return `
          <div class="col-12 col-md-6 col-xl-4">
            <div class="coop-card"
                 data-id="${coop.id_cooperativa ?? ''}"
                 data-nome="${(coop.razao_social || '').replace(/"/g, '&quot;')}"
                 data-cnpj="${safeFormatarCNPJ(coop.cnpj)}"
                 data-status="${coop.status ?? ''}"
                 data-data-cadastro="${coop.data_cadastro ?? ''}"
                 data-ultimo-acesso="${ultimoAcesso}"
                 data-ativo="${coop.aprovado ? 'Ativo' : 'Inativo'}"
                 data-telefone="${coop.telefone ?? ''}"
                 data-email="${coop.email ?? ''}"
                 data-endereco="${coop.endereco ?? ''}"
                 data-cidade="${coop.cidade ?? ''}"
                 data-estado="${coop.estado ?? ''}"
                 data-total-vendas="${coop.total_vendas ?? 0}"
                 data-materiais-vendidos="${coop.materiais_vendidos}"
            >
              <div class="coop-card-header">
                <div>
                  <h3 class="coop-name">${coop.razao_social ?? ''}</h3>
                  <p class="coop-cnpj">${safeFormatarCNPJ(coop.cnpj)}</p>
                </div>
                <span class="status-badge status-${coop.status ?? ''}">${toCapitalize(coop.status ?? '')}</span>
              </div>
  
              <div class="coop-card-body">
                <div class="coop-info-item"><i class="fa-solid fa-note-sticky"></i><span><strong>${coop.nome_fantasia ?? ''}</strong></span></div>
                <div class="coop-info-item"><i class="fas fa-map-marker-alt"></i><span>${coop.cidade ?? ''} - ${coop.estado ?? ''}</span></div>
                <div class="coop-info-item"><i class="fas fa-phone"></i><span>${formatarTelefone(coop.telefone)}</span></div>
                <div class="coop-info-item"><i class="fas fa-envelope"></i><span>${coop.email ?? ''}</span></div>
              </div>
  
              <div class="coop-card-footer">
                <div class="last-access">
                  <i class="fas fa-clock"></i>
                  <span>Último acesso: ${ultimoAcesso ? formatarData(ultimoAcesso) : 'Não registrado'}</span>
                  <span class="activity-indicator ${coop.aprovado ? 'activity-active' : 'activity-inactive'}" title="${coop.aprovado ? 'Ativo' : 'Inativo'}"></span>
                </div>
                ${coop.status === 'bloqueado'
                    ? `<button class="btn-block btn-block-success" data-user-id="${coop.id_usuario ?? ''}" data-coop-nome="${(coop.razao_social || '').replace(/"/g, '&quot;')}" data-novo-status="ativo"><i class="fas fa-unlock"></i> Desbloquear</button>`
                    : `<button class="btn-block btn-block-danger" data-user-id="${coop.id_usuario ?? ''}" data-coop-nome="${(coop.razao_social || '').replace(/"/g, '&quot;')}" data-novo-status="bloqueado"><i class="fas fa-ban"></i> Bloquear</button>`
                }
              </div>
            </div>
          </div>
        `;
        }).join('\n');

        if (!append) el.container.innerHTML = html;
        else el.container.insertAdjacentHTML('beforeend', html);
    }

    function renderPage(append = false) 
    {
        const perPage = state.itemsPerPage;
        const page = Math.max(1, state.page);
      
        if (append) {
            // Itens novos da página
            const start = (page - 1) * perPage;
            const end = Math.min(page * perPage, state.filtered.length);
            const newSlice = state.filtered.slice(start, end);
            // Sem novos itens
            if (newSlice.length > 0) {
                renderCards(newSlice, true); // append
            }
        } else {
            // Até página X
            const end = Math.min(page * perPage, state.filtered.length);
            const slice = state.filtered.slice(0, end);
            renderCards(slice, false); // replace
        }
      
        updateCounters();
        updateLoadMoreVisibility();
        updateActiveFiltersUI();
    }

    function updateCounters() 
    {
        if (!el.totalLabel || !el.mostrandoLabel) return;
        el.totalLabel.textContent = state.all.length;
        el.mostrandoLabel.textContent = Math.min(state.filtered.length, state.page * state.itemsPerPage);
    }

    function updateLoadMoreVisibility() {
        const shown = state.page * state.itemsPerPage;
        if (shown >= state.filtered.length) {
            el.loadMoreBtn.style.display = 'none';
        } else {
            el.loadMoreBtn.style.display = 'inline-block';
        }
    }

    function updateActiveFiltersUI() {
        const container = el.activeFilters;
        container.innerHTML = '';
        const labels = {
            status: { ativo: 'Ativos', pendente: 'Pendentes', bloqueado: 'Bloqueados' },
            atividade: { ativo: 'Ativos', inativo: 'Inativos' },
            aprovacao: { 'true': 'Aprovados', 'null': 'Aguardando aprovação', 'false': 'Reprovados' }
        };

        Object.keys(state.filtros).forEach(key => {
            const val = state.filtros[key];
            if (val === null || val === '' || val === undefined) return;
            let text = (key === 'q') ? `Busca: "${val}"` : (labels[key] && labels[key][val]) ? labels[key][val] : `${key}: ${val}`;
            container.insertAdjacentHTML('beforeend', `
          <span class="filter-tag">
            ${text}
            <i class="fas fa-times remove-filter" data-remove="${key}" title="Remover filtro"></i>
          </span>
        `);
        });

        // Anexa handlers de remoção
        container.querySelectorAll('.remove-filter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const k = e.currentTarget.dataset.remove;
                removeFilter(k);
            });
        });
    }

    function setFilter(key, value)
    {
        if (key === 'q') {
          value = (typeof value === 'string' && value.trim().length > 0) ? value.trim() : null;
        } else {
          value = (value === 'todos' || value === null || value === '') ? null : value;
        }
      
        state.filtros[key] = value;
        aplicarFiltros(true); // Reseta página
        renderPage();
        updateUrlParams();
    }

    function removeFilter(key)
    {
        setFilter(key, null);
    }

    // Atualiza URL sem recarregar
    function updateUrlParams() {
        const params = new URLSearchParams();
        const f = state.filtros;
        if (f.q) params.set('q', f.q);
        if (f.status) params.set('status', f.status);
        if (f.atividade) params.set('atividade', f.atividade);
        if (f.aprovacao) params.set('aprovacao', f.aprovacao);
        const newUrl = `${location.pathname}?${params.toString()}`;
        history.replaceState({}, '', newUrl);
    }

    function setFiltersFromUrl() {
        const params = new URLSearchParams(location.search);
        state.filtros.q = params.get('q') || null;
        state.filtros.status = params.get('status') || null;
        state.filtros.atividade = params.get('atividade') || null;
        state.filtros.aprovacao = params.get('aprovacao') || null;
    }

    function carregarMais()
    {
        const maxPage = Math.max(1, Math.ceil(state.filtered.length / state.itemsPerPage));

        if (state.page >= maxPage)
        {
            // Última página, esconde botão
            if (el.loadMoreBtn) el.loadMoreBtn.style.display = 'none';
            return;
        }

        state.page++;
        renderPage(true);
    }

    async function toggleBloqueioCooperativa(button) 
    {
        const userId = button.dataset.userId;
        const novoStatus = button.dataset.novoStatus;
        const coopNome = button.dataset.coopNome;

        const titulo = novoStatus === 'bloqueado' ? 'Bloquear cooperativa' : 'Desbloquear Cooperativa';
        const texto = novoStatus === 'bloqueado' ? `Tem certeza que deseja bloquear ${coopNome}?` : `Tem certeza que deseja desbloquear ${coopNome}?`;
        const confirmButtonText = novoStatus === 'bloqueado' ? 'Bloquear' : 'Desbloquear';

        const confirm = await Swal.fire({
            title: titulo,
            html: texto,
            icon: novoStatus === 'bloqueado' ? 'warning' : 'question',
            showCancelButton: true,
            confirmButtonColor: 'var(--verde-claro-medio)',
            confirmButtonText,
            cancelButtonText: 'Cancelar',
            cancelButtonColor: 'var(--vermelho)',  
        });

        if (!confirm.isConfirmed) return;

        try {
            const headers = { 'Content-Type': 'application/json' };
            if (sessionToken) headers['Authorization'] = sessionToken;

            const res = await fetch(`/api/usuarios/alterar-status/${userId}`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ 'novo-status': novoStatus })
            });

            const ct = res.headers.get('content-type') || '';
            const data = ct.includes('application/json') ? await res.json() : null;

            if (!res.ok) {
                throw new Error(data?.error || data?.texto || 'Erro ao alterar status');
            }

            // Atualiza status
            const idxAll = state.all.findIndex(x => String(x.id_usuario) === String(userId));
            if (idxAll !== -1) state.all[idxAll].status = novoStatus;
            else
            {
                // Fallback por id_cooperativa
                const possibleIdCoop = button.closest('.coop-card')?.dataset?.id;
                const idxC = state.all.findIndex(x => String(x.id_cooperativa) === String(possibleIdCoop));
                if (idxC !== -1) state.all[idxC].status = novoStatus;
            }

            // Reaplica filtros sem reset
            aplicarFiltros(false);

            // Índice no array filtrado
            const idxFiltered = state.filtered.findIndex(x =>
            String(x.id_usuario) === String(userId) || String(x.id_cooperativa) === String(button.closest('.coop-card')?.dataset?.id)
            );

            if (idxFiltered !== -1) {
                const itemsPerPage = state.itemsPerPage || ITEMS_PER_PAGE;
                const requiredPage = Math.ceil((idxFiltered + 1) / itemsPerPage) || 1;

                if (requiredPage > state.page) state.page = requiredPage; // Só sobe página
            }

            // Re-renderiza com página ajustada
            renderPage();

            await Swal.fire({ title: 'Sucesso', text: data?.texto || data?.message || 'Status atualizado', icon: 'success' });

        } 
        
        catch (err) 
        {
            console.error(err);
            Swal.fire('Erro', err.message || 'Não foi possível completar a ação', 'error');
        }
    }

    function preencherModalDetalhesFromCard(cardEl) {
        const ds = cardEl.dataset;
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        modalTitle.textContent = ds.nome || 'Detalhes';
        modalBody.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-success" role="status"><span class="visually-hidden">Carregando...</span></div></div>';

        const statusText = toCapitalize(ds.status || 'Indefinido');
        const statusClass = `status-${ds.status}`;

        // Preenche com dataset
        const html = `
        <div class="detail-section">
            <h6 class="detail-title">Informações Gerais</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">CNPJ</span>
                    <span class="detail-value">${ds.cnpj}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Status</span>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Data de Cadastro</span>
                    <span class="detail-value">${formatarData(ds.dataCadastro)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Último Acesso</span>
                    <span class="detail-value">${formatarData(ds.ultimoAcesso)}</span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Contato</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Telefone</span>
                    <span class="detail-value">${formatarTelefone(ds.telefone)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Email</span>
                    <span class="detail-value">${ds.email}</span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Endereço</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Logradouro</span>
                    <span class="detail-value">${ds.endereco}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Cidade/Estado</span>
                    <span class="detail-value">${ds.cidade} - ${ds.estado}</span>
                </div>
            </div>
        </div>

        <div class="detail-section">
            <h6 class="detail-title">Estatísticas</h6>
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Total de Vendas</span>
                    <span class="detail-value"><strong>${ds.totalVendas}</strong> vendas</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Materiais Vendidos</span>
                    <ul class="detail-value list-materiais-vendidos">${

                        ds.materiaisVendidos != 'null'

                        ?
                        
                        // Lista dos Materiais

                        ds.materiaisVendidos.split('|').map(material => {
                            return `<li class="materiais-vendidos-item">${material}</li>`;
                        }).join('')

                        :

                        // Sem vendas registradas
                        'Sem vendas registradas'

                    }</ul>
                </div>
            </div>
        </div>
      `;
        modalBody.innerHTML = html;

        // Mostra modal
        const modalEl = document.getElementById('cooperativaModal');
        if (modalEl) {
            const instance = new bootstrap.Modal(modalEl);
            instance.show();
        }
    }

    function attachDom() {
        el.container = document.getElementById('cooperativasContainer');
        el.mostrandoLabel = document.getElementById('mostrandoCooperativas');
        el.totalLabel = document.getElementById('totalCooperativas');
        el.searchForm = document.getElementById('searchForm');
        el.searchInput = document.getElementById('searchInput');
        el.activeFilters = document.getElementById('activeFilters');
        el.loadMoreBtn = document.getElementById('loadMoreBtn');
        el.modalEl = document.getElementById('cooperativaModal');

        if (!el.container) throw new Error('Elemento #cooperativasContainer não encontrado');
    }

    function bindEvents() {
        // Delegação de cliques
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-block');
            if (btn) {
                e.preventDefault();
                toggleBloqueioCooperativa(btn);
                return;
            }
            const card = e.target.closest('.coop-card');
            if (card) {
                preencherModalDetalhesFromCard(card);
            }
        });

        // Filtros dropdown
        document.querySelectorAll('.filter-item').forEach(elm => {
            elm.addEventListener('click', (ev) => {
                ev.preventDefault();
                const f = ev.currentTarget.dataset.filter;
                const v = ev.currentTarget.dataset.value;
                if (v === 'todos') removeFilter(f);
                else setFilter(f, v);
            });
        });

        // Busca
        if (el.searchForm) {
            el.searchForm.addEventListener('submit', (ev) => {
                ev.preventDefault();
                const val = el.searchInput?.value || '';
                setFilter('q', val || null);
            });
        }

        // Carregar mais
        if (el.loadMoreBtn) {
            el.loadMoreBtn.addEventListener('click', (ev) => {
                ev.preventDefault();
                carregarMais();
            });
        }
    }

    async function loadAndRender() {
        try {
            state.all = await fetchCooperativas();
            setFiltersFromUrl();
            aplicarFiltros();
            renderPage();
        } catch (err) {
            console.error(err);
            el.container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Erro ao carregar cooperativas: ${err.message}</div></div>`;
        }
    }

    async function init() {
        attachDom();
        bindEvents();
        await loadAndRender();
    }

    // Expõe init e handlers
    return { init, setFilter, removeFilter };
})();

// Init automático
document.addEventListener('DOMContentLoaded', () => {

    if (!sessionToken)
    {
        window.location.href = '/';
    }

    if (window.CooperativasApp && typeof window.CooperativasApp.init === 'function') {
        window.CooperativasApp.init();
    }
});  