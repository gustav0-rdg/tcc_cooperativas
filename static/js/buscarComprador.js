import { getMateriais } from "./api/getMateriais.js";
import { getCompradoresPorMaterial, getCompradoresavaliacoes } from "./api/getCompradores.js";


const buscarCompradoresSec = document.querySelector('.buscar-compradores__cartoes');
const detalheCompradores = document.querySelector('#detalhe-comprador');
async function renderizarMateriais() {
    const materiais = await getMateriais();
    if (!materiais) return; // Se não houver materiais, não faz nada
    buscarCompradoresSec.innerHTML = ''; 

    materiais.forEach(material => {

        buscarCompradoresSec.innerHTML += `
            <div class="col-12 col-md-6 col-lg-4 w-100 d-flex buscar-comprador__conteiner flex-column">
                <a href="#" class="cartao-material cartao-material--${material.nome_padrao}" data-material="${material.id_material_catalogo}">
                    <span class="cartao-material__rotulo">${material.nome_padrao}</span>
                </a>
                <button class="btn btn-lg buscar-compradores__ver-mais d-flex justify-content-center mt-2 rounded-5 w-70 align-self-center" data-material="${material.id_material_catalogo}">Ver mais</button>
            </div>
        `;
    });
}

buscarCompradoresSec.addEventListener('click', async (event) => {
    event.preventDefault();
    const targetElement = event.target.closest('[data-material]');

    if (targetElement) {
        const materialNome = targetElement.dataset.material;
        console.log(`Buscando compradores para: ${materialNome}`);
        const compradores = await getCompradoresPorMaterial(materialNome);
        await renderizarCompradores(compradores)
    }
});

async function renderizarCompradores(compradores) {
    buscarCompradoresSec.innerHTML = '';
    const htmlCompradores = compradores.map((comprador, index) => `
        <div class="comprador-card">
            <div class="comprador-header">
                <div class="comprador-avatar">
                    <span class="material-icons">${comprador.avatar}</span>
                </div>
                <div class="comprador-info">
                    <h3>${comprador.razao_social}</h3>
                    <span>Avaliação: ${comprador.avaliacao} ⭐</span>
                </div>
                <div class="comprador-preco">
                    <p>Preço pago: R$${comprador.valor_total}</p>
                    <small>${comprador.total_kg_comprado} Kgs</small>
                </div>
                <button class="verMais" data-value="${comprador.cnpj}" data-index="${index}">Ver mais</button>
            </div>
        </div>
    `).join('');

    detalheCompradores.innerHTML = htmlCompradores;
    detalheCompradores.classList.remove('hidden')

    const todosOsBotoes = detalheCompradores.querySelectorAll('.verMais');

    todosOsBotoes.forEach(botao => {
        botao.addEventListener('click', async (event) => {
            const compradorIndex = event.target.dataset.index;
            const compradorCnpj = event.target.dataset.value;
            const avaliacoes = await getCompradoresavaliacoes(compradorCnpj);
            console.log(avaliacoes);
            const compradorSelecionado = compradores[compradorIndex];
            Swal.fire({
                title: `${compradorSelecionado.razao_social}`,
                background: "var(--verde-principal)",
                html: `
                    <p><strong>Avaliação:</strong> ${compradorSelecionado.avaliacao} ⭐</p>
                    <p><strong>Valor Total Pago:</strong> R$${compradorSelecionado.valor_total}</p>
                    <p><strong>Total Comprado:</strong> ${compradorSelecionado.total_kg_comprado} Kgs</p>
                    <div class="container">
                    ${
                        avaliacoes.map(a => `<div class="item">${a.texto} <span class="badge">${a.quantidade}</span></div>`
                        ).join('')
                    }
                    </div>
                    `,
                icon: 'info'
            });
        });
    });
}

// Inicia o processo
renderizarMateriais();