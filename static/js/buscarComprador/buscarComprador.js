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
async function carregarCompradores(filtros = {}) {
    const token = localStorage.getItem('session_token');
    const cardsContainer = document.getElementById('cards-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorDetail = document.getElementById('error-detail');
    const errorTitle = document.getElementById('error-title');

    if (!token) {
        mostrarErro('Sessão inválida. Faça o login novamente.', 'Token não encontrado.');
        return;
    }

    try {
        // Mostrar loading
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        cardsContainer.innerHTML = '';

        // Construir URL com parâmetros de filtro
        const params = new URLSearchParams();
        if (filtros.material) params.append('material', filtros.material);
        if (filtros.estado) params.append('estado', filtros.estado);
        if (filtros.raio) params.append('raio', filtros.raio);

        const url = '/get/compradores' + (params.toString() ? '?' + params.toString() : '');
        
        console.log('Buscando compradores com URL:', url);

        const response = await fetch(url, {
            headers: { 
                'Authorization': token 
            }
        });

        const data = await response.json();

        console.log(data)

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar dados.');
        }

        // Esconde o loading
        loadingSpinner.classList.add('d-none');

        // Renderiza os cards
        if (data.length === 0) {
            cardsContainer.innerHTML = '<div class="col-12"><p class="text-center fs-5 text-muted">Nenhum comprador encontrado com os filtros aplicados.</p></div>';
            mostrarErro('oi', 'oi', 'warning')
            return;
        }

        data.forEach(comprador => {
            const card = criarCardComprador(comprador);
            cardsContainer.appendChild(card);
        });

    } catch (err) {
        console.error('Erro em carregarCompradores:', err);
        mostrarErro('Não foi possível carregar os compradores.', err.message, );
    }

    // Função interna de ajuda para mostrar erros
    function mostrarErro(mensagem, detalhe, type='alert') {
        loadingSpinner.classList.add('d-none');
        errorMessage.classList.remove('d-none');
        errorTitle.textContent = detalhe;
        errorDetail.textContent = mensagem; 

        switch (type)
        {
            case 'alert':

                errorMessage.className = 'alert alert-danger d-none text-center pt-5 pb-5';
                break;

            case 'warning':

                errorMessage.className = 'alert alert-warning d-none text-center pt-5 pb-5';
                break;
        }
    }
}

/**
 * Cria o elemento HTML (card) para um comprador
 * @param {object} comprador - O objeto do comprador vindo da API
 * @returns {HTMLElement} O elemento <div> do card
 */
function criarCardComprador(comprador) {

    console.log(comprador);

    const col = document.createElement('div');
    col.className = 'col-12 col-md-6 col-lg-4';

    const card = document.createElement('div');
    card.className = 'comprador-card';
    card.setAttribute('data-id', comprador.id_comprador);
    card.setAttribute('data-cnpj', comprador.cnpj);

    // Converte o score (Ex: 4.5) em estrelas
    const scoreHtml = gerarEstrelas(comprador.score_confianca);

    // Mostra a distância se disponível
    let distanciaHtml = '';
    if (comprador.distancia !== undefined) {
        distanciaHtml = `<div class="card-distance"><span class="material-icons">near_me</span> ${comprador.distancia} km</div>`;
    }

    // Formata o preço, se existir
    let precoHtml = '<p class="card-no-price">Nenhum preço registrado recentemente.</p>';
    if (comprador.preco_maximo && comprador.preco_minimo) 
    {
        const precoMin = parseFloat(comprador.preco_maximo).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        const precoMax = parseFloat(comprador.preco_minimo).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        let faixaPreco = `${precoMin} /Kg`;
        if (precoMin !== precoMax) {
            faixaPreco = `${precoMin} a ${precoMax} /Kg`;
        }
        precoHtml = `
            <div class="d-flex justify-content-between">
                <div>
                    <span class="material-icons">near_me</span>
                    <span class="card-price-info">${precoMin}</span>
                </div>
                <div>
                    <span class="material-icons">near_me</span>
                    <span class="card-price-info">${precoMax}</span>
                </div>
            </div>
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
                ${distanciaHtml}
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
        confirmButtonColor: 'var(--verde-claro-medio)'
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
            const precoMin = parseFloat(mat.preco_maximo).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            const precoMax = parseFloat(mat.preco_minimo).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
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
        const response_materiais = await fetch('/get/materiais', {
            headers: { 
                'Authorization': token 
            }
        });

        const materiais = await response_materiais.json();

        if (response_materiais.ok && materiais.length > 0) {
            // Processar cada material
            for (const material of materiais) {
                // Criar optgroup para o material base
                const optgroupMaterial = document.createElement('optgroup');
                optgroupMaterial.setAttribute('label', material.nome);

                // Adicionar opção "Todos de [Material]"
                const optionTodos = document.createElement('option');
                optionTodos.value = material.id_material_base;
                optionTodos.textContent = `✓ Todos de ${material.nome}`;
                optionTodos.className = 'material-all-option';
                optgroupMaterial.appendChild(optionTodos);

                // Buscar subtipos
                const response_subtipos = await fetch(`/get/subtipos/${material.id_material_base}`, {
                    headers: { 
                        'Authorization': token 
                    }
                });

                const subtipos = await response_subtipos.json();
                
                // Adicionar cada subtipo
                subtipos.forEach(subtipo => {
                    const optionSubtipo = document.createElement('option');
                    optionSubtipo.value = material.id_material_base; // Usa o ID do material base
                    optionSubtipo.textContent = `  ${subtipo.descricao}`;
                    optionSubtipo.className = 'material-subtipo-option';
                    optgroupMaterial.appendChild(optionSubtipo);
                });

                materialFilter.appendChild(optgroupMaterial);
            }
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
    const radiusFilter = document.getElementById('radius-filter');
    const radiusValue = document.getElementById('radius-value');

    applyFiltersBtn.addEventListener('click', aplicarFiltros);
    clearFiltersBtn.addEventListener('click', limparFiltros);

    // Atualiza o valor do raio em tempo real
    radiusFilter.addEventListener('input', (e) => {
        radiusValue.textContent = e.target.value;
    });

    // Busca em tempo real no campo de texto (filtro local)
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
    const raio = document.getElementById('radius-filter').value;

    const filtros = {};
    if (material) filtros.material = material;
    if (estado) filtros.estado = estado;
    if (raio) filtros.raio = parseFloat(raio);

    console.log('Aplicando filtros:', filtros);

    // Recarregar compradores com filtros aplicados
    await carregarCompradores(filtros);
}

/**
 * Limpa todos os filtros
 */
function limparFiltros() {
    document.getElementById('material-filter').value = '';
    document.getElementById('estado-filter').value = '';
    document.getElementById('search-input').value = '';
    document.getElementById('radius-filter').value = '100';
    document.getElementById('radius-value').textContent = '100';

    // Recarrega todos os compradores
    carregarCompradores({});
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
