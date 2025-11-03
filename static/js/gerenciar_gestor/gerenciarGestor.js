const session_token = localStorage.getItem('session_token');
const cardsContainer = document.getElementById('gestoresCards');

async function consultarGestores ()
{
    const response = await fetch (
        
        '/api/usuarios/get-all-gestores', 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data_gestores = await response?.json();

    if (!response.ok)
    {
        throw new Error (

            'error' in data_gestores
            ?
            data_gestores.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_gestores;
}

function renderizarCards (listaGestores)
{

    listaGestores = listaGestores.map(gestor => {

        return `
            <div
                class="card mb-3 gestor-card"
                dataset-nome="${gestor.nome}"
                dataset-email="${gestor.email}"
            >
                <div class="card-body">
                    <h5 class="card-title">${gestor.nome}</h5>
                    <p class="card-text">Email: ${gestor.email}</p>
                    <p class="card-text">Criado em: ${formatarData(gestor.data_criacao)}</p>
                    <p class="card-text">Último acesso: ${formatarData(gestor.ultimo_acesso)}</p>
                    <p class="card-text">
                    </p>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete(this, '${gestor.email}')">Excluir</button>
                    <button class="btn btn-secondary btn-sm" onclick="editGestor('${gestor.email}')">Editar</button>
                </div>
            </div>
        `;

    });

    console.log(listaGestores);

    cardsContainer.innerHTML = listaGestores.join(' ');

}

async function exibirGestores ()
{
    const gestores = await consultarGestores();
    renderizarCards(gestores);
}

function formatarData(input) 
{
    if (!input) return 'Não registrado';
    // aceita string de data do backend (e.g. "Sat, 16 Mar 2024 11:10:00 GMT")
    const d = new Date(input);
    if (isNaN(d.getTime())) {
        // se veio como timestamp em segundos
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

document.addEventListener('DOMContentLoaded', async function () {
    
    if (!session_token) window.location.href = URL_LOGIN_ADMIN;

    exibirGestores();
});

// Adicionar gestor
function addGestor() {
    
    Swal.fire({
        title: 'Cadastrar Novo Gestor',
        html: `
            <input type="text" id="nome" class="swal2-input" placeholder="Nome">
            <input type="email" id="email" class="swal2-input" placeholder="Email">
            <input type="password" id="senha" class="swal2-input" placeholder="Senha">
        `,
        
        customClass: {
            cancelButton: 'order-1 right-gap',
            confirmButton: 'order-2',
        },
        
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        
        confirmButtonText: 'Cadastrar',
        confirmButtonColor: '#6AB633',
        
        focusConfirm: false,

        preConfirm: () => {

            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;
            const senha = document.getElementById('senha').value;

            if (!nome || !email || !senha) {
                Swal.showValidationMessage('Por favor, preencha todos os campos');
                return false;
            }

            const createdAt = new Date().toLocaleString();
            const lastAccess = "Nunca";

            // Cria o objeto do gestor
            const gestor = { nome, email, senha, createdAt, lastAccess };

            // Salva no Local Storage
            saveGestorToLocalStorage(gestor);

            // Adiciona o gestor como um card
            addGestorCard(gestor);

        }
    });
}

// Editar o gestor
function editGestor(email) {

    const gestores = JSON.parse(localStorage.getItem('gestores')) || [];
    const gestor = gestores.find(g => g.email === email);

    if (!gestor) {
        Swal.fire('Erro', 'Gestor não encontrado', 'error');
        return;
    }

    Swal.fire({
        title: 'Editar Gestor',
        html: `
            <input type="text" id="editNome" class="swal2-input" placeholder="Nome" value="${gestor.nome}">
            <input type="email" id="editEmail" class="swal2-input" placeholder="Email" value="${gestor.email}">
            <input type="password" id="editSenha" class="swal2-input" placeholder="Nova Senha" value="${gestor.senha}">
            <input type="password" id="confirmarSenha" class="swal2-input" placeholder="Confirmar Senha" value="${gestor.senha}">
        `,
        confirmButtonText: 'Salvar',
        confirmButtonColor: '#6AB633',
        focusConfirm: false,

        preConfirm: () => {

            const nome = document.getElementById('editNome').value;
            const newEmail = document.getElementById('editEmail').value;
            const senha = document.getElementById('editSenha').value;
            const confirmarSenha = document.getElementById('confirmarSenha').value;

            // validando os campos se estão preenchidos
            if (!nome || !newEmail || !senha || !senha) {

                Swal.showValidationMessage('Por favor, preencha todos os campos');

                return false;
            }

            // validando se as senhas coincidem
            if (senha !== confirmarSenha) {

                Swal.showValidationMessage('As senhas não coincidem');

                return false;
            }

            // Atualiza os dados do gestor
            gestor.nome = nome;
            gestor.email = newEmail;
            gestor.senha = senha;

            // Atualiza o Local Storage
            localStorage.setItem('gestores', JSON.stringify(gestores));

            // Atualiza os cards na tela
            document.getElementById('gestoresCards').innerHTML = '';

            // Recarrega os gestores
            loadGestoresFromLocalStorage();
        }
    });
}

// Confirma a exclusão de um gestor
function confirmDelete(button, email) {

    const card = button.closest('.card');
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));

    // Mostra o modal de confirmação
    modal.show();

    // Configura o botão de confirmação
    document.getElementById('confirmDeleteButton').onclick = () => {

        // Remove o card da tela
        card.remove();

        // Remove do Local Storage
        deleteGestorFromLocalStorage(email);

        // Esconde o modal
        modal.hide();
    };
}

// Deletar gestor do Local Storage
function deleteGestorFromLocalStorage(email) {

    // Pega os gestores do Local Storage
    let gestores = JSON.parse(localStorage.getItem('gestores')) || [];

    // Filtra o gestor que será removido
    gestores = gestores.filter(gestor => gestor.email !== email);

    // Salva os gestores atualizados no Local Storage
    localStorage.setItem('gestores', JSON.stringify(gestores));

}

// Pesquisar os gestores
function searchGestores() {

    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.gestor-card');

    cards.forEach(card => {

        const nome = card.dataset.nome;

        const email = card.dataset.email;

        if (nome.includes(searchInput) || email.includes(searchInput)) {
            card.style.display = 'block';
        } 

        else{
            card.style.display = 'none';
        }
    });
}