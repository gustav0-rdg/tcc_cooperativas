const material = [
    { nome: 'Papel' },
    { nome: 'Metal' }
];

const vendedores = [
    {
        nome: 'Samuel',
        cpf: '479.151.534-94',
        ultima_venda: '23/05/2021',
        nota: 5
    },
    {
        nome: 'Ivo',
        cpf: '489.142.564-21',
        ultima_venda: '04/12/2023'
    }
];

const comentarios = [
    "Venda rápida e sem complicações.",
    "Cliente atendeu prontamente, tudo certo.",
    "Boa negociação, material limpo.",
    "Venda tranquila, pagou corretamente.",
    "Tudo certo, como combinado.",
    "Cliente educado e pontual.",
    "Material conforme esperado, sem surpresas.",
    "Recolheu tudo no horário.",
    "Transação simples, sem problemas.",
    "Ótima experiência de venda."
]

let etapaAtual = "materiais";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');

const vendaAtual = {
    vendedor: {},
    material: {},
    avaliacao: {},
    quantidade: 0
};

// Função para mostrar a etapa de vendedores
function exibirVendedores() {
    opcoesSection.innerHTML = ''; // Limpar as opções anteriores
    vendedores.forEach(vendedor => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${vendedor.nome}`);
        div.innerHTML = `
            <h1>${vendedor.nome}</h1>
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

// Função para mostrar a etapa de materiais
function exibirMateriais() {
    opcoesSection.innerHTML = ''; // Limpar as opções anteriores
    material.forEach(item => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${item.nome}`);
        div.innerHTML = `
            <h1>${item.nome}</h1>
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
function exibirValoresDeVenda() {
    opcoesSection.innerHTML = `
        <div>
            <h1>${vendaAtual.material.nome}</h1>
            <small>${vendaAtual.vendedor.nome}</small>
        </div>
        <div>
            <h3>Quantos Kgs?</h3>
            <input type="number" class="preco__kg" />
        </div>
        <div>
            <h3>Preço por kg</h3>
            <input type="number" class="peso__total" />
        </div>
        <button class="confirmar__venda">Confirmar Venda</button>
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

function exibirAvaliacao(){
    opcoesSection.innerHTML = '';
    opcoesSection.innerHTML = `
    <div class="resumo">
        <h1>Resumo da venda</h1>
        <div>
            <p>${vendaAtual.material.nome}</p>
            <small>${vendaAtual.quantidade}Kg</small>
        </div>
        <div>
            <p>${vendaAtual.total}</p>
            <small>${vendaAtual.preco_por_kg}</small>
        </div>
        <p> ${vendaAtual.vendedor.nome} </p>
        <small>${vendaAtual.vendedor.cpf}</small>
    </div>
    <div class="avaliacao">
        <h3>Como você avalia esse comprador?</h3>
        <input type="number" max=5 class="avaliacao__nota"/>
    </div>
    <div class="comentario">
        <h3>Comentario rápido</h3>
        ${comentarios.map(comentario => `
            <button class="comentario__btn" data-value="${comentario}">${comentario}</button>
            `).join('')}
    </div>
    <div class="opcional">
        <h3>Quer contar mais alguma coisa?</h3>
        <textarea rows="4" class="opcional__comentario"></textarea>
    </div>
    <div class="finalizar">
        <button class="finalizar__btn">Finalizar registro</button>
        <button>Pular avaliação</button>
    </div>
    `;
    let comentarioOpcional;
    const opcional = opcoesSection.querySelector('.opcional');
    const valorOpcional = opcional.querySelector('.opcional__comentario');
    valorOpcional.addEventListener('input', (e)=>{
        comentarioOpcional = e.target.value;
    })

    const avaliacaoNota = opcoesSection.querySelector('.avaliacao');
    const nota = avaliacaoNota.querySelector('.avaliacao__nota');
    let notaAtual;

    nota.addEventListener('input', (e)=>{
        notaAtual = e.target.value;
        console.log(notaAtual)
    })

    const comentariosRapido = opcoesSection.querySelector('.comentario');
    const botoes = comentariosRapido.querySelectorAll('.comentario__btn');

    let valorComentario;
    // Adiciona evento de clique para cada botão
    botoes.forEach(btn => { 
        btn.addEventListener('click', (e) => {
            // Pega o valor do comentário pelo dataset do botão clicado
            valorComentario = e.target.dataset.value;
            console.log('Comentário clicado:', valorComentario);

            // Aqui você pode salvar o comentário no objeto da venda, por exemplo:
        });
    })

    const finalizar = opcoesSection.querySelector('.finalizar');
    const finalizarBtn = finalizar.querySelector('.finalizar__btn');
    finalizarBtn.addEventListener('click', ()=>{
        vendaAtual.avaliacao.nota = notaAtual;
        vendaAtual.avaliacao.comentario = valorComentario;
        vendaAtual.avaliacao.analise = comentarioOpcional;
    })
}


// Inicializa a etapa
function inicializar() {
    if (etapaAtual === "materiais") {
        exibirMateriais(); // Exibe os materiais na primeira etapa
    }
}

inicializar(); // Chama a função inicial para carregar os materiais
