// Adicionar gestor
function addGestor() {
    Swal.fire({
        title: 'Cadastrar Novo Gestor',
        html: `
            <input type="text" id="nome" class="swal2-input" placeholder="Nome">
            <input type="email" id="email" class="swal2-input" placeholder="Email">
            <input type="password" id="senha" class="swal2-input" placeholder="Senha">
        `,
        confirmButtonText: 'Cadastrar',
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

    card.className = 'card mb-3';
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
        </div>
    `;

    cardsContainer.appendChild(card);
}

// Visiblidade da senha
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

// Carrega os gestores que estavam salvos no Local Storage ao iniciar a página
document.addEventListener('DOMContentLoaded', loadGestoresFromLocalStorage);