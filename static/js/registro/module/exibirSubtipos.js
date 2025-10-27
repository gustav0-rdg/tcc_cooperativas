import { material } from "../registrar_venda.js";

import { vendaAtual } from "../registrar_venda.js";
import { exibirVendedores } from "./exibirVendedores.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const compradorSection = document.querySelector('.registros__comprador');


export async function exibirSubtipos() {

    etapaSection.innerHTML = `
        <div class="etapa__progresso">
            <h1>Venda de ${vendaAtual.material.principal}</h1>
            <small>Qual o subtipo do produto</small>
            <div class="progress-container">
                <div class="progress-bar"></div>
            </div>
            <span class="progress-label">Passo 1 de 4</span>
        </div>
        `;

    opcoesSection.innerHTML = '';

    // --- Lógica do botão de registrar novo subtipo ---
    const novoSubtipo = document.createElement('button');
    novoSubtipo.className = "registros__opcoes-btn";
    novoSubtipo.classList.add("opcoes-btn__novo-comprador");
    novoSubtipo.textContent = "Registrar comprador";

    novoSubtipo.addEventListener('click', async () =>{
        Swal.fire({
            title:'Algum destes materiais'
        })
    })


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
                vendaAtual.material.subtipo = item.nome_padrao; // Atualiza o material no objeto vendaAtual
        
                // TROCAR ESTE PARA EXIBIR SUBTIPOS
                // exibirVendedores(); // Exibe os vendedores
                exibirVendedores();
                console.log(vendaAtual); // Apenas para visualização
            });
        });

}