import { exibirAvaliacao } from "./module/exibirAvaliacao.js";
import { exibirVendedores } from "./module/exibirVendedores.js";
const material = [
    { nome_comum: 'Papel', valor: '0,60' },
    { nome_comum: 'Metal', valor: '0,65' }
];

let etapaAtual = "materiais";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');

export const vendaAtual = {
    vendedor: {},
    material: {},
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
        div.setAttribute('data-value', `${item.nome_comum}`);
        div.innerHTML = `
            <h1>${item.nome_comum}</h1>
            <small>R$${item.valor}/Kg</small>
        `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o material
        div.addEventListener('click', () => {
            vendaAtual.material = item; // Atualiza o material no objeto vendaAtual
            etapaAtual = "vendedores"; // Muda para a etapa de vendedores
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

