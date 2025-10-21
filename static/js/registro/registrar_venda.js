import { exibirAvaliacao } from "./module/exibirAvaliacao.js";
import { exibirVendedores } from "./module/exibirVendedores.js";
import { getMateriais } from "../api/getMateriais.js";
const material = await getMateriais();

let etapaAtual = "materiais";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');

export const vendaAtual = {
    vendedor: {},
    material: {
        principal:'',
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
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${item.nome_padrao}`);
        div.innerHTML = `
            <h1>${item.nome_padrao}</h1>
            <small>${item.categoria}</small>
        `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o material
        div.addEventListener('click', () => {
            vendaAtual.material.principal = item.nome_padrao; // Atualiza o material no objeto vendaAtual
            etapaAtual = "subtipos"; // Muda para a etapa de vendedores
            exibirVendedores(); // Exibe os vendedores
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

