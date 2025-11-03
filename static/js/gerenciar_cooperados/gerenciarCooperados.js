// --- Funções de Renderização e UI ---

function getAddEditFormHtml(cooperado = {}) {
    // Define valores padrão para um novo cooperado ou usa os existentes
    const isEdit = !!cooperado.cpf;
    const defaults = {
        nome: '',
        cpf: '',
        telefone: '',
        cep: '',
        endereco: '',
        numero: '',
        bairro: '',
        cidade: '',
        estado: '',
        vinculo: '',
        desvinculo: 'Ativo',
        ...cooperado // Sobrescreve os padrões se 'cooperado' for fornecido
    };

    // CPF fica 'readonly' se for modo de edição
    const cpfReadonly = isEdit ? 'readonly style="background: #eee;"' : '';

    return `
        <input type="text" id="nome" class="swal2-input" placeholder="Nome Completo" value="${defaults.nome}">
        
        <input type="text" id="cpf" class="swal2-input" placeholder="CPF (será o login)" value="${defaults.cpf}" 
            oninput="formatCPF(this)" ${cpfReadonly}>
        
        <input type="password" id="senha" class="swal2-input" placeholder="Senha (mín. 8 caracteres)">
        
        <input type="text" id="telefone" class="swal2-input" placeholder="Telefone" value="${defaults.telefone}" 
            oninput="formatTelefone(this)">
        
        <hr>
        
        <input type="text" id="cep" class="swal2-input" placeholder="CEP" value="${defaults.cep}" 
            oninput="formatCEP(this)" 
            onblur="buscarCep(this.value)">
            
        <input type="text" id="endereco" class="swal2-input" placeholder="Endereço (Rua, Av...)" value="${defaults.endereco}">
        <input type="text" id="numero" class="swal2-input" placeholder="Número" value="${defaults.numero}">
        <input type="text" id="bairro" class="swal2-input" placeholder="Bairro" value="${defaults.bairro}">
        <input type="text" id="cidade" class="swal2-input" placeholder="Cidade" value="${defaults.cidade}">
        <input type="text" id="estado" class="swal2-input" placeholder="Estado (Ex: SP)" value="${defaults.estado}">
        
        <hr>
        
        <label for="vinculo" class="swal2-label">Data de Vínculo:</label>
        <input type="date" id="vinculo" class="swal2-input" value="${defaults.vinculo}">
        
        <label for="desvinculo" class="swal2-label">Status (Ex: Ativo):</label>
        <input type="text" id="desvinculo" class="swal2-input" value="${defaults.desvinculo}">
    `;
}

// Pega os dados do formulário do SweetAlert
function getFormData() {
    return {
        nome: document.getElementById('nome').value,
        cpf: document.getElementById('cpf').value,
        senha: document.getElementById('senha').value,
        telefone: document.getElementById('telefone').value,
        cep: document.getElementById('cep').value,
        endereco: document.getElementById('endereco').value,
        numero: document.getElementById('numero').value,
        bairro: document.getElementById('bairro').value,
        cidade: document.getElementById('cidade').value,
        estado: document.getElementById('estado').value,
        vinculo: document.getElementById('vinculo').value,
        desvinculo: document.getElementById('desvinculo').value,
    };
}

// Adicionar um card de cooperado na tela
function addCooperadoCard(cooperado) {
    const cardsContainer = document.getElementById('cooperadoCards');
    const card = document.createElement('div');
    card.className = 'card mb-3 cooperado-card cooperado-card-clickable'; 
    
    // Armazena dados para busca e clique
    card.dataset.nome = (cooperado.nome || '').toLowerCase(); 
    card.dataset.cpf = (cooperado.cpf || '').toLowerCase(); 

    if (cooperado.cpf) {
        card.setAttribute('onclick', `showCooperadoDetails('${cooperado.cpf}')`);
    } else {
        card.style.cursor = 'default'; 
    }

    card.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">${cooperado.nome || 'Nome não cadastrado'}</h5>
            <p class="card-text">CPF: ${cooperado.cpf || 'CPF não cadastrado'}</p>
            <p class="card-text">Telefone: ${cooperado.telefone || 'Telefone não cadastrado'}</p>
        </div>
    `;
    cardsContainer.appendChild(card);
}

// --- Funções de Ação (CRUD na UI) ---

// Adicionar novo cooperado
function addCooperado() {
    Swal.fire({
        title: 'Cadastrar Novo Cooperado',
        html: getAddEditFormHtml(), // Usa o gerador de formulário
        customClass: {
            cancelButton: 'order-1 right-gap',
            confirmButton: 'order-2',
        },
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        confirmButtonText: 'Cadastrar',
        confirmButtonColor: '#6AB633',
        focusConfirm: false,
        width: '800px', // Modal maior para o formulário

        preConfirm: () => {
            const data = getFormData();

            // Validação
            if (!data.nome || !data.cpf || !data.senha) {
                Swal.showValidationMessage('Nome, CPF e Senha são obrigatórios');
                return false;
            }
            if (data.senha.length < 8) {
                Swal.showValidationMessage('A senha deve ter pelo menos 8 caracteres');
                return false;
            }
            if (cooperadoService.cpfExists(data.cpf)) {
                Swal.showValidationMessage('Este CPF já está cadastrado');
                return false;
            }

            const cooperado = {
                ...data,
                createdAt: new Date().toLocaleString(),
                lastAccess: "Nunca",
                desvinculo: data.desvinculo || "Ativo",
            };

            cooperadoService.save(cooperado);
            addCooperadoCard(cooperado); // Adiciona o card na tela
        }
    });
}

// Mostrar detalhes do cooperado
function showCooperadoDetails(cpf) {
    const cooperado = cooperadoService.getByCpf(cpf);
    if (!cooperado) return;

    // Formata o endereço
    const enderecoCompleto = [
        cooperado.endereco,
        cooperado.numero,
        cooperado.bairro,
        cooperado.cidade,
        cooperado.estado
    ].filter(Boolean).join(', '); // Filtra nulos/vazios e junta com vírgula

    Swal.fire({
        title: cooperado.nome,
        html: `
            <div style="text-align: left; padding: 0 1rem;">
                <p><strong>CPF:</strong> ${cooperado.cpf}</p>
                <p><strong>Telefone:</strong> ${cooperado.telefone}</p>
                <p><strong>Endereço:</strong> ${enderecoCompleto || 'Não informado'}</p>
                <p><strong>Vínculo:</strong> ${cooperado.vinculo ? new Date(cooperado.vinculo + 'T00:00:00').toLocaleDateString('pt-BR') : 'Não informado'}</p>
                <p><strong>Status:</strong> ${cooperado.desvinculo}</p>
                <p><strong>Último acesso:</strong> ${cooperado.lastAccess}</p>
            </div>
        `,
        showCloseButton: true,
        showCancelButton: true,
        showDenyButton: true,
        confirmButtonText: 'Editar',
        confirmButtonColor: '#6AB633',
        denyButtonText: 'Excluir',
        denyButtonColor: '#d33',
        cancelButtonText: 'Fechar',
    }).then((result) => {
        if (result.isConfirmed) editCooperado(cpf);
        else if (result.isDenied) confirmDelete(cpf);
    });
}

// Editar o cooperado
function editCooperado(cpf) {
    const cooperado = cooperadoService.getByCpf(cpf);
    if (!cooperado) return;

    Swal.fire({
        title: 'Editar Cooperado',
        html: getAddEditFormHtml(cooperado), 
        confirmButtonText: 'Salvar',
        confirmButtonColor: '#6AB633',
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        focusConfirm: false,
        width: '800px',

        preConfirm: () => {
            const data = getFormData();

            // Validação
            if (!data.nome || !data.cpf) {
                Swal.showValidationMessage('Nome e CPF são obrigatórios');
                return false;
            }
            
            // Cria o objeto atualizado
            const updatedCooperado = {
                // Pega os dados antigos (como createdAt, lastAccess)
                ...cooperado, 
                // Sobrescreve com os dados do formulário
                ...data,      
            };

            // Só atualiza a senha se uma nova foi digitada
            if (data.senha) {
                if (data.senha.length < 8) {
                    Swal.showValidationMessage('A nova senha deve ter pelo menos 8 caracteres');
                    return false;
                }
                updatedCooperado.senha = data.senha;
            } else {
                // Se a senha ficou em branco, mantém a senha antiga
                updatedCooperado.senha = cooperado.senha;
            }
            
            loadCooperados(); 
            // Recarrega todos os cards
            cooperadoService.save(updatedCooperado);
        }
    });
}

// Confirma a exclusão de um cooperado
function confirmDelete(cpf) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Você não poderá reverter isso!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            cooperadoService.delete(cpf);
            loadCooperados(); // Recarrega a lista
            Swal.fire('Excluído!', 'O cooperado foi removido.', 'success');
        }
    });
}

// --- Funções de Carga e Pesquisa ---

// Carrega os cooperados do Service e exibe na tela
function loadCooperados() {
    const cardsContainer = document.getElementById('cooperadoCards');
    cardsContainer.innerHTML = ''; // Limpa a tela
    
    const cooperados = cooperadoService.getAll();
    cooperados.forEach(cooperado => addCooperadoCard(cooperado));
}

// Pesquisar os cooperados (por nome ou CPF)
function searchCooperados() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.cooperado-card');

    cards.forEach(card => {
        const nome = card.dataset.nome;
        const cpf = card.dataset.cpf;
        if (nome.includes(searchInput) || cpf.includes(searchInput)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Adiciona o evento de pesquisa ao campo de entrada
document.getElementById('searchInput').addEventListener('input', searchCooperados);

// Carrega os cooperados ao iniciar a página
document.addEventListener('DOMContentLoaded', loadCooperados);