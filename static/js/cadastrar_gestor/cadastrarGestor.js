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

// Salva o gestor no Local Storage
function saveGestorToLocalStorage(gestor) {
    let gestores = JSON.parse(localStorage.getItem('gestores')) || [];
    gestores.push(gestor);
    localStorage.setItem('gestores', JSON.stringify(gestores));
}

// Carrega os gestores do Local Storage
function loadGestoresFromLocalStorage() {
    const gestores = JSON.parse(localStorage.getItem('gestores')) || [];
    gestores.forEach(gestor => addGestorCard(gestor));
}

// Adicionar um card de gestor na tela
function addGestorCard(gestor) {
    const cardsContainer = document.getElementById('gestoresCards');
    const card = document.createElement('div');

    card.className = 'card mb-3 gestor-card';
    // Armazena o nome em minúsculas para facilitar a busca
    card.dataset.nome = gestor.nome.toLowerCase(); 
    // Armazena o email em minúsculas para facilitar a busca
    card.dataset.email = gestor.email.toLowerCase(); 
    card.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">${gestor.nome}</h5>
            <p class="card-text">Email: ${gestor.email}</p>
            <p class="card-text">Criado em: ${gestor.createdAt}</p>
            <p class="card-text">Último acesso: ${gestor.lastAccess}</p>
            <p class="card-text">
                Senha: 
                <span class="password-container">
                    <span class="password" style="font-weight: bold;">******</span>
                    <i class="material-icons" style="cursor: pointer;" onclick="togglePasswordVisibility(this, '${gestor.senha}')">visibility</i>
                </span>
            </p>
            <button class="btn btn-danger btn-sm" onclick="confirmDelete(this, '${gestor.email}')">Excluir</button>
            <button class="btn btn-secondary btn-sm" onclick="editGestor('${gestor.email}')">Editar</button>
        </div>
    `;

    cardsContainer.appendChild(card);
}

// Função para alternar a visibilidade da senha
function togglePasswordVisibility(icon, senha) {
    const passwordSpan = icon.previousElementSibling;
    if (passwordSpan.textContent === "******") {
        // Mostra a senha
        passwordSpan.textContent = senha; 
        // Altera o ícone para "ocultar"
        icon.textContent = "visibility_off";
    } else {
        // Oculta a senha
        passwordSpan.textContent = "******"; 
        // Altera o ícone para "mostrar"
        icon.textContent = "visibility"; 
    }
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
            <input type="password" id="editSenha" class="swal2-input" placeholder="Senha" value="${gestor.senha}">
        `,
        confirmButtonText: 'Salvar',
        confirmButtonColor: '#6AB633',
        focusConfirm: false,
        preConfirm: () => {
            const nome = document.getElementById('editNome').value;
            const newEmail = document.getElementById('editEmail').value;
            const senha = document.getElementById('editSenha').value;

            if (!nome || !newEmail || !senha) {
                Swal.showValidationMessage('Por favor, preencha todos os campos');
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
            loadGestoresFromLocalStorage();
        }
    });
}

// Confirma a exclusão de um gestor
function confirmDelete(button, email) {
    const card = button.closest('.card');
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));

    modal.show();

    document.getElementById('confirmDeleteButton').onclick = () => {
        card.remove();
        deleteGestorFromLocalStorage(email);
        modal.hide();
    };
}

// Deletar gestor do Local Storage
function deleteGestorFromLocalStorage(email) {
    let gestores = JSON.parse(localStorage.getItem('gestores')) || [];
    gestores = gestores.filter(gestor => gestor.email !== email);
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
        } else {
            card.style.display = 'none';
        }
    });
}

// Adiciona o evento de pesquisa ao campo de entrada
document.getElementById('searchInput').addEventListener('input', searchGestores);

// Carrega os gestores que estavam salvos no Local Storage ao iniciar a página
document.addEventListener('DOMContentLoaded', loadGestoresFromLocalStorage);