// /static/js/gerenciar_gestor/gerenciarGestor.js

// --- CONSTANTES GLOBAIS ---
const session_token = localStorage.getItem('session_token');
const cardsContainer = document.getElementById('gestoresCards');
const addGestorBtn = document.getElementById('addGestorBtn');
const barraPesquisa = document.getElementById('searchInput');

// URLs da API (para fácil manutenção)
const API_ENDPOINTS = {
    GET_ALL: '/api/usuarios/get-all-gestores',
    CREATE: '/api/usuarios/cadastrar',
    UPDATE: (id) => `/api/usuarios/update/${id}`,
    // Usando GET para delete, como no seu código original que funcionava
    DELETE: (id) => `/api/usuarios/delete/${id}` 
};  

// --- ESTADO GLOBAL ---
// Armazena a lista de gestores para evitar chamadas de API na pesquisa
let todosGestores = [];

// --- INICIALIZAÇÃO ---
document.addEventListener('DOMContentLoaded', init);

/**
 * Função principal de inicialização
 */
async function init() {
    if (!session_token) {
        // Assume que URL_LOGIN_ADMIN está definida globalmente
        window.location.href = URL_LOGIN_ADMIN || '/admin/login'; 
        return;
    }

    setupEventListeners();
    await carregarEExibirGestores(true); // Faz o carregamento inicial
}

/**
 * Configura todos os event listeners da página
 */
function setupEventListeners() {
    addGestorBtn.addEventListener('click', () => openAddGestorModal());
    barraPesquisa.addEventListener('input', filtrarEExibirGestores);
    
    // Delegação de eventos para os botões de ação nos cards
    cardsContainer.addEventListener('click', (e) => {
        const button = e.target.closest('button');
        if (!button) return;

        e.preventDefault();
        const card = button.closest('.gestor-card');
        // Pega o ID do card (fonte única da verdade)
        const id = parseInt(card.dataset.id, 10); 

        if (button.classList.contains('btn-excluir')) {
            const nome = button.dataset.gestorNome; // Pega o nome do botão
            openDeleteModal(id, nome, card);
        } else if (button.classList.contains('btn-editar')) {
            handleEditClick(id);
        }
    });
}

// --- LÓGICA PRINCIPAL (CARREGAR E RENDERIZAR) ---

/**
 * Carrega os gestores da API, atualiza o estado global e renderiza os cards.
 * @param {boolean} [showLoading=false] - Se deve mostrar um indicador de "Carregando...".
 */
async function carregarEExibirGestores(showLoading = false) {
    if (showLoading) {
        cardsContainer.innerHTML = `<p class="text-center text-white-50 fs-5 mt-4">Carregando gestores...</p>`;
    }

    try {
        const gestores = await apiFetch(API_ENDPOINTS.GET_ALL);
        todosGestores = gestores; // Atualiza o estado global
        renderizarCards(todosGestores);
    } catch (error) {
        showError('Erro ao Carregar Gestores', error.message);
        cardsContainer.innerHTML = `<p class="text-center text-danger fs-5 mt-4">Não foi possível carregar os gestores.</p>`;
    }
}

/**
 * Renderiza os cards no HTML com base na lista de gestores.
 * @param {Array} listaGestores - A lista de gestores a ser renderizada.
 */
function renderizarCards(listaGestores) {
    if (listaGestores.length === 0) {
        const termo = barraPesquisa.value;
        const mensagem = termo 
            ? `Nenhum gestor encontrado para "<strong>${termo}</strong>".`
            : 'Nenhum gestor cadastrado no momento.';
        cardsContainer.innerHTML = `<p class="text-center text-white-50 fs-5 mt-4">${mensagem}</p>`;
        return;
    }

    const cardsHtml = listaGestores.map(gestor => {
        return `
            <div class="card mb-3 gestor-card" data-id="${gestor.id_usuario}">
                <div class="card-body">
                    <h5 class="card-title">
                        <span class="material-icons-outlined">person</span>
                        ${gestor.nome}
                    </h5>
                    <p class="card-text"><strong>Email:</strong> ${gestor.email}</p>
                    <p class="card-text"><strong>Criado em:</strong> ${formatarData(gestor.data_criacao)}</p>
                    <p class="card-text"><strong>Último acesso:</strong> ${formatarData(gestor.ultimo_acesso)}</p>
                    
                    <div class="card-actions">
                        <button 
                            class="btn btn-danger btn-sm btn-excluir"
                            data-gestor-nome="${gestor.nome}" 
                        >
                            <span class="material-icons-outlined">delete_outline</span> Excluir
                        </button>
                        <button 
                            class="btn btn-secondary btn-sm btn-editar"
                        >
                            <span class="material-icons-outlined">edit</span> Editar
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    cardsContainer.innerHTML = cardsHtml;
}

/**
 * Filtra a lista 'todosGestores' com base no input de pesquisa e renderiza.
 */
function filtrarEExibirGestores() {
    const termo = barraPesquisa.value.toLowerCase().trim();
    if (!termo) {
        renderizarCards(todosGestores); // Mostra todos se a pesquisa estiver vazia
        return;
    }

    const gestoresFiltrados = todosGestores.filter(gestor => 
        gestor.nome.toLowerCase().includes(termo) ||
        gestor.email.toLowerCase().includes(termo)
    );
    renderizarCards(gestoresFiltrados);
}

// --- HANDLERS DE AÇÃO E MODAIS (CRUD) ---

/**
 * Abre o modal para ADICIONAR um novo gestor.
 */
function openAddGestorModal() {
    Swal.fire({
        title: 'Cadastrar Novo Gestor',
        html: `
            <input type="text" id="swal-nome" class="swal2-input" placeholder="Nome">
            <input type="email" id="swal-email" class="swal2-input" placeholder="Email">
            <input type="password" id="swal-senha" class="swal2-input" placeholder="Senha (mín. 8 caracteres)">
        `,
        customClass: swalCustomClasses(),
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        confirmButtonText: 'Cadastrar',
        focusConfirm: false,
        preConfirm: async () => {
            const nome = document.getElementById('swal-nome').value;
            const email = document.getElementById('swal-email').value;
            const senha = document.getElementById('swal-senha').value;

            if (!nome || !email || !senha) {
                Swal.showValidationMessage('Por favor, preencha todos os campos');
                return false;
            }
            if (senha.length < 8) {
                Swal.showValidationMessage('A senha deve ter pelo menos 8 caracteres');
                return false;
            }

            const payload = { nome, email, senha, tipo: 'gestor' };

            try {
                await apiFetch(API_ENDPOINTS.CREATE, 'POST', payload);
                return { nome }; // Sucesso
            } catch (error) {
                Swal.showValidationMessage(error.message);
                return false;
            }
        },
        allowOutsideClick: () => !Swal.isLoading()
    }).then(async (result) => {
        if (result.isConfirmed) {
            showSuccess('Novo gestor adicionado!', `<strong>${result.value.nome}</strong> já pode se conectar.`);
            await carregarEExibirGestores(); // Recarrega a lista
        }
    });
}

/**
 * Lida com o clique no botão "Editar". Encontra o gestor e abre o modal.
 * @param {number} id - O ID do gestor a ser editado.
 */
function handleEditClick(id) {
    const gestor = todosGestores.find(g => g.id_usuario === id);

    if (!gestor) {
        console.error('Gestor não encontrado no estado local. ID:', id);
        showError('Erro', 'Não foi possível encontrar os dados do gestor. Tente recarregar a página.');
        return;
    }

    openEditModal(gestor);
}

/**
 * Abre o modal para EDITAR um gestor existente.
 * @param {object} gestor - O objeto do gestor a ser editado.
 */
function openEditModal(gestor) {
    Swal.fire({
        title: 'Editar Gestor',
        html: `
            <input type="text" id="swal-nome" class="swal2-input" placeholder="Nome" value="${gestor.nome}">
            <input type="email" id="swal-email" class="swal2-input" placeholder="Email" value="${gestor.email}">
            <hr class="my-3">
            <small class="text-muted">Deixe em branco para não alterar a senha</small>
            <input type="password" id="swal-senha" class="swal2-input mt-2" placeholder="Nova Senha">
            <input type="password" id="swal-confirmar" class="swal2-input" placeholder="Confirmar Nova Senha">
        `,
        customClass: swalCustomClasses(),
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        confirmButtonText: 'Salvar Alterações',
        focusConfirm: false,
        preConfirm: async () => {
            const nome = document.getElementById('swal-nome').value;
            const email = document.getElementById('swal-email').value;
            const senha = document.getElementById('swal-senha').value;
            const confirmar = document.getElementById('swal-confirmar').value;

            if (!nome || !email) {
                Swal.showValidationMessage('Nome e Email são obrigatórios');
                return false;
            }

            const payload = { nome, email };

            if (senha) {
                if (senha.length < 8) {
                    Swal.showValidationMessage('A nova senha deve ter pelo menos 8 caracteres');
                    return false;
                }
                if (senha !== confirmar) {
                    Swal.showValidationMessage('As senhas não coincidem');
                    return false;
                }
                payload.senha = senha;
            }

            try {
                await apiFetch(API_ENDPOINTS.UPDATE(gestor.id_usuario), 'PUT', payload);
                return true; // Sucesso
            } catch (error) {
                Swal.showValidationMessage(error.message);
                return false;
            }
        },
        allowOutsideClick: () => !Swal.isLoading()
    }).then(async (result) => {
        if (result.isConfirmed) {
            showSuccess('Gestor Atualizado!', 'Os dados foram salvos.');
            await carregarEExibirGestores(); // Recarrega a lista
        }
    });
}

/**
 * Abre o modal de confirmação para EXCLUIR um gestor.
 * @param {number} id - O ID do gestor a ser excluído.
 * @param {string} nome - O nome do gestor (para exibição).
 * @param {HTMLElement} cardElement - O elemento do card no DOM (para remoção).
 */
function openDeleteModal(id, nome, cardElement) {
    Swal.fire({
        title: 'Confirmar Exclusão',
        html: `Tem certeza que deseja excluir o gestor <strong>${nome}</strong>?<br><br><strong class="text-danger">Esta ação não pode ser desfeita.</strong>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar',
        customClass: {
            ...swalCustomClasses(),
            confirmButton: 'swal-confirm-custom-danger',
        },
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                // Usando 'GET' conforme o seu backend parece esperar
                await apiFetch(API_ENDPOINTS.DELETE(id), 'GET'); 
                
                showSuccess('Gestor removido!');
                
                // Remove localmente para feedback instantâneo
                cardElement.remove();
                todosGestores = todosGestores.filter(g => g.id_usuario !== id);
                if (todosGestores.length === 0) {
                    renderizarCards([]); // Mostra mensagem de "vazio"
                }

            } catch (error) {
                showError('Erro ao Remover Gestor', error.message);
            }
        }
    });
}


// --- FUNÇÃO WRAPPER DE API (Centralizada) ---

/**
 * Wrapper centralizado para todas as chamadas 'fetch'.
 * Lida com autenticação, body e erros comuns (como sessão expirada).
 * @param {string} endpoint - A URL da API para chamar.
 * @param {string} [method='GET'] - O método HTTP (GET, POST, PUT, DELETE).
 * @param {object} [body=null] - O corpo da requisição (para POST/PUT).
 * @returns {Promise<any>} - A resposta JSON da API.
 */
async function apiFetch(endpoint, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': session_token
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(endpoint, options);
        
        // Verifica se a resposta é um HTML (provável redirect de login)
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            // Se o status não for OK, é um erro (ex: 401, 302)
            if (!response.ok) {
                throw new Error('Sua sessão pode ter expirado. Tente fazer login novamente.');
            }
            // Se for OK mas não for JSON, é uma resposta inesperada
            throw new Error('O servidor retornou uma resposta em formato inesperado.');
        }
        
        const data = await response.json();

        if (!response.ok) {
            // A API retornou um JSON de erro (ex: { "error": "..." })
            throw new Error(data.error || 'Ocorreu um erro desconhecido na API.');
        }

        return data; // Sucesso

    } catch (error) {
        // Pega o erro 'Unexpected token <' que acontece se o 'try' falhar
        if (error instanceof SyntaxError) {
            throw new Error('Sua sessão expirou. Por favor, faça login novamente.');
        }
        // Re-lança o erro (seja o que criamos ou outro)
        throw error;
    }
}


// --- FUNÇÕES UTILITÁRIAS ---

/**
 * Retorna as classes CSS customizadas para os modais SweetAlert.
 */
function swalCustomClasses() {
    return {
        popup: 'swal-popup-custom',
        confirmButton: 'swal-confirm-custom',
        cancelButton: 'swal-cancel-custom',
    };
}

/**
 * Exibe um modal SweetAlert de sucesso.
 * @param {string} title - O título do modal.
 * @param {string} [html=''] - O conteúdo HTML opcional.
 * @param {number} [timer=2000] - O tempo para fechar automaticamente.
 */
function showSuccess(title, html = '', timer = 2000) {
    Swal.fire({
        icon: 'success',
        title: title,
        html: html,
        timer: timer,
        showConfirmButton: false,
        customClass: { popup: 'swal-popup-custom' }
    });
}

/**
 * Exibe um modal SweetAlert de erro.
 * @param {string} title - O título do modal.
 * @param {string} text - O texto de explicação do erro.
 */
function showError(title, text) {
    Swal.fire({
        icon: 'error',
        title: title,
        text: text,
        confirmButtonColor: 'var(--verde-claro-medio)',
        customClass: { popup: 'swal-popup-custom' }
    });
}

/**
 * Formata uma data (string, timestamp) para o padrão dd/mm/aaaa (diferença).
 * @param {string | number} input - A data de entrada.
 * @returns {string} - A data formatada.
 */
function formatarData(input) {
    if (!input) return 'Não registrado';
    const d = new Date(input);
    if (isNaN(d.getTime())) {
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
    
    if (diffDias === 0) return `${dataFormatada} (Hoje)`;
    if (diffDias === 1) return `${dataFormatada} (há 1 dia)`;
    return `${dataFormatada} (há ${diffDias} dias)`;
} 