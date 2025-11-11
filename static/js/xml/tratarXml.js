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
            console.log('✅ Sucesso:', data);
            alert('Venda registrada com sucesso!');
        } else {
            console.error('Erro:', data);
            if (data.material_invalido) {
                abrirModalCadastroMaterial();
                alert(`Erro: ${data.material_invalido}`);
            } else {
                alert(`Erro: ${data.erro || 'Falha desconhecida'}`);
            }
        }

    } catch (err) {
        console.error('❌ Erro inesperado:', err);
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
    margin-bottom: -10px; 
  }
  .swal-input-field {
    width: 100% !important; 
    margin: 0;
    border-radius: 6px !important; 
    background-color: var(--verde-claro);
  }
  .swal-input-field:focus {
    border-color: var(--verde-escuro-medio);
    outline: none;
    box-shadow: 0 0 5px rgba(49, 97, 16, 0.5);
  }
  .swal-input-field::placeholder{
    color: var(--ver-escuro-medio)
  }
  .swal-material-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 180px; 
    overflow-y: auto;
    border: 1px solid var(--verde-escuro-medio);
    padding: 12px;
    border-radius: 6px; 
    background: var(--verde-principal); 
  }
  .swal-radio-option {
    display: flex;
    align-items: center;
    gap: 10px; 
    cursor: pointer;
    padding: 8px;
    border-radius: 4px; 
    color: var(--verde-escuro-medio);
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
  /* Bônus: Efeito de hover para os rádios */
  .swal-radio-option:hover {
     background-color: var(--verde-claro);
  }
`;

// Sua função para injetar o estilo do BOTÃO
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

// Nova função para injetar o estilo do CONTEÚDO
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
 * =================================================================
 * 3. FUNÇÃO PARA GERAR O HTML DO SWAL
 * =================================================================
 */

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
        
        <label class="swal-input-label" for="swal-nome-padrao">2. Nome Padrão do Novo Material:</label>
        <input id="swal-nome-padrao" 
               class="swal-input-field" 
               placeholder="Ex: Garrafa PET 2L, Papelão Ondulado">
        
        <label class="swal-input-label" for="swal-sinonimo">3. Sinônimo (Opcional):</label>
        <input id="swal-sinonimo" 
               class="swal-input-field" 
               placeholder="Ex: PET transparente, Caixa de Papelão">
      </div>
    `;
}

/**
 * =================================================================
 * 4. FUNÇÃO PRINCIPAL QUE DISPARA O SWAL
 * =================================================================
 */
function abrirModalCadastroMaterial() {
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
        
        /**
         * didOpen é chamado após o modal aparecer.
         * Usamos para injetar o conteúdo dinâmico (lista de rádios).
         */
        didOpen: async () => {
            const container = document.getElementById('material-list-container');
            if (container) {
                const materiais = await getMateriais()
                // Use os dados reais da sua API aqui
                container.innerHTML = gerarHtmlCategorias(materiais); 
            }
        },

        /**
         * preConfirm é chamado ANTES de fechar o modal ao clicar em "Confirmar".
         * É o local perfeito para validar e coletar dados.
         */
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
            
            // Retorna os dados coletados.
            // Isso será o `result.value` no .then()
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
            
            // Ex: fetch('/api/materiais', { method: 'POST', body: JSON.stringify(result.value) })
        }
    });
}