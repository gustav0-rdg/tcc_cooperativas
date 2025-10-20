import { registrarNovoVendedor } from "../registrar_vendedores.js";
import { validarCNPJ } from "./validarCnpj.js";
import buscarVendedores from "../obterVendedor.js";
import { getCompradores } from "../../api/getCompradores.js";

import { exibirValoresDeVenda } from "./exibirValoresDeVenda.js";
import { vendaAtual } from "../registrar_venda.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const compradorSection = document.querySelector('.registros__comprador');



// Função para mostrar a etapa de vendedores
export async function exibirVendedores() {
    // --- Essa parte inicial continua a mesma ---
    etapaSection.innerHTML = `
    <div class="etapa__progresso">
        <h1>Venda de ${vendaAtual.material.nome_comum}</h1>
        <small>Para quem você vendeu?</small>
        <div class="progress-container">
            <div class="progress-bar cinquenta"></div>
        </div>
        <span class="progress-label">Passo 2 de 4</span>
    </div>
    `;
    opcoesSection.innerHTML = '';
    
    // --- Lógica do botão de registrar novo comprador ---
    const novoComprador = document.createElement('button');
    novoComprador.className = "registros__opcoes-btn";
    novoComprador.classList.add("opcoes-btn__novo-comprador");
    novoComprador.textContent = "Registrar comprador";

    novoComprador.addEventListener('click', async () => {
        Swal.fire({
            title: 'Buscar novo comprador.',
            html: `<input type="text" id="buscarComprador" />`,
            showCancelButton: true,
            confirmButtonText: 'Buscar',
            cancelButtonText: 'Cancelar',
            background: "var(--verde-principal)",
            preConfirm: () => {
                const valor = document.getElementById('buscarComprador').value;
                if (!valor) {
                    Swal.showValidationMessage('Digite algo para buscar!');
                }
                return valor;
            }
        }).then(async (result) => {
            if (result.isConfirmed) {
                const isCnpj = validarCNPJ(result.value);
                if (!isCnpj) {
                    return Swal.fire({
                        title: "Insira um CNPJ Válido",
                        icon: "error"
                    });
                }

                // Registra o novo vendedor
                const dados = await buscarVendedores(result.value);
                const novoVendedor = await registrarNovoVendedor(dados);
                if (novoVendedor){
                    Swal.fire({
                        title: "Cadastro concluído.",
                        icon: "success"
                    });
                    await renderizarListaDeVendedores();

                }
                // =======================================================
            }
        });
    });
    compradorSection.appendChild(novoComprador);
    // Agora, para exibir a lista pela primeira vez, basta chamar sua nova função.
    await renderizarListaDeVendedores();
}

async function renderizarListaDeVendedores() {
    // 1. Limpa a seção de opções para não duplicar a lista
    opcoesSection.innerHTML = '';

    // 2. Busca a lista ATUALIZADA de compradores no seu backend
    const vendedores = await getCompradores();
    
    // 3. Cria e adiciona o botão de cada vendedor na tela
    vendedores.forEach(vendedor => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${vendedor.razao_social}`);
        div.innerHTML = `
            <h1>${vendedor.razao_social}</h1>
            <small>CNPJ: ${vendedor.cnpj}</small>
        `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o vendedor
        div.addEventListener('click', () => {
            vendaAtual.vendedor = vendedor;
            console.log(vendaAtual);
            exibirValoresDeVenda();
        });
    });
}