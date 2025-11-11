import { getMateriais } from "../api/getMateriais.js";

document.getElementById('form-xml').addEventListener('submit', async (e) => {
    e.preventDefault(); // Evita reload da página

    const formData = new FormData(e.target);

    try {
        const response = await fetch('/post/dados-xml', {
            method: 'POST',
            body: formData
        });
        const materiais = await getMateriais();
        console.log(materiais);
        const data = await response.json(); // <- Aqui lê o jsonify do Flask

        if (response.ok) {
            console.log(' Sucesso:', data);
            alert('Venda registrada com sucesso!');
        } else {
            console.error('Erro:', data);
            if (data.material_invalido) {
                abrirModalCadastroMaterial(data.nome_material_invalido);
            } else {
                alert(`Erro: ${data.erro || 'Falha desconhecida'}`);
            }
        }

    } catch (err) {
        console.error('Erro inesperado:', err);
        alert('Erro de conexão com o servidor.');
    }
});


// Seus estilos CSS para o conteúdo
const swalStyles = `
  .swal-content-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    text-align: left;
  }

  .swal-input-label {
    font-size: 1em;
    font-weight: 600;
    color: var(--verde-escuro);
    margin-bottom: -5px;
  }

  /* ==== INPUTS MELHORADOS ==== */
  .swal-input-field {
    width: 100% !important;
    margin: 0;
    border: 2px solid var(--verde-claro-medio);
    border-radius: 10px !important;
    background-color: var(--verde-claro);
    color: var(--verde-escuro);
    font-size: 0.95rem;
    padding: 10px 12px;
    transition: all 0.2s ease;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
  }

  .swal-input-field::placeholder {
    color: #4a4a4a99;
    font-style: italic;
  }

  .swal-input-field:hover {
    border-color: var(--verde-principal);
    background-color: var(--branco);
  }

  .swal-input-field:focus {
    border-color: var(--verde-escuro-medio);
    background-color: var(--branco);
    outline: none;
    box-shadow: 0 0 5px rgba(58, 124, 24, 0.4);
  }

  /* ==== LISTA DE CATEGORIAS ==== */
  .swal-material-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 180px;
    overflow-y: auto;
    border: 1px solid var(--verde-escuro-medio);
    padding: 12px;
    border-radius: 8px;
    background: var(--verde-principal);
  }

  .swal-radio-option {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 8px;
    border-radius: 6px;
    color: var(--verde-escuro);
    transition: background-color 0.2s;
  }

  .swal-radio-option input[type="radio"] {
    margin: 0;
    flex-shrink: 0;
  }

  .swal-radio-option label {
    font-weight: 500;
    cursor: pointer;
  }

  .swal-radio-option:hover {
     background-color: var(--verde-claro);
  }
`;

function injectSwalButtonStyles() {
    const styleId = 'swal-custom-button-style';
    if (document.getElementById(styleId)) {
        return;
    }
    const style = document.createElement('style');
    style.id = styleId;
    style.innerHTML = `
      .swal2-confirm.swal-confirm-custom-style {
        background-color: var(--verde-escuro-medio) !important; 
        color: var(--verde-claro) !important;           
      }
    `;
    document.head.appendChild(style);
}

function injectSwalContentStyles() {
    const styleId = 'swal-custom-content-style';
    if (document.getElementById(styleId)) {
        return;
    }
    const style = document.createElement('style');
    style.id = styleId;
    style.innerHTML = swalStyles; // Usa a variável de estilos que você definiu
    document.head.appendChild(style);
}

/**
 * Gera o HTML da lista de categorias como botões de rádio.
 * @param {Array} categorias - O array de objetos vindo da API.
 * @returns {string} - O HTML dos botões de rádio.
 */
function gerarHtmlCategorias(categorias) {
    return categorias.map(cat => `
        <div class="swal-radio-option" onclick="this.querySelector('input').click()">
            <input type="radio" 
                   name="material_catalogo" 
                   id="cat-${cat.id_material_catalogo}" 
                   value="${cat.id_material_catalogo}">
                   
            <label for="cat-${cat.id_material_catalogo}">
                <strong>${cat.nome_padrao}:</strong> ${cat.descricao}
            </label>
        </div>
    `).join('');
}

/**
 * Gera o HTML estático principal para o modal.
 * @returns {string} - O HTML do formulário.
 */
function gerarSwalHtml() {
    return `
      <div class="swal-content-container">
        
        <label class="swal-input-label">1. Selecione a Categoria Principal:</label>
        <div class="swal-material-list" id="material-list-container">
          <p>Carregando categorias...</p>
        </div>
        
        <label class="swal-input-label" for="swal-nome-padrao">2. Nome Base do Novo Material:</label>
        <input id="swal-nome-padrao" 
               class="swal-input-field" 
               placeholder="Ex: Garrafa PET 2L, Papelão Ondulado"
               readonly>
        
        <label class="swal-input-label" for="swal-sinonimo">3. Sinônimo (Opcional):</label>
        <input id="swal-sinonimo" 
               class="swal-input-field" 
               placeholder="Ex: PET transparente, Caixa de Papelão">
      </div>
    `;
}

function abrirModalCadastroMaterial(nome_invalido) {
    // Garante que os estilos estão na página
    injectSwalButtonStyles();
    injectSwalContentStyles();

    Swal.fire({
        title: 'Cadastrar Novo Tipo de Material',
        html: gerarSwalHtml(),
        
        // Aplica a classe customizada ao botão
        customClass: {
            confirmButton: 'swal-confirm-custom-style',
        },
        
        showCancelButton: true,
        confirmButtonText: 'Cadastrar Material',
        cancelButtonText: 'Cancelar',
        
        didOpen: async () => {
            const container = document.getElementById('material-list-container');
            if (container) {
                const materiais = await getMateriais()
                // Use os dados reais da sua API aqui
                container.innerHTML = gerarHtmlCategorias(materiais); 
            }

            const input = document.querySelector('#swal-nome-padrao');
            input.textContent = nome_invalido;
            input.value = nome_invalido;
        },

        preConfirm: () => {
            // Coleta os valores do formulário
            const radioSelecionado = document.querySelector('input[name="material_catalogo"]:checked');
            const idCategoria = radioSelecionado ? radioSelecionado.value : null;
            const nomePadrao = document.getElementById('swal-nome-padrao').value;
            const sinonimo = document.getElementById('swal-sinonimo').value;

            // Validação
            if (!idCategoria) {
                Swal.showValidationMessage('Você precisa selecionar uma categoria principal.');
                return false; // Impede o fechamento
            }
            if (!nomePadrao || nomePadrao.trim() === '') {
                Swal.showValidationMessage('O "Nome Padrão" é obrigatório.');
                return false; // Impede o fechamento
            }
            
            return {
                id_material_catalogo: parseInt(idCategoria), // Converte para número
                nome_padrao: nomePadrao,
                sinonimo: sinonimo
            };
        }
        
    }).then((result) => {
        // O `result.value` contém o objeto retornado pelo preConfirm
        if (result.isConfirmed) {
            console.log('Dados prontos para enviar para a API:', result.value);
            
            // Simula uma chamada de API
            Swal.fire(
                'Sucesso!',
                'Novo material cadastrado.',
                'success'
            );
            
        }
    });
}











const session_token = localStorage.getItem('session_token');

async function cadastrarMateriais(id_material, nome_especifico, nome_sinonimo){
    const resp = await fetch(`
        /post/material/${id_material}
        `,
        {
            method: 'POST',
            headers: {
                'Content-type':'Application/json',
                'Authorization': session_token,
            } ,
            body: JSON.stringify(nome_especifico)

        }
    )
}