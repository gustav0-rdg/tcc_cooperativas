const material = [
    { nome_comum: 'Papel', valor: '0,60' },
    { nome_comum: 'Metal', valor: '0,65' }
];

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
function exibirValoresDeVenda() {
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

function exibirAvaliacao() {
    etapaSection.innerHTML = '';
    etapaSection.innerHTML = `
    <div class="etapa__progresso">
        <h1>Como foi a venda?</h1>
        <small>Sua opinião vale muito!</small>
        <div class="progress-container">
            <div class="progress-bar quatro"></div>
        </div>
        <span class="progress-label">Passo 4 de 4</span>
    </div>
    `

    opcoesSection.innerHTML = '';
    opcoesSection.innerHTML = `
    <div class="resumo">
        <h1>Resumo da venda</h1>
        <div class="resumo__venda">
            <div>
                <p>${vendaAtual.material.nome_comum}</p>
                <small>${vendaAtual.quantidade} Kg</small>
            </div>
            <div>
                <p>R$${vendaAtual.total}</p>
                <small>R$${vendaAtual.preco_por_kg}/Kg</small>
            </div>
        </div>
        <hr>
        <p> ${vendaAtual.vendedor.nome_fantasia} </p>
        <small>${vendaAtual.vendedor.cnpj}</small>
    </div>
    <div class="avaliacao">
        <h3>Como você avalia esse comprador?</h3>
        <div class="estrelas">
            <i class="fa-regular fa-star estrela" data-index="1"></i>
            <i class="fa-regular fa-star estrela" data-index="2"></i>
            <i class="fa-regular fa-star estrela" data-index="3"></i>
            <i class="fa-regular fa-star estrela" data-index="4"></i>
            <i class="fa-regular fa-star estrela" data-index="5"></i>
        </div>
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

    const estrelas = opcoesSection.querySelectorAll('.estrela');
    let avaliacaoSelecionada = 0;
    let notaAtual;

    estrelas.forEach((estrela, index) => {
        estrela.addEventListener('mouseover', () => {
            preencherEstrelas(index + 1);
        });

        estrela.addEventListener('mouseout', () => {
            preencherEstrelas(avaliacaoSelecionada);
        });

        estrela.addEventListener('click', () => {
            avaliacaoSelecionada = index + 1;
            console.log(avaliacaoSelecionada);
            notaAtual = avaliacaoSelecionada;
            preencherEstrelas(avaliacaoSelecionada);
        });
    });

    function preencherEstrelas(qtd) {
        estrelas.forEach((estrela, i) => {
            if (i < qtd) {
                estrela.classList.remove('fa-regular');
                estrela.classList.add('fa-solid');
            } else {
                estrela.classList.remove('fa-solid');
                estrela.classList.add('fa-regular');
            }
        });
    }


    let comentarioOpcional;
    const opcional = opcoesSection.querySelector('.opcional');
    const valorOpcional = opcional.querySelector('.opcional__comentario');
    valorOpcional.addEventListener('input', (e) => {
        comentarioOpcional = e.target.value;
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
    finalizarBtn.addEventListener('click', () => {
        vendaAtual.avaliacao.nota = notaAtual;
        vendaAtual.avaliacao.comentario = valorComentario;
        vendaAtual.avaliacao.analise = comentarioOpcional;

        enviarValores(vendaAtual);

        Swal.fire({
            icon: "success",
            title: "Venda registrada!",
            html: `
            <div class="relatorio_de_venda">
                <h3> R$${vendaAtual.total}</h3>
                <p>${vendaAtual.quantidade}Kg de ${vendaAtual.material.nome_comum} para ${vendaAtual.vendedor.nome_fantasia}</p>
            </div>
            <div class="finalizacao_sw">
                <p>Obrigado por registrar sua venda!<br>Isso ajuda toda a comunidade. </p>
                <a href="/registrar-venda">Registrar nova venda</a>
                <a href="/pagina-inicial">Voltar ao ínicio</a>
            </div>
                `,
            color: "var(--verde-claro-principal)",
            background: "var(--verde-medio-secundario)",
            showConfirmButton: false,
            showCancelButton: false,
        })
    })
}


// Inicializa a etapa
function inicializar() {
    if (etapaAtual === "materiais") {
        exibirMateriais(); // Exibe os materiais na primeira etapa
    }
}

inicializar(); // Chama a função inicial para carregar os materiais

const enviarValores = async (dados) =>{
    fetch('/post/dados-venda', {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
        },
        body: JSON.stringify(dados)
    }).then(response => response.json())
    .then(data =>{
        console.log('Sucesso:', data);
    }).catch((error) =>{
        console.error('erro:', error)
    })
}