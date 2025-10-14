import { registrarNovoVendedor } from "../registrar_vendedores.js";
import obterVendedores from "../obterVendedor.js";
import { exibirValoresDeVenda } from "./exibirValoresDeVenda.js";
import { vendaAtual } from "../registrar_venda.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const compradorSection = document.querySelector('.registros__comprador');


const vendedores = [
    {
        nome_fantasia: 'Samuel',
        cnpj: '479.151.534-94',
        data_ultima_venda: '23/05/2021',
        nota: 5
    },
    {
        nome_fantasia: 'Ivo',
        cnpj: '489.142.564-21',
        data_ultima_venda: '04/12/2023'
    },
    {
        nome_fantasia: 'Alex',
        cnpj: '405.313.132-34', 
        data_ultima_venda: '07/11/2024'
    },
    {
        nome_fantasia: 'Matheus Fagulhos Nani',
        cnpj: '404.213.123-94',
        data_ultima_venda: '08/12/2024'
    }
];

// Função para mostrar a etapa de vendedores
export function exibirVendedores() {
    etapaSection.innerHTML = '';
    etapaSection.innerHTML = `
    <div class="etapa__progresso">
        <h1>Venda de ${vendaAtual.material.nome_comum}</h1>
        <small>Para quem você vendeu?</small>
        <div class="progress-container">
            <div class="progress-bar cinquenta"></div>
        </div>
        <span class="progress-label">Passo 2 de 4</span>
    </div>
    `
    
    opcoesSection.innerHTML = '';
    
    const novoComprador = document.createElement('button');
    novoComprador.className = "registros__opcoes-btn";
    novoComprador.classList.add("opcoes-btn__novo-comprador")
    novoComprador.textContent = "Registrar comprador";

    novoComprador.addEventListener('click', async ()=>{
        Swal.fire({
            title: 'Buscar novo comprador.',
            html: `
                <input type="text" id="buscarComprador" />
            `,
            showCancelButton: true,
            confirmButtonText: 'Buscar',
            cancelButtonText: 'Cancelar',
            background: "var(--verde-principal)",
            preConfirm: () => {
                const valor = document.getElementById('buscarComprador').value;
                if (!valor){
                    Swal.showValidationMessage('Digite algo para buscar!')
                }
                return valor
            }
        }).then(async (result) =>{
            if (result.isConfirmed){
                const dados = await obterVendedores(result.value);
                const novoVendedor = registrarNovoVendedor(dados)
            }
        })
    })
    compradorSection.appendChild(novoComprador);

    vendedores.forEach(vendedor => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${vendedor.nome_fantasia}`);
        div.innerHTML = `
            <h1>${vendedor.nome_fantasia}</h1>
            <small>CNPJ: ${vendedor.cnpj}</small>
        `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o vendedor
        div.addEventListener('click', () => {
            vendaAtual.vendedor = vendedor; // Atualiza o vendedor no objeto vendaAtual
            console.log(vendaAtual); // Apenas para visualização
            exibirValoresDeVenda()
        });
    });
}
