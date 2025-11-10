document.addEventListener('DOMContentLoaded', function() {
    // 1. Verifica se o gestor está logado (procurando o token)
    const token = localStorage.getItem('session_token');
    
    if (!token) {
        // Se não houver token, expulsa o utilizador
        Swal.fire('Erro', 'Acesso negado. Faça o login como gestor.', 'error')
            .then(() => window.location.href = '/login-admin');
        return;
    }
    
    // 2. Se estiver logado, carrega as solicitações pendentes
    carregarSolicitacoes(token);
});

/**
 * Busca as solicitações pendentes na API e manda desenhar os cards
 * @param {string} token - O token de sessão do gestor
 */
async function carregarSolicitacoes(token) {
    const container = document.getElementById('solicitacoesContainer');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noSolicitacoesAlert = document.getElementById('no-solicitacoes-alert');
    const resultsCount = document.getElementById('resultsCount'); // Assumindo que tens um span com este ID

    try {
        // Chama a rota da API que vamos criar no Passo 3
        const response = await fetch('/get/cooperativas-pendentes', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        // Esconde o spinner de qualquer forma
        loadingSpinner.style.display = 'none';

        const data = await response.json();

        if (!response.ok) {
            // O erro 404 vai cair aqui
            throw new Error(data.error || 'Erro ao buscar solicitações');
        }

        if (data.length === 0) {
            // Se não houver dados, mostra o alerta de "nada pendente"
            noSolicitacoesAlert.style.display = 'block';
            if(resultsCount) resultsCount.textContent = 'Nenhuma solicitação pendente.';
        } else {
            // Se houver dados, cria os cards
            if(resultsCount) resultsCount.textContent = `Exibindo ${data.length} solicitação(ões) pendente(s).`;
            data.forEach(solicitacao => {
                const card = criarCardSolicitacao(solicitacao, token);
                container.appendChild(card);
            });
        }

    } catch (error) {
        console.error('Erro em carregarSolicitacoes:', error);
        loadingSpinner.style.display = 'none';
        if(resultsCount) resultsCount.textContent = 'Erro ao carregar solicitações.';
        Swal.fire('Erro', error.message, 'error');
    }
}

/**
 * Cria o elemento HTML (o card) para uma única solicitação
 */
function criarCardSolicitacao(solicitacao, token) {
    const col = document.createElement('div');
    col.className = 'col-lg-4 col-md-6 mb-4';
    
    const dataCadastro = new Date(solicitacao.data_cadastro).toLocaleDateString('pt-BR');
    
    // Verifica se há um documento para baixar
    const temDocumento = solicitacao.arquivo_url;
    const downloadButton = `
        <a href="/static/${solicitacao.arquivo_url}" 
           target="_blank" 
           class="btn-download" 
           ${!temDocumento ? 'disabled title="Nenhum documento enviado"' : 'title="Baixar documento de comprovação"'}>
            <i class="fas fa-file-download"></i> 
            ${temDocumento ? 'Baixar Documento' : 'Sem Documento'}
        </a>
    `;

    // Cria o HTML do card
    col.innerHTML = `
        <div class="solicitacao-card" data-id="${solicitacao.id_cooperativa}" data-email="${solicitacao.email}">
            <div class="solicitacao-card-header">
                <h5>${solicitacao.razao_social}</h5>
                <span class="badge bg-warning text-dark">Aguardando Análise</span>
            </div>
            <div class="solicitacao-card-body">
                <p><strong>CNPJ:</strong> ${solicitacao.cnpj}</p>
                <p><strong>E-mail:</strong> ${solicitacao.email}</p>
                <p><strong>Solicitado em:</strong> ${dataCadastro}</p>
                ${downloadButton}
            </div>
            <div class="solicitacao-card-footer">
                <button class="btn-action btn-reject">
                    <i class="fas fa-times-circle"></i> Rejeitar
                </button>
                <button class="btn-action btn-approve">
                    <i class="fas fa-check-circle"></i> Aprovar
                </button>
            </div>
        </div>
    `;

    // Adiciona os "event listeners" (as ações) aos botões
    col.querySelector('.btn-approve').addEventListener('click', () => {
        handleAprovar(solicitacao.id_cooperativa, token, col);
    });

    col.querySelector('.btn-reject').addEventListener('click', () => {
        handleRejeitar(solicitacao.id_cooperativa, solicitacao.email, token, col);
    });

    return col;
}

/**
 * Lida com a APROVAÇÃO de uma cooperativa
 */
function handleAprovar(id, token, cardElement) {
    Swal.fire({
        title: 'Aprovar Cadastro?',
        text: "A cooperativa terá o acesso liberado e o usuário será ativado.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sim, aprovar!',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: 'var(--verde-principal)',
        cancelButtonColor: 'var(--vermelho)'
    }).then(async (result) => {
        if (result.isConfirmed) {
            Swal.fire({ title: 'Aprovando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });

            try {
                // Chama a rota da API que JÁ EXISTE no teu ficheiro
                const response = await fetch('/api/cooperativas/alterar-aprovacao', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ 
                        id_cooperativa: id,
                        aprovacao: true // Define a aprovação como TRUE
                    })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Erro desconhecido');

                Swal.fire('Aprovado!', data.texto || 'Cooperativa aprovada com sucesso!', 'success');
                cardElement.remove(); // Remove o card da tela

            } catch (error) {
                Swal.fire('Erro', error.message, 'error');
            }
        }
    });
}

/**
 * Lida com a REJEIÇÃO de uma cooperativa
 */
async function handleRejeitar(id, email, token, cardElement) {
    
    const formHtml = `
        <select id="swal-motivo" class="form-select mb-3">
            <option value="" selected disabled>Selecione um motivo...</option>
            <option value="Documento Inválido">Documento Inválido</option>
            <option value="Dados Inconsistentes">Dados Inconsistentes (CNPJ e Nome não batem)</option>
            <option value="Fora do Escopo">Fora do Escopo (Não é uma cooperativa de reciclagem)</option>
            <option value="Outro">Outro (especifique abaixo)</option>
        </select>
        <textarea id="swal-justificativa" class="form-control" rows="3" placeholder="Escreva aqui a justificativa para a cooperativa. (Obrigatório)"></textarea>
    `;

    const { value: formValues, isConfirmed } = await Swal.fire({
        title: 'Rejeitar Cadastro',
        html: formHtml,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, rejeitar e enviar e-mail',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: 'var(--vermelho)',
        focusConfirm: false,
        preConfirm: () => {
            const motivo = document.getElementById('swal-motivo').value;
            const justificativa = document.getElementById('swal-justificativa').value;
            if (!motivo || !justificativa) {
                Swal.showValidationMessage('Por favor, selecione um motivo e preencha a justificativa.');
                return false;
            }
            return { motivo: motivo, justificativa: justificativa };
        }
    });

    if (isConfirmed && formValues) {
        Swal.fire({ title: 'Rejeitando...', allowOutsideClick: false, didOpen: () => Swal.showLoading() });
        
        try {
            // Chama a rota da API que JÁ EXISTE no teu ficheiro
            const response = await fetch('/api/cooperativas/rejeitar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    id_cooperativa: id,
                    email: email,
                    motivo: formValues.motivo,
                    justificativa: formValues.justificativa
                })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Erro desconhecido');

            Swal.fire('Rejeitado!', data.message, 'success');
            cardElement.remove(); // Remove o card da tela

        } catch (error) {
            Swal.fire('Erro', error.message, 'error');
        }
    }
}