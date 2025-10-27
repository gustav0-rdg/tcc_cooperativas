// Adcionar gestor
function addGestor() {
    Swal.fire({
        title: 'Cadastrar Novo Gestor',
        html: `
            <input type="text" id="id" class="swal2-input" placeholder="ID">
            <input type="text" id="nome" class="swal2-input" placeholder="Nome">
            <input type="email" id="email" class="swal2-input" placeholder="Email">
        `,
        confirmButtonText: 'Cadastrar',
        focusConfirm: false,
        preConfirm: () => {
            const id = document.getElementById('id').value;
            const nome = document.getElementById('nome').value;
            const email = document.getElementById('email').value;

            if (!id || !nome || !email) {
                Swal.showValidationMessage('Por favor, preencha todos os campos');
                return false;
            }

            const createdAt = new Date().toLocaleString();
            const lastAccess = "Nunca";

            // Adiciona o gestor como um card
            const cardsContainer = document.getElementById('gestoresCards');
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h5>${nome} (ID: ${id})</h5>
                <p>Email: ${email}</p>
                <p>Criado em: ${createdAt}</p>
                <p>Último acesso: ${lastAccess}</p>
                <button class="btn btn-danger btn-sm" onclick="confirmDelete(this)">Excluir</button>
            `;
            cardsContainer.appendChild(card);
        }
    });
}

// Confirmar exclusão
function confirmDelete(button) {
    const card = button.closest('.card');
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();

    document.getElementById('confirmDeleteButton').onclick = () => {
        card.remove();
        modal.hide();
    };
}