// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    // 1. Carrega materiais para o filtro
    carregarMateriaisFiltro();

    // 2. Inicia o carregamento dos compradores
    carregarCompradores();

    // 3. Configura eventos dos filtros
    configurarFiltros();
});

/**
 * Função principal para carregar e renderizar os compradores
 */
async function carregarCompradores(material = '', distancia = '', searchQuery = '') {
    const token = localStorage.getItem('session_token');
    const cardsContainer = document.getElementById('cards-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorDetail = document.getElementById('error-detail');

    if (!token) {
        mostrarErro('Sessão inválida. Faça o login novamente.', 'Token não encontrado.');
        return;
    }

    try {
        // Construir URL com parâmetros de filtro
        let url = '/get/compradores-destaque';
        const params = new URLSearchParams();
        if (material) params.append('material', material);
        if (distancia) params.append('estado', distancia); // Usando estado como proxy para distancia, ajustar se necessário
        if (searchQuery) params.append('search', searchQuery); // Adicionar parâmetro de busca se suportado
        if (params.toString()) url += '?' + params.toString();

        // 2. Chama a nova API de "destaques" com filtros
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.erro || 'Erro ao buscar dados.');
        }

        // 3. Renderiza os cards
        loadingSpinner.classList.add('d-none'); // Esconde o loading
        cardsContainer.innerHTML = ''; // Limpa o container

        if (data.length === 0) {
            cardsContainer.innerHTML = '<p class="text-center fs-5">Nenhum comprador encontrado com os filtros aplicados.</p>';
            return;
        }

        data.forEach(comprador => {
            const card = criarCardComprador(comprador);
            cardsContainer.appendChild(card);
        });

    } catch (err) {
        console.error('Erro em carregarCompradores:', err);
        mostrarErro('Não foi possível carregar os compradores.', err.message);
    }

    // Função interna de ajuda para mostrar erros
    function mostrarErro(mensagem, detalhe) {
        loadingSpinner.classList.add('d-none');
        errorMessage.classList.remove('d-none');
        errorDetail.textContent = detalhe;
    }
}

/**
 * Cria o elemento HTML (card) para um comprador
 * @param {object} comprador - O objeto do comprador vindo da API
 * @returns {HTMLElement} O elemento <div> do card
 */
function criarCardComprador(comprador) {
    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';

    const card = document.createElement('div');
    card.className = 'comprador-card';
    card.setAttribute('data-id', comprador.id_comprador);
    card.setAttribute('data-cnpj', comprador.cnpj);

    // Converte o score (Ex: 4.5) em estrelas
    const scoreHtml = gerarEstrelas(comprador.score_confianca);

    // Formata o preço, se existir
    let precoHtml = '<p class="card-no-price">Nenhum preço registrado recentemente.</p>';
    if (comprador.preco_min_kg && comprador.preco_max_kg && comprador.ultimo_material_comprado) {
        const precoMin = parseFloat(comprador.preco_min_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        const precoMax = parseFloat(comprador.preco_max_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        let faixaPreco = `${precoMin} /Kg`;
        if (precoMin !== precoMax) {
            faixaPreco = `${precoMin} a ${precoMax} /Kg`;
        }
        precoHtml = `
            <p class="card-price-info">Faixa de preço (14 dias):</p>
            <span class="card-price-value">${faixaPreco}</span>
            <p class="card-price-material">em ${comprador.ultimo_material_comprado}</p>
        `;
    }

    card.innerHTML = `
        <div class="card-header">
            <div>
                <h3 class="card-title">${comprador.razao_social}</h3>
                <div class="card-location">
                    <span class="material-icons">place</span>
                    ${comprador.cidade || 'Não informado'}, ${comprador.estado || 'NI'}
                </div>
            </div>
            <div class="card-score">
                ${scoreHtml}
            </div>
        </div>
        <div class="card-body">
            ${precoHtml}
        </div>
        <div class="card-footer">
            Ver detalhes
        </div>
    `;

    // Adiciona o evento de clique para abrir o modal
    card.addEventListener('click', () => {
        abrirModalDetalhes(comprador);
    });

    col.appendChild(card);
    return col;
}

/**
 * Converte um score (número) em ícones de estrela (HTML)
 * @param {number} score - O score (ex: 4.3)
 * @returns {string} - O HTML das estrelas
 */
function gerarEstrelas(score) {
    if (score === null || score === undefined) return '<span style="font-size: 0.9rem;">Sem nota</span>';

    const scoreNum = parseFloat(score);
    let estrelas = '';
    const cheia = '<i class="fas fa-star"></i>';
    const meia = '<i class="fas fa-star-half-alt"></i>';
    const vazia = '<i class="far fa-star"></i>'; // Estrela vazia

    for (let i = 1; i <= 5; i++) {
        if (i <= scoreNum) {
            estrelas += cheia; // Estrela cheia
        } else if (i - 0.5 <= scoreNum) {
            estrelas += meia; // Meia estrela
        } else {
            estrelas += vazia; // Estrela vazia
        }
    }
    return `<span>${scoreNum.toFixed(1)}</span> ${estrelas}`;
}

/**
 * Busca todos os dados de detalhe e abre o modal (SweetAlert)
 * @param {object} comprador - O objeto do comprador (da lista inicial)
 */
async function abrirModalDetalhes(comprador) {
    const token = localStorage.getItem('session_token');

    // Feedback imediato de carregamento
    Swal.fire({
        title: `Carregando ${comprador.razao_social}...`,
        html: 'Buscando detalhes, materiais e avaliações.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    try {
        // 1. Busca os dados em paralelo (muito mais rápido)
        const [detalhesRes, tagsRes, comentariosRes] = await Promise.all([
            fetch(`/get/comprador-detalhes/${comprador.id_comprador}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(`/get/feedback-tags/${comprador.cnpj}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(`/get/comentarios-livres/${comprador.cnpj}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
        ]);

        // 2. Processa os JSON
        const detalhes = await detalhesRes.json();
        const tags = await tagsRes.json();
        const comentarios = await comentariosRes.json();

        // 3. Valida se alguma API falhou
        if (!detalhesRes.ok) throw new Error(detalhes.erro || 'Falha ao buscar detalhes');
        if (!tagsRes.ok) throw new Error(tags.erro || 'Falha ao buscar tags');
        if (!comentariosRes.ok) throw new Error(comentarios.erro || 'Falha ao buscar comentários');

        // 4. Constrói o HTML do modal
        const modalHtml = construirHtmlModal(comprador, detalhes, tags, comentarios);

        // 5. Exibe o SweetAlert completo
        Swal.fire({
            html: modalHtml,
            width: '800px', // Modal mais largo
            confirmButtonText: 'Fechar',
            confirmButtonColor: 'var(--verde-escuro-medio)'
        });

    } catch (err) {
        console.error('Erro ao abrir modal:', err);
        Swal.fire('Erro!', `Não foi possível carregar os detalhes deste comprador. (${err.message})`, 'error');
    }
}

/**
 * Constrói o HTML final para o pop-up SweetAlert
 */
function construirHtmlModal(comprador, detalhes, tags, comentarios) {

    // --- Contatos ---
    let contatosHtml = '';
    if (comprador.email) contatosHtml += `<li><span class="material-icons">email</span> ${comprador.email}</li>`;
    if (comprador.telefone) contatosHtml += `<li><span class="material-icons">phone</span> ${comprador.telefone}</li>`;
    if (comprador.whatsapp) contatosHtml += `<li><span class="material-icons">whatsapp</span> ${comprador.whatsapp}</li>`;
    if (!contatosHtml) contatosHtml = '<p>Nenhum contato direto informado.</p>';

    // --- Materiais e Preços ---
    let materiaisHtml = '';
    if (detalhes.materiais_comprados && detalhes.materiais_comprados.length > 0) {
        materiaisHtml = detalhes.materiais_comprados.map(mat => {
            const precoMin = parseFloat(mat.preco_min_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            const precoMax = parseFloat(mat.preco_max_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            let faixaPreco = `${precoMin} /Kg`;
            // Só mostra faixa (Ex: R$1,50 a R$2,00) se os preços forem diferentes
            if (precoMin !== precoMax) {
                faixaPreco = `${precoMin} a ${precoMax} /Kg`;
            }

            return `
                <li class="material-price-item">
                    <span class="material-name">${mat.material_nome} (x${mat.total_vendas} vendas)</span>
                    <span class="material-price-range">${faixaPreco}</span>
                </li>
            `;
        }).join('');
    } else {
        materiaisHtml = '<p>Este comprador ainda não registrou compras de materiais específicos.</p>';
    }

    // --- Tags de Feedback (Positivas e Negativas) ---
    let tagsHtml = '';
    if (tags && tags.length > 0) {
        tagsHtml = tags.map(tag => {
            // O seu comentarios_controller já retorna o 'tipo'
            const tagClass = tag.tipo === 'positivo' ? 'positivo' : 'negativo';
            return `
                <div class="feedback-tag ${tagClass}">
                    ${tag.texto}
                    <span class="tag-count">${tag.quantidade}x</span>
                </div>
            `;
        }).join('');
    } else {
        tagsHtml = '<p>Ainda não há avaliações rápidas para este comprador.</p>';
    }

    // --- Avaliações Recentes ---
    let avaliacoesHtml = '';
    if (detalhes.avaliacoes_recentes && detalhes.avaliacoes_recentes.length > 0) {
        // Agrupar avaliações por data (mais recentes primeiro)
        const avaliacoesAgrupadas = {};
        detalhes.avaliacoes_recentes.forEach(aval => {
            const dataFormatada = new Date(aval.data_avaliacao).toLocaleDateString('pt-BR');
            if (!avaliacoesAgrupadas[dataFormatada]) {
                avaliacoesAgrupadas[dataFormatada] = [];
            }
            avaliacoesAgrupadas[dataFormatada].push(aval);
        });

        // Mostrar apenas as 3 datas mais recentes
        const datasRecentes = Object.keys(avaliacoesAgrupadas).sort((a, b) => new Date(b) - new Date(a)).slice(0, 3);

        avaliacoesHtml = datasRecentes.map(data => {
            const avaliacoesDia = avaliacoesAgrupadas[data];
            const mediaPontualidade = avaliacoesDia.reduce((sum, aval) => sum + aval.pontualidade_pagamento, 0) / avaliacoesDia.length;
            const mediaLogistica = avaliacoesDia.reduce((sum, aval) => sum + aval.logistica_entrega, 0) / avaliacoesDia.length;
            const mediaNegociacao = avaliacoesDia.reduce((sum, aval) => sum + aval.qualidade_negociacao, 0) / avaliacoesDia.length;

            const estrelasPontualidade = gerarEstrelas(mediaPontualidade);
            const estrelasLogistica = gerarEstrelas(mediaLogistica);
            const estrelasNegociacao = gerarEstrelas(mediaNegociacao);

            const comentariosDia = avaliacoesDia.filter(aval => aval.comentario_livre).map(aval => aval.comentario_livre);

            return `
                <li class="avaliacao-item">
                    <div class="avaliacao-header">
                        <span class="avaliacao-data">${data}</span>
                        <span class="avaliacao-count">(${avaliacoesDia.length} avaliação${avaliacoesDia.length > 1 ? 'ões' : ''})</span>
                    </div>
                    <div class="avaliacao-scores">
                        <div class="score-item">
                            <span class="score-label">Pontualidade:</span>
                            ${estrelasPontualidade}
                        </div>
                        <div class="score-item">
                            <span class="score-label">Logística:</span>
                            ${estrelasLogistica}
                        </div>
                        <div class="score-item">
                            <span class="score-label">Negociação:</span>
                            ${estrelasNegociacao}
                        </div>
                    </div>
                    ${comentariosDia.length > 0 ? `<div class="avaliacao-comentarios">${comentariosDia.map(com => `<p class="avaliacao-comentario">"${com}"</p>`).join('')}</div>` : ''}
                </li>
            `;
        }).join('');
    } else {
        avaliacoesHtml = '<p>Nenhuma avaliação recente registrada.</p>';
    }

    // --- Comentários Livres (ANÔNIMOS) ---
    let comentariosHtml = '';
    if (comentarios && comentarios.length > 0) {
        comentariosHtml = comentarios.map(com => {
            return `
                <li class="comment-item">
                    <p class="comment-text">"${com.comentario_livre}"</p>
                    <p class="comment-anon">- Avaliação feita por uma Cooperativa</p>
                </li>
            `;
        }).join('');
    } else {
        comentariosHtml = '<p>Nenhum comentário adicional registrado.</p>';
    }

    // --- Montagem Final ---
    return `
        <div class="swal-modal-container">
            <h2 class="swal-modal-title">${comprador.razao_social}</h2>
            <p class="swal-modal-location">
                <span class="material-icons">place</span>
                ${comprador.endereco || 'Endereço não informado'} - ${comprador.cidade}, ${comprador.estado}
            </p>

            <section class="swal-modal-section">
                <h3 class="swal-modal-subtitle"><span class="material-icons">contacts</span> Contato</h3>
                <ul class="contact-list">${contatosHtml}</ul>
            </section>

            <section class="swal-modal-section">
                <h3 class="swal-modal-subtitle"><span class="material-icons">recycling</span> Materiais e Faixa de Preço</h3>
                <ul class="material-price-list">${materiaisHtml}</ul>
            </section>

            <section class="swal-modal-section">
                <h3 class="swal-modal-subtitle"><span class="material-icons">star</span> Avaliações Recentes</h3>
                <ul class="avaliacao-list">${avaliacoesHtml}</ul>
            </section>

            <section class="swal-modal-section">
                <h3 class="swal-modal-subtitle"><span class="material-icons">thumb_up_alt</span> Avaliações Rápidas</h3>
                <div class="feedback-tags-container">${tagsHtml}</div>
            </section>

            <section class="swal-modal-section">
                <h3 class="swal-modal-subtitle"><span class="material-icons">chat</span> Comentários (Anônimos)</h3>
                <ul class="comment-list">${comentariosHtml}</ul>
            </section>
        </div>
    `;
}

/**
 * Carrega materiais para o filtro de busca
 */
async function carregarMateriaisFiltro() {
    const token = localStorage.getItem('session_token');
    const materialFilter = document.getElementById('material-filter');

    if (!token) return;

    try {
        const response = await fetch('/get/materiais', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const materiais = await response.json();

        if (response.ok && materiais.length > 0) {
            materiais.forEach(material => {
                const option = document.createElement('option');
                option.value = material.id_material_base;
                option.textContent = material.nome;
                materialFilter.appendChild(option);
            });
        }
    } catch (err) {
        console.error('Erro ao carregar materiais:', err);
    }
}

/**
 * Configura os eventos dos filtros
 */
function configurarFiltros() {
    const applyFiltersBtn = document.getElementById('apply-filters');
    const clearFiltersBtn = document.getElementById('clear-filters');
    const searchInput = document.getElementById('search-input');

    applyFiltersBtn.addEventListener('click', aplicarFiltros);
    clearFiltersBtn.addEventListener('click', limparFiltros);

    // Busca em tempo real no campo de texto
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        filtrarCompradoresLocal(query);
    });
}

/**
 * Aplica os filtros selecionados
 */
async function aplicarFiltros() {
    const material = document.getElementById('material-filter').value;
    const estado = document.getElementById('estado-filter').value;
    const searchQuery = document.getElementById('search-input').value.toLowerCase();

    // Recarregar compradores com filtros aplicados
    await carregarCompradores(material, estado, searchQuery);
}

/**
 * Limpa todos os filtros
 */
function limparFiltros() {
    document.getElementById('material-filter').value = '';
    document.getElementById('estado-filter').value = '';
    document.getElementById('search-input').value = '';

    // Recarrega todos os compradores
    carregarCompradores();
}

/**
 * Filtra compradores localmente (por nome)
 * @param {string} query - Termo de busca
 */
function filtrarCompradoresLocal(query) {
    const cards = document.querySelectorAll('.comprador-card');

    cards.forEach(card => {
        const nome = card.querySelector('.card-title').textContent.toLowerCase();
        const shouldShow = nome.includes(query);
        card.closest('.col-12').style.display = shouldShow ? '' : 'none';
    });
}
