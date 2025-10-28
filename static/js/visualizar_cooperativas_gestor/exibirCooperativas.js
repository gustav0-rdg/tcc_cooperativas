const listCooperativasContainer = document.getElementById('cooperativasContainer');
const mostrandoCooperativasLabel = document.getElementById('mostrandoCooperativas');
const totalCooperativasLabel = document.getElementById('totalCooperativas');

const session_token = localStorage.getItem('session_token');

function formatarCNPJ (cnpj) 
{  
    const cnpjLimpo = cnpj.replace(/\D/g, '');
    if (!cnpj || cnpjLimpo.length !== 14) 
    {
        throw new Error ('CNPJ inválido');
    }

    return cnpjLimpo.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    '$1.$2.$3/$4-$5'
    );
}

async function consultarCooperativas ()
{
    const response = await fetch (
        
        '/api/cooperativas/get-all', 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );

    const data_request = await response?.json();

    if (!response.ok)
    {
        throw new Error (

            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'

        );
    }

    return data_request.dados_cooperativas;

}

function renderizarCooperativas (cooperativas)
{
    if (!Array.isArray(cooperativas))
    {
        throw new Error ('Valor inválido de cooperativas');
    }

    console.log(cooperativas)

    const listCooperativasRenderizadas = cooperativas.map((cooperativa) => {

        return `
            <div class="col-12 col-md-6 col-xl-4">

                <!-- Card individual da cooperativa -->
                <div class="coop-card"
                    data-id="${cooperativa.id_cooperativa}"
                    data-nome="${cooperativa.razao_social}"
                    data-cnpj="${formatarCNPJ(cooperativa.cnpj)}"
                    data-status="${cooperativa.status}"
                    data-data-cadastro="${cooperativa.id_cooperativa}"
                    data-ultimo-acesso="${cooperativa.id_cooperativa}"
                    data-ativo="${cooperativa.aprovado ? 'Ativo' : 'Inativo'}}"
                    data-telefone="${cooperativa.telefone}"
                    data-email="${cooperativa.email}"
                    data-endereco="${cooperativa.endereco}"
                    data-cidade="${cooperativa.cidade}"
                    data-estado="${cooperativa.estado}"
                    data-total-vendas="${cooperativa.totalVendas}"
                    data-materiais-vendidos="${cooperativa.materiaisVendidos}"
                >
                    
                    <!-- Cabeçalho do card -->
                    <div class="coop-card-header">
                        <div>
                            <h3 class="coop-name">${cooperativa.razao_social}</h3>
                            <p class="coop-cnpj">${formatarCNPJ(cooperativa.cnpj)}</p>
                        </div>
                        <span class="status-badge status-${cooperativa.status}">
                            ${cooperativa.status}
                        </span>
                    </div>
                    
                    <!-- Corpo do card com informações básicas -->
                    <div class="coop-card-body">
                        <div class="coop-info-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${cooperativa.cidade} - ${cooperativa.estado}</span>
                        </div>
                        <div class="coop-info-item">
                            <i class="fas fa-phone"></i>
                            <span>${cooperativa.telefone}</span>
                        </div>
                        <div class="coop-info-item">
                            <i class="fas fa-envelope"></i>
                            <span>${cooperativa.email}</span>
                        </div>
                    </div>
                    
                    <!-- Rodapé com status de atividade e botão de ação -->
                    <div class="coop-card-footer">
                        <div class="last-access">
                            <i class="fas fa-clock"></i>
                            <span>Último acesso: ${Date.now() - cooperativa.ultima_atualizacao}</span>
                            
                            <!-- Indicador visual de atividade (ativo/inativo) -->
                            <span class="activity-indicator ${cooperativa.aprovado ? 'activity-active' : 'activity-inactive'}" 
                                    title="${cooperativa.aprovado ? 'Ativo' : 'Inativo'}"></span>
                        </div>
                        
                        <!-- Botão de bloqueio ou desbloqueio, conforme status -->
                        ${
                            cooperativa.status == 'bloqueado'
                            ?
                            `
                            <button class="btn-block btn-block-success" 
                                    data-user-id="${cooperativa.id_usuario}" 
                                    data-coop-nome="${cooperativa.razao_social}"
                                    data-acao="desbloquear">
                                <i class="fas fa-unlock"></i> Desbloquear
                            </button>
                            `
                            :
                            `
                            <button class="btn-block btn-block-danger" 
                                    data-user-id="${cooperativa.id_usuario}" 
                                    data-coop-nome="${cooperativa.razao_social}"
                                    data-acao="bloquear">
                                <i class="fas fa-ban"></i> Bloquear
                            </button>
                            `
                        }
                    </div>
                </div>
            </div>
        `

    });

    return listCooperativasRenderizadas;

}


document.addEventListener('DOMContentLoaded', async function () {

    const data_cooperativas = await consultarCooperativas();

    if (data_cooperativas.length <= 0)
    {
        listCooperativasContainer.innerHTML = `

            <div class="col-12">
                <div class="alert alert-info text-center" style="background: var(--branco); border: 2px solid var(--verde-claro-medio); border-radius: 12px;">
                    <i class="fas fa-info-circle" style="font-size: 2rem; color: var(--verde-principal); margin-bottom: 1rem;"></i>
                    <h5 style="color: var(--verde-escuro);">Nenhuma cooperativa encontrada</h5>
                    <p style="color: var(--cinza-claro); margin-bottom: 0;">Tente ajustar os filtros de pesquisa</p>
                </div>
            </div>
        `;
    }

    else
    {
        totalCooperativasLabel.textContent = data_cooperativas.length;
        listCooperativasContainer.innerHTML = renderizarCooperativas(data_cooperativas).join(' ');
    }

}); 