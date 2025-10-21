import { getMateriais } from "./api/getMateriais.js";
import { getCompradoresPorMaterial } from "./api/getCompradores.js";


const buscarCompradoresSec = document.querySelector('.buscar-compradores__cartoes');

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
                <button class="verMais" data-index="${index}">Ver mais</button>
            </div>
        </div>
    `).join('');

    // 3. Insere todo o HTML no DOM de uma só vez (muito mais performático)
    buscarCompradoresSec.innerHTML = htmlCompradores;

    // 4. Agora que todos os botões existem, busca todos eles
    const todosOsBotoes = buscarCompradoresSec.querySelectorAll('.verMais');

    // 5. Adiciona o evento de clique para cada botão
    todosOsBotoes.forEach(botao => {
        botao.addEventListener('click', (event) => {
            // Pega o 'index' que guardamos no atributo 'data-index' do botão
            const compradorIndex = event.target.dataset.index;
            
            // Usa o index para pegar o objeto correto do array original
            const compradorSelecionado = compradores[compradorIndex];

            // Agora sim, mostra o SweetAlert com os dados corretos
            Swal.fire({
                title: `${compradorSelecionado.razao_social}`,
                html: `
                    <p><strong>Avaliação:</strong> ${compradorSelecionado.avaliacao} ⭐</p>
                    <p><strong>Valor Total Pago:</strong> R$${compradorSelecionado.valor_total}</p>
                    <p><strong>Total Comprado:</strong> ${compradorSelecionado.total_kg_comprado} Kgs</p>
                    `,
                icon: 'info'
            });
        });
    });
}

// Inicia o processo
renderizarMateriais();