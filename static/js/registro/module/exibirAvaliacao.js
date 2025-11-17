import { vendaAtual } from "../registrar_venda.js";
import { getFeedbacks } from "../../api/getFeedbacks.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');

const comentarios = await getFeedbacks();

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
                <p>${vendaAtual.material.subtipo}</p>
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
        <button class="pular-avaliacao">Pular avaliação</button>
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
    const pularBtn = finalizar.querySelector('.pular-avaliacao');

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
                <p>${vendaAtual.quantidade}Kg de ${vendaAtual.material.subtipo} para ${vendaAtual.vendedor.razao_social}</p>
            </div>
            <div class="finalizacao_sw">
                <p>Obrigado por registrar sua venda!<br>Isso ajuda toda a comunidade. </p>
                <a href="/registrar-venda">Registrar nova venda</a>
                <a href="/pagina-inicial">Voltar ao ínicio</a>
            </div>
                `,
            color: "var(--verde-escuro)",
            background: "var(--branco)",
            showConfirmButton: false,
            showCancelButton: false,
        })
    })

    pularBtn.addEventListener('click', () => {
        // Remove a avaliação do objeto vendaAtual
        delete vendaAtual.avaliacao;

        enviarValores(vendaAtual);

        Swal.fire({
            icon: "success",
            title: "Venda registrada!",
            html: `
            <div class="relatorio_de_venda">
                <h3> R$${vendaAtual.total}</h3>
                <p>${vendaAtual.quantidade}Kg de ${vendaAtual.material.subtipo} para ${vendaAtual.vendedor.razao_social}</p>
            </div>
            <div class="finalizacao_sw">
                <p>Obrigado por registrar sua venda!<br>Isso ajuda toda a comunidade. </p>
                <a href="/registrar-venda">Registrar nova venda</a>
                <a href="/pagina-inicial">Voltar ao ínicio</a>
            </div>
                `,
            color: "var(--verde-escuro)",
            background: "var(--branco)",
            showConfirmButton: false,
            showCancelButton: false,
        })
    })
}

const enviarValores = async (dados) =>{
    await getCoop();
    console.log('dados', JSON.stringify(dados))
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
           tipo = "negativo" 
            break
        case nota >= 3:
            tipo = "positivo"
            break
        }
    renderizarComentarios(tipo);
}

function renderizarComentarios(tipo){
    const comentariosHtml = opcoesSection.querySelector('.comentario');
    comentariosHtml.innerHTML = '';
    comentariosHtml.innerHTML = comentarios.filter(c => c.tipo === tipo).map
    (c => `<button class="comentario__btn comentario-rapido" data-value="${c.texto}">${c.texto}</button>
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
            // Aqui você pode salvar o comentário no objeto da venda, por exemplo:
        });
    })
}




const session_token = localStorage.getItem('session_token');

async function getUsuario (){
    const response = await fetch (
        
        `/api/usuarios/get`, 
        
        {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': session_token
            }
        }
    );
    
    const data_request = await response?.json();
    
    if (!response.ok)
    {
        throw new Error (
    
            'error' in data_request
            ?
            data_request.error
            :
            'Erro Interno. Tente novamente mais tarde.'
    
        );
    }
    
    return data_request;
}

async function getCooperativa(id){
  const response = await fetch (
        
      `/api/cooperativas/get/${id }`, 
      
      {
          method: 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'Authorization': session_token
          }
      }
  );

  const data_request = await response?.json();

  if (!response.ok)
  {
      throw new Error (

          'error' in data_request
          ?
          data_request.error
          :
          'Erro Interno. Tente novamente mais tarde.'

      );
  }

  return data_request;
}


const getCoop = async () =>{
    const user = await getUsuario();
    const cooperativa = await getCooperativa(user.id_usuario);
    vendaAtual.id_cooperativa = cooperativa.dados_cooperativa.id_cooperativa;
}