
// --- Event Listeners  ---
document.getElementById('searchInput').addEventListener('input', searchCooperados);
document.addEventListener('DOMContentLoaded', loadCooperados);

// --- Funções de Renderização e UI ---

function getAddEditFormHtml(cooperado = {}) {

    const isEdit = !!cooperado.cpf;

    const defaults = {
        nome: '', cpf: '', telefone: '', cep: '',
        endereco: '', numero: '', bairro: '', cidade: '', estado: '',
        vinculo: '', desvinculo: 'Ativo', ...cooperado 
    };

    const cpfReadonly = isEdit ? 'readonly' : '';

    const senhaPlaceholder = isEdit ? 'Nova Senha (deixe em branco para manter)' : 'Senha (mín. 8 caracteres)';

    const selectedAtivo = (defaults.desvinculo === 'Ativo' || !defaults.desvinculo) ? 'selected' : '';

    const selectedInativo = defaults.desvinculo === 'Inativo' ? 'selected' : '';


    return `
    <div class="swal-form-container">

        <input type="text" id="nome" class="swal2-input" placeholder="Nome Completo" value="${defaults.nome}">
        
        <input type="text" id="cpf" class="swal2-input" placeholder="CPF" value="${defaults.cpf}" 
            oninput="formatCPF(this)" ${cpfReadonly}>
        
        <input type="password" id="senha" class="swal2-input" placeholder="${senhaPlaceholder}">
        
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
        
        <label for="desvinculo" class="swal2-label">Status:</label>
        <select id="desvinculo" class="swal2-input">
            <option value="Ativo" ${selectedAtivo}>Ativo</option>
            <option value="Inativo" ${selectedInativo}>Inativo</option>
        </select>

        </div>
    `;
}

// Pega os dados do formulário do SweetAlert
function getFormData() {

    // Retorna um objeto com os valores dos campos do formulário

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

    card.className = 'card cooperado-card cooperado-card-clickable'; 
    
    card.dataset.nome = (cooperado.nome || '').toLowerCase(); 

    card.dataset.cpf = (cooperado.cpf || '').toLowerCase(); 

    if (cooperado.cpf) {

        card.setAttribute('onclick', `showCooperadoDetails('${cooperado.cpf}')`);

    } else {
        
        card.style.cursor = 'default';

    }

    card.innerHTML = 
    `
        <div class="card-body">

            <h5 class="card-title">${cooperado.nome || 'Nome não cadastrado'}</h5>

            <p class="card-text">CPF: ${cooperado.cpf || 'CPF não cadastrado'}</p>

            <p class="card-text">Telefone: ${cooperado.telefone || 'Telefone não cadastrado'}</p>

        </div>
    `;

    cardsContainer.appendChild(card);
}

// --- Funções de Ação  ---

// Adicionar novo cooperado
function addCooperado() {

    Swal.fire({

        title: 'Cadastrar Novo Cooperado',

        html: getAddEditFormHtml(),

        customClass: {
            popup: 'swal-wide',
        },

        showCancelButton: true,

        cancelButtonText: 'Cancelar',

        confirmButtonText: 'Cadastrar',

        confirmButtonColor: 'var(--verde-principal)',

        focusConfirm: false,

        preConfirm: () => {

            const data = getFormData();

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

                desvinculo: data.desvinculo, 
            };

            cooperadoService.save(cooperado);

            addCooperadoCard(cooperado);
        }
    });
}

// Mostrar detalhes do cooperado
function showCooperadoDetails(cpf) {

    const cooperado = cooperadoService.getByCpf(cpf);

    if (!cooperado) return;

    const enderecoCompleto = [

        cooperado.endereco, cooperado.numero, cooperado.bairro,

        cooperado.cidade, cooperado.estado

    ].filter(Boolean).join(', ');

    Swal.fire({

        title: cooperado.nome,

        customClass: {
            popup: 'swal-details',
        },
        
        html: `
            <dl class="details-list">
                <dt>CPF</dt>
                <dd>${cooperado.cpf}</dd>
                <dt>Telefone</dt>
                <dd>${cooperado.telefone || 'Não informado'}</dd>
                <dt>Endereço</dt>
                <dd>${enderecoCompleto || 'Não informado'}</dd>
                <dt>Vínculo</dt>
                <dd>${cooperado.vinculo ? new Date(cooperado.vinculo + 'T00:00:00').toLocaleDateString('pt-BR') : 'Não informado'}</dd>
                <dt>Status</dt>
                <dd>${cooperado.desvinculo}</dd>
                <dt>Último Acesso</dt>
                <dd>${cooperado.lastAccess}</dd>
            </dl>
        `,
        showCloseButton: true,

        showCancelButton: true,

        showDenyButton: true,

        confirmButtonText: 'Editar',

        confirmButtonColor: 'var(--verde-principal)',

        denyButtonText: 'Excluir',

        denyButtonColor: 'var(--vermelho)',

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
        
        customClass: {
            popup: 'swal-wide',
        },

        confirmButtonText: 'Salvar',

        confirmButtonColor: 'var(--verde-principal)',

        showCancelButton: true,

        cancelButtonText: 'Cancelar',

        focusConfirm: false,

        preConfirm: () => {

            const data = getFormData(); 

            if (!data.nome || !data.cpf) {

                Swal.showValidationMessage('Nome e CPF são obrigatórios');

                return false;
            }
            
            const updatedCooperado = { ...cooperado, ...data };

            if (data.senha) {
                if (data.senha.length < 8) {

                    Swal.showValidationMessage('A nova senha deve ter pelo menos 8 caracteres');

                    return false;

                }

                updatedCooperado.senha = data.senha;
            } else {

                updatedCooperado.senha = cooperado.senha;

            }

            cooperadoService.save(updatedCooperado);

            loadCooperados();
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
        confirmButtonColor: 'var(--vermelho)',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    
    }).then((result) => {
        if (result.isConfirmed) {
            cooperadoService.delete(cpf);
            loadCooperados();
            Swal.fire('Excluído!', 'O cooperado foi removido.', 'success');
        }
    });
}

// --- Funções de Carga e Pesquisa ---

function loadCooperados() {

    const cardsContainer = document.getElementById('cooperadoCards');

    cardsContainer.innerHTML = '';
    
    const cooperados = cooperadoService.getAll();

    cooperados.forEach(cooperado => addCooperadoCard(cooperado));
}

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

