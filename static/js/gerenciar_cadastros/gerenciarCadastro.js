/* /static/js/gerenciar_cadastros/gerenciar_cadastros.js */

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('solicitacoesContainer');

    if (container) {
        // Usamos delegação de eventos
        container.addEventListener('click', function(e) {
            const approveButton = e.target.closest('.btn-approve');
            const rejectButton = e.target.closest('.btn-reject');

            if (approveButton) {
                e.preventDefault();
                handleAcaoCadastro(approveButton, 'aprovar');
            } else if (rejectButton) {
                e.preventDefault();
                handleAcaoCadastro(rejectButton, 'rejeitar');
            }
        });
    }
});

/**
 * Lida com a ação (aprovar ou rejeitar) de um cadastro.
 * @param {HTMLElement} button O botão que foi clicado.
 * @param {string} acao 'aprovar' ou 'rejeitar'.
 */
function handleAcaoCadastro(button, acao) {
    const card = button.closest('.solicitacao-card');
    const solicitacaoId = card.dataset.id;
    const solicitacaoEmail = card.dataset.email;

    // Configurações do SweetAlert
    let config = {
        title: 'Você tem certeza?',
        html: `Você deseja <strong>${acao}</strong> o cadastro de <br><strong>${solicitacaoEmail}</strong>?`,
        icon: 'warning',
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    };

    if (acao === 'aprovar') {
        config.confirmButtonText = 'Sim, aprovar!';
        config.confirmButtonColor = 'var(--verde-principal)';
    } else {
        config.title = 'Rejeitar Cadastro?';
        config.icon = 'error';
        config.confirmButtonText = 'Sim, rejeitar!';
        config.confirmButtonColor = 'var(--vermelho)';
        
        // Pergunta o motivo da rejeição
        config.input = 'textarea';
        config.inputPlaceholder = 'Digite o motivo da rejeição (será enviado ao usuário)...';
        config.inputValidator = (value) => {
            if (!value) {
                return 'Você precisa informar um motivo para a rejeição!';
            }
        };
    }

    // Exibe o modal do SweetAlert
    Swal.fire(config).then((result) => {
        if (result.isConfirmed) {
            // O usuário confirmou
            
            // Monta a URL e o corpo da requisição
            const url = `/gestores/cadastros/${solicitacaoId}/${acao}`;
            const body = {};

            if (acao === 'rejeitar') {
                body.motivo = result.value; // Pega o motivo do input
            }

            // Envia a requisição para o backend
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Adicionar 'X-CSRF-TOKEN' se você usar CSRF
                },
                body: JSON.stringify(body)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'Sucesso!',
                        text: data.message || 'Ação realizada com sucesso.',
                        icon: 'success',
                        confirmButtonColor: 'var(--verde-principal)'
                    }).then(() => {
                        // Recarrega a página para remover o card
                        location.reload(); 
                    });
                } else {
                    throw new Error(data.message || 'Erro ao realizar a ação.');
                }
            })
            .catch(error => {
                Swal.fire(
                    'Erro!',
                    error.message || 'Não foi possível completar a ação.',
                    'error'
                );
            });
        }
    });
}