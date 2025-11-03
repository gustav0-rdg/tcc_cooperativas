const listCooperativasContainer = document.getElementById('cooperativasContainer');
const mostrandoCooperativasLabel = document.getElementById('mostrandoCooperativas');
const totalCooperativasLabel = document.getElementById('totalCooperativas');

const session_token = localStorage.getItem('session_token');

//#region Funções de formatações (CNPJ, Capitalize, Data e Telefone)

function formatarCNPJ (cnpj) 
{  
    const cnpjLimpo = cnpj.replace(/\D/g, '');
    if (!cnpj || cnpjLimpo.length !== 14) 
    {
        throw new Error ('CNPJ inválido');
    }

    return cnpjLimpo.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    '$1.$2.$3/$4-$5'
    );
}

function toCapitalize (str)
{
    if (typeof str !== 'string' || str.length === 0) 
    {
        return '';
    }

    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatarData(timestamp) 
{
    const data = new Date(timestamp * 1000);
    const agora = new Date();

    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    const dataFormatada = `${dia}/${mes}/${ano}`;
  
    const diffMs = agora - data;
    const diasAtras = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
    let tempoStr;
    if (diasAtras === 0) tempoStr = '(Hoje)';
    else if (diasAtras === 1) tempoStr = '(há 1 dia)';
    else tempoStr = `(há ${diasAtras} dias)`;
  
    return `${dataFormatada} ${tempoStr}`;
}

function formatarTelefone(telefone) 
{
    telefone = telefone.replace(/\D/g, "");

    if (telefone.length === 11) return telefone.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
    else if (telefone.length === 10) return telefone.replace(/(\d{2})(\d{4})(\d{4})/, "($1) $2-$3");

    return telefone;
}

//#endregion

async function consultarCooperativas ()
{
    const response = await fetch (
        
        '/api/cooperativas/get-all', 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data_request = await response?.json();

    if (!response.ok)
    {
        throw new Error (

            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_request.dados_cooperativas;

}

function renderizarCooperativas (cooperativas)
{
    if (!Array.isArray(cooperativas))
    {
        throw new Error ('Valor inválido de cooperativas');
    }

    const listCooperativasRenderizadas = cooperativas.map((cooperativa) => {

        console.log(cooperativa)

        return `
            <div class="col-12 col-md-6 col-xl-4">

                <!-- Card individual da cooperativa -->
                <div class="coop-card"
                    data-id="${cooperativa.id_cooperativa}"
                    data-nome="${cooperativa.razao_social}"
                    data-cnpj="${formatarCNPJ(cooperativa.cnpj)}"
                    data-status="${cooperativa.status}"
                    data-data-cadastro="${new Date(cooperativa.data_cadastro).getTime() / 1000}"
                    data-ultimo-acesso="${new Date(cooperativa.ultima_atualizacao).getTime() / 1000}"
                    data-ativo="${cooperativa.aprovado ? 'Ativo' : 'Inativo'}"
                    data-telefone="${cooperativa.telefone}"
                    data-email="${cooperativa.email}"
                    data-endereco="${cooperativa.endereco}"
                    data-cidade="${cooperativa.cidade}"
                    data-estado="${cooperativa.estado}"
                    data-total-vendas="${cooperativa.total_vendas}"
                    data-materiais-vendidos="${cooperativa.materiais_vendidos}"
                >
                    
                    <!-- Cabeçalho do card -->
                    <div class="coop-card-header">
                        <div>
                            <h3 class="coop-name">${cooperativa.razao_social}</h3>
                            <p class="coop-cnpj">${formatarCNPJ(cooperativa.cnpj)}</p>
                        </div>
                        <span class="status-badge status-${cooperativa.status}">
                            ${toCapitalize(cooperativa.status)}
                        </span>
                    </div>
                    
                    <!-- Corpo do card com informações básicas -->
                    <div class="coop-card-body">
                        <div class="coop-info-item">
                            <i class="fa-solid fa-note-sticky"></i>
                            <span><strong>${cooperativa.nome_fantasia}</strong></span>
                        </div>
                        <div class="coop-info-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${cooperativa.cidade} - ${cooperativa.estado}</span>
                        </div>
                        <div class="coop-info-item">
                            <i class="fas fa-phone"></i>
                            <span>${formatarTelefone(cooperativa.telefone)}</span>
                        </div>
                        <div class="coop-info-item">
                            <i class="fas fa-envelope"></i>
                            <span>${cooperativa.email}</span>
                        </div>
                    </div>
                    
                    <!-- Rodapé com status de atividade e botão de ação -->
                    <div class="coop-card-footer">
                        <div class="last-access">
                            <i class="fas fa-clock"></i>
                            <span>Último acesso: ${
                                cooperativa.ultima_atualizacao 
                                ? 
                                formatarData(new Date(cooperativa.ultima_atualizacao).getTime() / 1000) 
                                : 
                                'Não registrado'
                            }</span>
                            
                            <!-- Indicador visual de atividade (ativo/inativo) -->
                            <span class="activity-indicator ${cooperativa.aprovado ? 'activity-active' : 'activity-inactive'}" 
                                    title="${cooperativa.aprovado ? 'Ativo' : 'Inativo'}"></span>
                        </div>
                        
                        <!-- Botão de bloqueio ou desbloqueio, conforme status -->
                        ${
                            cooperativa.status == 'bloqueado'
                            ?
                            `
                            <button class="btn-block btn-block-success" 
                                    data-user-id="${cooperativa.id_usuario}" 
                                    data-coop-nome="${cooperativa.razao_social}"
                                    data-novo-status="ativo">
                                <i class="fas fa-unlock"></i> Desbloquear
                            </button>
                            `
                            :
                            `
                            <button class="btn-block btn-block-danger" 
                                    data-user-id="${cooperativa.id_usuario}" 
                                    data-coop-nome="${cooperativa.razao_social}"
                                    data-novo-status="bloqueado">
                                <i class="fas fa-ban"></i> Bloquear
                            </button>
                            `
                        }
                    </div>
                </div>
            </div>
        `

    });

    return listCooperativasRenderizadas;

}

async function exibirCooperativas ()
{
    const data_cooperativas = await consultarCooperativas();

    if (data_cooperativas.length <= 0)
    {
        listCooperativasContainer.innerHTML = `

            <div class="col-12">
                <div class="alert alert-info text-center" style="background: var(--branco); border: 2px solid var(--verde-claro-medio); border-radius: 12px;">
                    <i class="fas fa-info-circle" style="font-size: 2rem; color: var(--verde-principal); margin-bottom: 1rem;"></i>
                    <h5 style="color: var(--verde-escuro);">Nenhuma cooperativa encontrada</h5>
                    <p style="color: var(--cinza-claro); margin-bottom: 0;">Tente ajustar os filtros de pesquisa</p>
                </div>
            </div>
        `;
    }

    else
    {
        const params = new URLSearchParams(window.location.search);
        const termoBusca = params.get('q')?.toLowerCase() || '';
        const status = params.get('status');
        const atividade = params.get('atividade');

        let cooperativasFiltradas = [...data_cooperativas];

        if (termoBusca) 
        {
            cooperativasFiltradas = cooperativasFiltradas.filter(coop => 
                coop.razao_social.toLowerCase().includes(termoBusca) ||
                coop.nome_fantasia.toLowerCase().includes(termoBusca) ||
                coop.cnpj.replace(/\D/g, '').includes(termoBusca.replace(/\D/g, ''))
            );
        }

        // Filtro por Status

        if (status) 
        {
            cooperativasFiltradas = cooperativasFiltradas.filter(coop => 
                coop.status === status
            );
        }

        // Filtro por Atividades

        if (atividade) 
        {
            const agora = new Date();
            cooperativasFiltradas = cooperativasFiltradas.filter(coop => {
                const ultima = new Date(coop.ultima_atualizacao);
                const diasSemAtividade = (agora - ultima) / (1000 * 60 * 60 * 24);

                if (atividade === 'ativo') return diasSemAtividade <= 60;
                if (atividade === 'inativo') return diasSemAtividade > 60 || !coop.ultima_atualizacao;
                return true;
            });
        }

        totalCooperativasLabel.textContent = data_cooperativas.length;
        listCooperativasContainer.innerHTML = renderizarCooperativas(cooperativasFiltradas).join(' ');
    }
}

function handleSearch(e) 
{
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

//#region Filtros

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

function handleFilter(e) 
{
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

function atualizarTagsFiltros() {
    const container = document.getElementById('activeFilters');
    container.innerHTML = '';

    if (filtrosAtivos.status) {
        const statusText = {
            'ativo': 'Ativos',
            'pendente': 'Pendentes',
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

function removerFiltro(tipo) {
    const params = new URLSearchParams(window.location.search);
    params.delete(tipo);
    params.delete('page');
    window.location.search = params.toString();
}

//#endregion

document.addEventListener('DOMContentLoaded', function () {

    inicializarEstadoDosFiltros();

    exibirCooperativas();

}); 