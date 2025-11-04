import { exibirAvaliacao } from "./module/exibirAvaliacao.js";
import { exibirSubtipos } from "./module/exibirSubtipos.js";
import { exibirVendedores } from "./module/exibirVendedores.js";
import { getMateriais } from "../api/getMateriais.js";
export const material = await getMateriais();

let etapaAtual = "materiais";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');

export const vendaAtual = {
    vendedor: {},
    material: {
        id_categoria:0,
        categoria:'',
        subtipo:''
    },
    avaliacao: {
        comentarios_rapidos: [],
    },
    quantidade: 0
};


// Função para mostrar a etapa de materiais
function exibirMateriais() {
    etapaSection.innerHTML = `
    <h1>Registrar Venda</h1>
    <small>O que você vendeu?</small>
    <div class="progress-container">
        <div class="progress-bar"></div>
    </div>
    <span class="progress-label">Passo 1 de 4</span>

    `

    opcoesSection.innerHTML = ''; // Limpar as opções anteriores
    material.forEach(item => {
        console.log(item)
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${item.nome_padrao}`);
        div.innerHTML = `
            <h1>${item.nome_padrao}</h1>
        `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o material
        div.addEventListener('click', () => {
            vendaAtual.material.categoria = item.nome_padrao;
            vendaAtual.material.id_categoria = item.id_material_catalogo // Atualiza o material no objeto vendaAtual
            etapaAtual = "subtipos"; // Muda para a etapa de vendedores
            // TROCAR ESTE PARA EXIBIR SUBTIPOS
            // exibirVendedores(); // Exibe os vendedores
            exibirSubtipos();
            console.log(vendaAtual); // Apenas para visualização
        });
    });
}

// Inicializa a etapa
function inicializar() {
    if (etapaAtual === "materiais") {
        exibirMateriais(); // Exibe os materiais na primeira etapa
    }
}

inicializar(); // Chama a função inicial para carregar os materiais

