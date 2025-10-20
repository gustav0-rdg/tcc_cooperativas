import { vendaAtual } from "../registrar_venda.js";

const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const comentarios = [
    // Bom
    { comentario: "Tudo certo, cliente pagou na hora e retirou rápido.", tipo: "Bom" },
    { comentario: "Venda rápida, pagamento via Pix e entrega tranquila.", tipo: "Bom" },
    { comentario: "Cliente de confiança, tudo conforme combinado.", tipo: "Bom" },
    { comentario: "Pagou adiantado e buscou no mesmo dia.", tipo: "Bom" },
    { comentario: "Negociação fácil, entrega no prazo e sem complicações.", tipo: "Bom" },
    { comentario: "Transação limpa, sem atrasos nem dúvidas.", tipo: "Bom" },
    { comentario: "Cliente eficiente, tudo ocorreu bem.", tipo: "Bom" },
    { comentario: "Ótima experiência, logística e pagamento em dia.", tipo: "Bom" },
    { comentario: "Retirada feita pontualmente, pagamento certinho.", tipo: "Bom" },
    { comentario: "Cliente educado e objetivo, ótimo negócio.", tipo: "Bom" },

    // Neutro
    { comentario: "Entrega saiu com atraso leve, mas sem grandes problemas.", tipo: "Neutro" },
    { comentario: "Cliente demorou para responder, mas finalizou a compra.", tipo: "Neutro" },
    { comentario: "Alguns ajustes durante a venda, mas tudo certo no final.", tipo: "Neutro" },
    { comentario: "Pagamento feito no último dia, dentro do prazo.", tipo: "Neutro" },
    { comentario: "Venda foi ok, sem destaques positivos ou negativos.", tipo: "Neutro" },
    { comentario: "Cliente novo, ainda conhecendo o processo.", tipo: "Neutro" },
    { comentario: "Logística um pouco confusa, mas resolvida.", tipo: "Neutro" },
    { comentario: "Faltou um pouco de comunicação, mas foi concluído.", tipo: "Neutro" },
    { comentario: "Tudo certo, mas houve dúvidas no início.", tipo: "Neutro" },
    { comentario: "Negociação comum, sem intercorrências.", tipo: "Neutro" },

    // Ruim
    { comentario: "Cliente atrasou o pagamento por vários dias.", tipo: "Ruim" },
    { comentario: "Entrega teve que ser refeita por erro do cliente.", tipo: "Ruim" },
    { comentario: "Muita demora na negociação e respostas vagas.", tipo: "Ruim" },
    { comentario: "Pagou só depois de muita insistência.", tipo: "Ruim" },
    { comentario: "Combina uma coisa, depois muda tudo.", tipo: "Ruim" },
    { comentario: "Cliente difícil de lidar, gerou retrabalho.", tipo: "Ruim" },
    { comentario: "Não cumpriu prazo e não avisou.", tipo: "Ruim" },
    { comentario: "Venda estressante e mal resolvida.", tipo: "Ruim" },
    { comentario: "Sumiu após entrega, demorou a pagar.", tipo: "Ruim" },
    { comentario: "Nunca mais vendo para esse cliente.", tipo: "Ruim" }
];

export function exibirAvaliacao() {
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
        <p> ${vendaAtual.vendedor.razao_social} </p>
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
            notaAtual = avaliacaoSelecionada;
            mudarTipo(notaAtual);
            preencherEstrelas(avaliacaoSelecionada);
        });
    });

    function preencherEstrelas(qtd) {
        estrelas.forEach((estrela, i) => {
            if (i < qtd) {
                estrela.classList.remove('fa-regular');
                estrela.classList.add('fa-solid');
                estrela.style.color = "yellow"
            } else {
                estrela.classList.remove('fa-solid');
                estrela.classList.add('fa-regular');
                estrela.style.color = "black"
            }
        });
    }


    let comentarioOpcional;
    const opcional = opcoesSection.querySelector('.opcional');
    const valorOpcional = opcional.querySelector('.opcional__comentario');
    valorOpcional.addEventListener('input', (e) => {
        comentarioOpcional = e.target.value;
    })


    
    
    const finalizar = opcoesSection.querySelector('.finalizar');
    const finalizarBtn = finalizar.querySelector('.finalizar__btn');
    finalizarBtn.addEventListener('click', () => {
        vendaAtual.avaliacao.nota = notaAtual;
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
            color: "var(--verde-escuro-principal)",
            background: "var(--branco)",
            showConfirmButton: false,
            showCancelButton: false,
        })
    })
}

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

function mudarTipo(nota){
    let tipo; 

    switch (true){
        case nota <= 2:
           tipo = "Ruim" 
            break
        case nota == 3:
            tipo = "Neutro"
            break
        case nota > 3:
            tipo = "Bom"
            break
        };
    renderizarComentarios(tipo);
}

function renderizarComentarios(tipo){
    const comentariosHtml = opcoesSection.querySelector('.comentario');
    comentariosHtml.innerHTML = '';
    comentariosHtml.innerHTML = comentarios.filter(c => c.tipo === tipo).map
    (c => `<button class="comentario__btn" data-value="${c.comentario}">${c.comentario}</button>
            `).join('');

    const comentariosRapido = opcoesSection.querySelector('.comentario');
    const botoes = comentariosRapido.querySelectorAll('.comentario__btn');
    
    let valorComentario;
    // Adiciona evento de clique para cada botão
    botoes.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Pega o valor do comentário pelo dataset do botão clicado
            valorComentario = e.target.dataset.value;
            // adiciona no clicado
            btn.classList.toggle('ativo');
            const index = vendaAtual.avaliacao.comentarios_rapidos.indexOf(valorComentario);

            if (index > -1) {
                // Se já existe, remove
                vendaAtual.avaliacao.comentarios_rapidos.splice(index, 1);
            } else {
                // Se não existe, adiciona
                vendaAtual.avaliacao.comentarios_rapidos.push(valorComentario);
            }       
            console.log(vendaAtual.avaliacao.comentarios_rapidos);
            
            // Aqui você pode salvar o comentário no objeto da venda, por exemplo:
        });
    })
}