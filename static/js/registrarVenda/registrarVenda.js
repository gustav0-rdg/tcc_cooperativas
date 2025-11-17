import { getMateriais } from '../api/getMateriais.js';

// Aguarda o DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    inicializarRegistroVenda();
});

// Estado da venda
let vendaAtual = {
    material: null,
    subtipo: null,
    comprador: null,
    quantidade: 0,
    preco: 0,
    avaliacao: {}
};

let etapaAtual = 1;
const totalEtapas = 4;

/**
 * Inicializa o registro de venda
 */
async function inicializarRegistroVenda() {
    const token = localStorage.getItem('session_token');
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const mainContent = document.getElementById('main-content');

    if (!token) {
        mostrarErro('Sessão inválida. Faça o login novamente.');
        return;
    }

    try {
        loadingSpinner.classList.remove('d-none');
        errorMessage.classList.add('d-none');
        mainContent.classList.add('d-none');

        // Carrega materiais
        await carregarMateriais();

        loadingSpinner.classList.add('d-none');
        mainContent.classList.remove('d-none');

        // Configura eventos
        configurarEventos();

        // Mostra primeira etapa
        mostrarEtapa(1);

        // Adiciona botão para adicionar novo material
        // adicionarBotaoNovoMaterial(); // Removido pois o botão já está no HTML

    } catch (err) {
        console.error('Erro em inicializarRegistroVenda:', err);
        mostrarErro('Não foi possível inicializar o registro de venda.');
    }
}

/**
 * Carrega materiais via API
 */
async function carregarMateriais() {
    try {
        const materiais = await getMateriais();
        if (!materiais || materiais.length === 0) {
            throw new Error('Nenhum material encontrado.');
        }
        vendaAtual.materiaisDisponiveis = materiais;
    } catch (err) {
        throw new Error('Erro ao carregar materiais: ' + err.message);
    }
}

/**
 * Configura eventos dos botões
 */
function configurarEventos() {
    document.getElementById('btn-prev').addEventListener('click', () => navegarEtapa(-1));
    document.getElementById('btn-next').addEventListener('click', () => navegarEtapa(1));
}

/**
 * Navega entre etapas
 */
function navegarEtapa(direcao) {
    const novaEtapa = etapaAtual + direcao;

    if (novaEtapa < 1 || novaEtapa > totalEtapas) return;

    // Validação da etapa atual antes de prosseguir
    if (direcao > 0 && !validarEtapaAtual()) {
        return;
    }

    etapaAtual = novaEtapa;
    mostrarEtapa(etapaAtual);
}

/**
 * Valida a etapa atual
 */
function validarEtapaAtual() {
    switch (etapaAtual) {
        case 1:
            return vendaAtual.material !== null;
        case 2:
            return vendaAtual.subtipo !== null;
        case 3:
            return vendaAtual.comprador !== null;
        case 4:
            return vendaAtual.quantidade > 0 && vendaAtual.preco > 0;
        default:
            return true;
    }
}

/**
 * Mostra a etapa especificada
 */
function mostrarEtapa(etapa) {
    atualizarCabecalho(etapa);
    atualizarConteudo(etapa);
    atualizarNavegacao(etapa);
}

/**
 * Atualiza o cabeçalho da etapa
 */
function atualizarCabecalho(etapa) {
    const titulos = {
        1: { titulo: 'Selecionar Material', subtitulo: 'Escolha o material que você vendeu' },
        2: { titulo: 'Selecionar Subtipo', subtitulo: 'Escolha o subtipo do material' },
        3: { titulo: 'Selecionar Comprador', subtitulo: 'Escolha o comprador' },
        4: { titulo: 'Informações da Venda', subtitulo: 'Digite os detalhes da venda' }
    };

    const info = titulos[etapa];
    document.getElementById('step-title').textContent = info.titulo;
    document.getElementById('step-subtitle').textContent = info.subtitulo;

    const progresso = (etapa / totalEtapas) * 100;
    document.getElementById('progress-bar').style.width = `${progresso}%`;
    document.getElementById('progress-label').textContent = `Passo ${etapa} de ${totalEtapas}`;
}

/**
 * Atualiza o conteúdo da etapa
 */
function atualizarConteudo(etapa) {
    const stepContent = document.getElementById('step-content');

    switch (etapa) {
        case 1:
            stepContent.innerHTML = gerarConteudoMateriais();
            break;
        case 2:
            stepContent.innerHTML = gerarConteudoSubtipos();
            break;
        case 3:
            stepContent.innerHTML = gerarConteudoCompradores();
            break;
        case 4:
            stepContent.innerHTML = gerarConteudoDetalhes();
            break;
    }
}

/**
 * Gera conteúdo para seleção de materiais
 */
function gerarConteudoMateriais() {
    const materiais = vendaAtual.materiaisDisponiveis || [];

    return `
        <div class="selection-grid">
            ${materiais.map(material => {
                const nomes = [material.nome, ...material.sinonimos];
                return `
                <div class="selection-card ${vendaAtual.material?.id === material.id_material_base ? 'selected' : ''}"
                     data-id="${material.id_material_base}"
                     data-nome="${material.nome}">
                    <h4>${material.nome}</h4>
                    ${material.sinonimos && material.sinonimos.length > 0 ? `<small>Sinônimos: ${material.sinonimos.join(', ')}</small>` : ''}
                    <p>Material reciclável</p>
                    <button class="btn btn-sm btn-outline-primary btn-sinonimo" data-material-id="${material.id_material_base}" data-material-nome="${material.nome}">
                        <i class="fas fa-edit"></i> Sinônimo
                    </button>
                </div>
                `;
            }).join('')}
            <div class="selection-card novo-material" data-action="novo">
                <h4>+ Novo Material</h4>
                <p>Adicionar material não listado</p>
            </div>
        </div>
    `;
}

/**
 * Gera conteúdo para seleção de subtipos
 */
function gerarConteudoSubtipos() {
    // Simulação de subtipos - em produção, buscar via API
    const subtipos = [
        { id: 1, nome: 'Papel Branco', descricao: 'Papel de escritório' },
        { id: 2, nome: 'Papel Misto', descricao: 'Papéis diversos' },
        { id: 3, nome: 'Jornais e Revistas', descricao: 'Materiais impressos' }
    ];

    return `
        <div class="selection-grid">
            ${subtipos.map(subtipo => `
                <div class="selection-card ${vendaAtual.subtipo?.id === subtipo.id ? 'selected' : ''}"
                     data-id="${subtipo.id}"
                     data-nome="${subtipo.nome}">
                    <h4>${subtipo.nome}</h4>
                    <p>${subtipo.descricao}</p>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Gera conteúdo para seleção de compradores
 */
function gerarConteudoCompradores() {
    // Simulação de compradores - em produção, buscar via API
    const compradores = [
        { id: 1, nome: 'Empresa A', local: 'São Paulo, SP' },
        { id: 2, nome: 'Empresa B', local: 'Rio de Janeiro, RJ' },
        { id: 3, nome: 'Empresa C', local: 'Belo Horizonte, MG' }
    ];

    return `
        <div class="selection-grid">
            ${compradores.map(comprador => `
                <div class="selection-card ${vendaAtual.comprador?.id === comprador.id ? 'selected' : ''}"
                     data-id="${comprador.id}"
                     data-nome="${comprador.nome}">
                    <h4>${comprador.nome}</h4>
                    <p>${comprador.local}</p>
                </div>
            `).join('')}
        </div>
    `;
}

/**
 * Gera conteúdo para detalhes da venda
 */
function gerarConteudoDetalhes() {
    return `
        <div class="step-form">
            <h3>Detalhes da Venda</h3>
            <div class="input-group">
                <label for="quantidade">Quantidade (kg)</label>
                <input type="number" id="quantidade" min="0" step="0.1" value="${vendaAtual.quantidade || ''}" required>
            </div>
            <div class="input-group">
                <label for="preco">Preço por kg (R$)</label>
                <input type="number" id="preco" min="0" step="0.01" value="${vendaAtual.preco || ''}" required>
            </div>
        </div>
    `;
}

/**
 * Atualiza a navegação
 */
function atualizarNavegacao(etapa) {
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    btnPrev.disabled = etapa === 1;

    if (etapa === totalEtapas) {
        btnNext.textContent = 'Finalizar Venda';
        btnNext.innerHTML = '<i class="fas fa-check"></i> Finalizar Venda';
        btnNext.onclick = finalizarVenda;
    } else {
        btnNext.textContent = 'Próximo';
        btnNext.innerHTML = 'Próximo <i class="fas fa-arrow-right"></i>';
        btnNext.onclick = () => navegarEtapa(1);
    }
}

/**
 * Finaliza a venda
 */
async function finalizarVenda() {
    if (!validarEtapaAtual()) {
        Swal.fire('Atenção!', 'Por favor, preencha todos os campos obrigatórios.', 'warning');
        return;
    }

    try {
        // Aqui seria feita a chamada para a API de salvar venda
        // Por enquanto, apenas simula o sucesso

        Swal.fire('Sucesso!', 'Venda registrada com sucesso!', 'success')
            .then(() => {
                window.location.href = '/pagina-inicial';
            });

    } catch (err) {
        console.error('Erro em finalizarVenda:', err);
        Swal.fire('Erro!', 'Não foi possível registrar a venda. Tente novamente.', 'error');
    }
}

/**
 * Mostra mensagem de erro
 */
function mostrarErro(mensagem) {
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorMessage = document.getElementById('error-message');
    const errorDetail = document.getElementById('error-detail');

    if (errorDetail) {
        loadingSpinner.classList.add('d-none');
        errorMessage.classList.remove('d-none');
        errorDetail.textContent = mensagem;
    } else {
        console.error('Elemento error-detail não encontrado no DOM');
    }
}

// Delegação de eventos para seleção de cards
document.addEventListener('click', async (e) => {
    if (e.target.closest('.selection-card')) {
        const card = e.target.closest('.selection-card');
        const cards = document.querySelectorAll('.selection-card');

        // Verifica se é o botão de sinônimo
        if (e.target.closest('.btn-sinonimo')) {
            e.stopPropagation();
            const btn = e.target.closest('.btn-sinonimo');
            const materialId = btn.dataset.materialId;
            const materialNome = btn.dataset.materialNome;

            const { value: sinonimo } = await Swal.fire({
                title: `Adicionar Sinônimo para ${materialNome}`,
                input: 'text',
                inputLabel: 'Digite o sinônimo para este material',
                inputPlaceholder: 'Ex: Papel Pardo, Plástico PET, etc.',
                showCancelButton: true,
                confirmButtonText: 'Adicionar',
                cancelButtonText: 'Cancelar',
                inputValidator: (value) => {
                    if (!value) {
                        return 'Sinônimo é obrigatório!';
                    }
                }
            });

            if (sinonimo) {
                try {
                    const response = await fetch('/post/cadastrar-sinonimo-base', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            id_material_base: materialId,
                            sinonimo: sinonimo
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        Swal.fire('Sucesso!', 'Sinônimo adicionado com sucesso!', 'success');
                        // Recarrega materiais
                        await carregarMateriais();
                        mostrarEtapa(1);
                    } else {
                        Swal.fire('Erro!', result.message || 'Erro ao adicionar sinônimo.', 'error');
                    }
                } catch (error) {
                    console.error('Erro ao adicionar sinônimo:', error);
                    Swal.fire('Erro!', 'Erro ao adicionar sinônimo.', 'error');
                }
            }
            return;
        }

        // Verifica se é o card de novo material
        if (card.classList.contains('novo-material')) {
            const { value: nomeMaterial } = await Swal.fire({
                title: 'Novo Material',
                input: 'text',
                inputLabel: 'Digite o nome do material que você vendeu',
                inputPlaceholder: 'Ex: Plástico PET, Papel Kraft, etc.',
                showCancelButton: true,
                confirmButtonText: 'Adicionar',
                cancelButtonText: 'Cancelar',
                inputValidator: (value) => {
                    if (!value) {
                        return 'Nome do material é obrigatório!';
                    }
                }
            });

            if (nomeMaterial) {
                try {
                    const response = await fetch('/post/cadastrar-material-base', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ nome_material: nomeMaterial })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        Swal.fire('Sucesso!', 'Material adicionado com sucesso!', 'success');
                        // Recarrega materiais
                        await carregarMateriais();
                        mostrarEtapa(1);
                    } else {
                        Swal.fire('Erro!', result.message || 'Erro ao adicionar material.', 'error');
                    }
                } catch (error) {
                    console.error('Erro ao adicionar material:', error);
                    Swal.fire('Erro!', 'Erro ao adicionar material.', 'error');
                }
            }
            return;
        }

        // Remove seleção de todos
        cards.forEach(c => c.classList.remove('selected'));

        // Seleciona o clicado
        card.classList.add('selected');

        // Atualiza o estado
        const id = parseInt(card.dataset.id);
        const nome = card.dataset.nome;

        switch (etapaAtual) {
            case 1:
                vendaAtual.material = { id, nome };
                break;
            case 2:
                vendaAtual.subtipo = { id, nome };
                break;
            case 3:
                vendaAtual.comprador = { id, nome };
                break;
        }
    }
});

// Atualiza quantidade e preço em tempo real
document.addEventListener('input', (e) => {
    if (e.target.id === 'quantidade') {
        vendaAtual.quantidade = parseFloat(e.target.value) || 0;
    } else if (e.target.id === 'preco') {
        vendaAtual.preco = parseFloat(e.target.value) || 0;
    }
});
