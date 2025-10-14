import { exibirAvaliacao } from "./exibirAvaliacao.js";
import { vendaAtual } from "../registrar_venda.js";
const etapaSection = document.querySelector('.registros__etapa');
const compradorSection = document.querySelector('.registros__comprador');
const opcoesSection = document.querySelector('.registros__opcoes');

export function exibirValoresDeVenda() {
    etapaSection.innerHTML = '';
    etapaSection.innerHTML = `
    <div class="etapa__progresso">
        <h1>${vendaAtual.vendedor.nome_fantasia}</h1>
        <small>Quanto vendeu e por quanto?</small>
        <div class="progress-container">
            <div class="progress-bar tres"></div>
        </div>
        <span class="progress-label">Passo 3 de 4</span>
    </div>
    `
    compradorSection.innerHTML = '';

    opcoesSection.innerHTML = `
        <div class="informacoes__vendedor">
            <h1>${vendaAtual.material.nome_comum}</h1>
            <small>Para: ${vendaAtual.vendedor.nome_fantasia}</small>
        </div>
        
        <div class="container__valores"> 
            <div class="valores__kg">
                <h3>Quantos Kgs?</h3>
                <input type="number" class="preco__kg" />
            </div>
            <div class="valores__preco">
                <h3>Preço por kg</h3>
                <input type="number" class="peso__total" />
            </div>
        </div>
        
        <button class="confirmar__venda">Continuar para a avaliação</button>
    `;
    // Adiciona o listener após os elementos estarem no DOM
    const botaoConfirmar = document.querySelector('.confirmar__venda');

    botaoConfirmar.addEventListener('click', () => {
        const quantidadeInput = document.querySelector('.preco__kg');
        const precoPorKgInput = document.querySelector('.peso__total');

        const quantidade = parseFloat(quantidadeInput.value);
        const precoPorKg = parseFloat(precoPorKgInput.value);

        // Adiciona os valores ao objeto vendaAtual
        vendaAtual.quantidade = quantidade;
        vendaAtual.preco_por_kg = precoPorKg;
        vendaAtual.total = quantidade * precoPorKg;

        console.log('Venda registrada:', vendaAtual);
        exibirAvaliacao()
        // Aqui você pode seguir para outra etapa ou resetar, conforme seu fluxo
    });
}