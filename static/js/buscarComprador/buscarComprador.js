document.addEventListener('DOMContentLoaded', () => {
    carregarMateriaisFiltro();

    carregarCompradores();

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
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        cardsContainer.innerHTML = '';

        const params = new URLSearchParams();
        if (filtros.material) params.append('material', filtros.material);
        if (filtros.estado) params.append('estado', filtros.estado);
        if (filtros.raio) params.append('raio', filtros.raio);

        const url = '/get/compradores' + (params.toString() ? '?' + params.toString() : '');

        const response = await fetch(url, {
            headers: {
                'Authorization': token
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao buscar dados.');
        }

        loadingSpinner.classList.add('d-none');

        if (data.length === 0) {
            cardsContainer.innerHTML = '<div class="col-12"><p class="text-center fs-5 text-muted">Nenhum comprador encontrado com os filtros aplicados.</p></div>';
            errorMessage.classList.add('d-none');
            return;
        }

        // Ordena os compradores por score de confiança (maior primeiro)
        data.sort((a, b) => (b.score_confianca || 0) - (a.score_confianca || 0));

        data.forEach(comprador => {
            const card = criarCardComprador(comprador);
            cardsContainer.appendChild(card);
        });

    } catch (err) {
        console.error('Erro em carregarCompradores:', err);
        mostrarErro('Não foi possível carregar os compradores.', err.message, );
    }

    function mostrarErro(mensagem, detalhe, type='alert') {
        loadingSpinner.classList.add('d-none');
        errorMessage.classList.remove('d-none'); 
        errorTitle.textContent = detalhe;
        errorDetail.textContent = mensagem; 

        errorMessage.classList.remove('alert-danger', 'alert-warning');

        switch (type)
        {
            case 'alert':
                errorMessage.classList.add('alert-danger');
                break;
            case 'warning':
                errorMessage.classList.add('alert-warning');
                break;
        }
    }
}

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
        const precoMedio = parseFloat(comprador.preco_medio).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

        let faixaPreco = `${precoMin} /Kg`;
        if (precoMin !== precoMax) {
            faixaPreco = `${precoMin} a ${precoMax} /Kg`;
        }
        precoHtml = `
            <div>
                <div class="d-flex justify-content-between card-min-max-price">
                    <div class="card-price-info card-max-price">
                        <span class="material-icons">north</span>
                        <span>${precoMin} /Kg</span>
                    </div>
                    <div class="card-price-info card-min-price">
                        <span class="material-icons">south</span>
                        <span>${precoMax} /Kg</span>
                    </div>
                </div>
                <div class="d-flex flex-column text-center card-avg-price mt-3 card-price-info">
                    <span class="avg-price-label">Preço Médio</span>
                    <span>${precoMedio} /Kg</span>
                </div>
            </div>
        `;
    }

    card.innerHTML = `
        <div class="card-header">
            <div>
                <h3 class="card-title">${comprador.razao_social}</h3>
                <span class="card-cnpj">${safeFormatarCNPJ(comprador.cnpj)}</span>
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
    return `<span class="nota-comprador">${scoreNum.toFixed(1)}</span> ${estrelas}`;
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
        html: 'Buscando todos os detalhes do comprador.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    try {
        const response = await fetch(`/get/comprador-detalhes/${comprador.id_comprador}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const detalhes = await response.json();

        // Valida se a API falhou
        if (!response.ok) {
            throw new Error(detalhes.error || 'Falha ao buscar detalhes do comprador');
        }

        const modalHtml = construirHtmlModal(detalhes);

        Swal.fire({
            html: modalHtml,
            width: '800px',
            showCloseButton: true,
            showConfirmButton: false
        });

    } catch (err) {
        console.error('Erro ao abrir modal:', err);
        Swal.fire('Erro!', `Não foi possível carregar os detalhes deste comprador. (${err.message})`, 'error');
    }
}

/**
 * Constrói o HTML final para o pop-up SweetAlert
 */
function construirHtmlModal(detalhes) {
    const { logradouro, numero, complemento, bairro, cidade, estado, email } = detalhes;
    const { phones } = detalhes.api_externa || {};

    const enderecoFormatado = [logradouro, numero, complemento, bairro]
        .filter(Boolean)
        .join(', ') + ` - ${cidade}, ${estado}`;

    let phoneList = [];
    if (phones && phones.length > 0) {
        const uniquePhones = new Set();
        phones.forEach(phone => {
            const numeroCompleto = `(${phone.area}) ${phone.number}`;
            if (!uniquePhones.has(numeroCompleto)) {
                uniquePhones.add(numeroCompleto);
                phoneList.push({ numero: numeroCompleto, type: phone.type });
            }
        });
    } else {
        const uniquePhones = new Set();
        if (detalhes.telefone) {
            uniquePhones.add(detalhes.telefone);
            phoneList.push({ numero: detalhes.telefone, type: 'LANDLINE' });
        }
        if (detalhes.whatsapp && !uniquePhones.has(detalhes.whatsapp)) {
            uniquePhones.add(detalhes.whatsapp);
            phoneList.push({ numero: detalhes.whatsapp, type: 'MOBILE' });
        }
    }

    if (phoneList.length > 2) {
        phoneList = phoneList.slice(0, 2);
    }

    let contatosHtml = '';
    if (email) {
        contatosHtml += `<li><span class="material-icons">email</span> ${email}</li>`;
    }

    phoneList.forEach(phone => {
        const icon = phone.type === 'MOBILE' ? 'smartphone' : 'phone';
        contatosHtml += `<li><span class="material-icons">${icon}</span> ${phone.numero}</li>`;
    });

    contatosHtml += `<li><span class="material-icons">place</span> ${enderecoFormatado}</li>`;

    let materiaisHtml = '';
    if (detalhes.materiais_comprados && detalhes.materiais_comprados.length > 0) {
        materiaisHtml = detalhes.materiais_comprados.map(mat => {
            const precoMin = parseFloat(mat.preco_max_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            const precoMax = parseFloat(mat.preco_min_kg).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            const faixaPreco = precoMin !== precoMax ? `${precoMin} a ${precoMax} /Kg` : `${precoMin} /Kg`;

            return `
                <li class="material-price-item">
                    <span class="material-name">${mat.material_nome} (x${mat.total_vendas} vendas)</span>
                    <span class="material-price-range">${faixaPreco}</span>
                </li>`;
        }).join('');
    } else {
        materiaisHtml = '<p>Este comprador ainda não registrou compras de materiais específicos.</p>';
    }

    const tags = detalhes.feedback_tags || [];
    const tagsHtml = tags.length > 0 ? tags.map(tag => `
        <div class="feedback-tag ${tag.tipo === 'positivo' ? 'positivo' : 'negativo'}">
            ${tag.texto}
            <span class="tag-count">${tag.quantidade}x</span>
        </div>`
    ).join('') : '<p>Ainda não há avaliações rápidas para este comprador.</p>';

    const avaliacoesLimitadas = (detalhes.avaliacoes_recentes || []).slice(0, 5);
    const avaliacoesHtml = avaliacoesLimitadas.length > 0 ? avaliacoesLimitadas.map(aval => {
        const dataFormatada = new Date(aval.data_avaliacao).toLocaleDateString('pt-BR');
        const estrelasHtml = gerarEstrelas(aval.score);
        const comentarioHtml = aval.comentario_livre ? `<p class="avaliacao-comentario">“${aval.comentario_livre}”</p>` : '';

        return `
            <li class="avaliacao-item">
                <div class="avaliacao-header">
                    <div class="avaliacao-estrelas">${estrelasHtml}</div>
                    <span class="avaliacao-data">${dataFormatada}</span>
                </div>
                ${comentarioHtml}
            </li>`;
    }).join('') : '<p>Nenhuma avaliação recente registrada.</p>';
    
    const whatsAppNumber = phoneList.find(p => p.type === 'MOBILE');
    const whatsAppButton = whatsAppNumber ? `
        <a href="https://wa.me/55${whatsAppNumber.numero.replace(/\D/g, '')}" target="_blank" class="btn btn-success ms-2">
            <i class="fab fa-whatsapp"></i> WhatsApp
        </a>` : '';

    return `
        <div class="swal-modal-container">
            <div class="swal-modal-header">
                <h2 class="swal-modal-title">${detalhes.razao_social}</h2>
            </div>

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

            <section class="swal-modal-footer d-flex justify-content-end">
                <button type="button" class="btn btn-secondary" onclick="Swal.close()">Fechar</button>
                ${whatsAppButton}
            </section>
        </div>
    `;
}

function configurarFiltros() {
    const btnAplicarFiltros = document.getElementById('apply-filters');
    const searchInput = document.getElementById('search-input');

    // Botão de Ação para Aplicar Filtros do Servidor
    btnAplicarFiltros.addEventListener('click', async function () {
        await aplicarFiltros();

        const query = searchInput.value.trim();
        if (query) {
            filtrarCompradoresLocal(query);
        }
    });

    // Botão para Limpar Filtros
    document.getElementById('clear-filters').addEventListener('click', limparFiltros);

    // Função interna para a busca por Nome/CNPJ
    function buscarNomeCNPJ() {
        const query = searchInput.value.trim();

        if (query === '') {
            aplicarFiltros(); 
        } else {
            aplicarFiltros().then(() => {
                filtrarCompradoresLocal(query);
            });
        }
    }

    searchInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            buscarNomeCNPJ();
        }
    });

    // Lógica do Slider de Raio
    const enableRadius = document.getElementById('enable-radius-filter');
    const radiusControls = document.getElementById('radius-controls');
    const radiusInput = document.getElementById('radius-filter');
    const radiusValue = document.getElementById('radius-value');

    enableRadius.addEventListener('change', () => {
        radiusControls.disabled = !enableRadius.checked;
        radiusValue.textContent = enableRadius.checked ? `${radiusInput.value} km` : '...';
    });

    radiusInput.addEventListener('input', (e) => {
        radiusValue.textContent = `${e.target.value} km`;
    });

    const materialSelect = document.getElementById('material-filter');
    materialSelect.addEventListener('change', (e) => {
        const idMaterialPai = e.target.value;
        carregarSubtipos(idMaterialPai);
    });
}

/**
 * Carrega os Tipos de Materiais (Categorias Principais)
 */
async function carregarMateriaisFiltro() {
    try {
        // Ajuste a rota se necessário para pegar apenas as categorias pais
        const response = await fetch('/get/materiais'); 
        const materiais = await response.json();

        const select = document.getElementById('material-filter');
        // Mantém a opção padrão
        select.innerHTML = '<option value="">Todos os tipos</option>';

        materiais.forEach(mat => {
            const option = document.createElement('option');
            option.value = mat.id_material_base;
            option.textContent = mat.nome_padrao;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar materiais:', error);
    }
}

/**
 * Carrega os Subtipos baseado no Material Pai selecionado
 * @param {string} idMaterialPai 
 */
async function carregarSubtipos(idMaterialPai) {
    const subtipoSelect = document.getElementById('subtipo-filter');
    
    // Resetar o select de subtipos
    subtipoSelect.innerHTML = '<option value="">Todos os subtipos</option>';
    
    if (!idMaterialPai) {
        subtipoSelect.disabled = true;
        subtipoSelect.innerHTML = '<option value="">Selecione um tipo primeiro</option>';
        return;
    }

    try {
        subtipoSelect.disabled = true; // Trava enquanto carrega
        
        const response = await fetch(`/get/subtipos/${idMaterialPai}`);
        
        if (!response.ok) throw new Error('Falha ao buscar subtipos');
        
        const subtipos = await response.json();

        subtipos.forEach(sub => {
            const option = document.createElement('option');
            option.value = sub.id_material_catalogo; 
            option.textContent = sub.nome_especifico;
            subtipoSelect.appendChild(option);
        });

        subtipoSelect.disabled = false; // Destrava após carregar

    } catch (error) {
        console.error('Erro ao carregar subtipos:', error);
        subtipoSelect.innerHTML = '<option value="">Erro ao carregar</option>';
    }
}

/**
 * Aplica os filtros selecionados e chama a API
 */
async function aplicarFiltros() {
    const material = document.getElementById('material-filter').value;
    const subtipo = document.getElementById('subtipo-filter').value; // NOVO
    const estado = document.getElementById('estado-filter').value;
    
    // Lógica do Raio
    const enableRadius = document.getElementById('enable-radius-filter');
    const raio = enableRadius.checked ? document.getElementById('radius-filter').value : null;

    const filtros = {};

    if (material) filtros.material = material;
    if (subtipo) filtros.subtipo = subtipo; 
    if (estado) filtros.estado = estado;
    if (raio) filtros.raio = parseFloat(raio);

    await carregarCompradores(filtros);
}

/**
 * Limpa todos os filtros
 */
function limparFiltros() {
    document.getElementById('material-filter').value = '';
    
    // Limpa e desabilita o subtipo
    const subtipoSelect = document.getElementById('subtipo-filter');
    subtipoSelect.value = '';
    subtipoSelect.innerHTML = '<option value="">Selecione um tipo primeiro</option>';
    subtipoSelect.disabled = true;

    document.getElementById('estado-filter').value = '';
    document.getElementById('search-input').value = '';
    
    // Reseta o raio
    document.getElementById('enable-radius-filter').checked = false;
    document.getElementById('radius-controls').disabled = true;
    document.getElementById('radius-value').textContent = '...';

    // Recarrega todos os compradores (sem filtros)
    carregarCompradores({});
}

function desformatarCNPJ(cnpj) 
{
    return cnpj.replace(/[^\d]+/g, '');
}

/**
 * Filtra compradores localmente (por nome)
 * @param {string} query - Termo de busca
 */
function filtrarCompradoresLocal(query) {
    const cards = document.querySelectorAll('.comprador-card');

    cards.forEach(card => {
        const nome = card.querySelector('.card-title').textContent.toLowerCase();
        const cnpj = card.querySelector('.card-cnpj').textContent;
        const shouldShow = nome.includes(query.toLowerCase()) || desformatarCNPJ(cnpj).includes(query) || cnpj.includes(query);
        card.closest('.col-12').style.display = shouldShow ? '' : 'none';
    });
}