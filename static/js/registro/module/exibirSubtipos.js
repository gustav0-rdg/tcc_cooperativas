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
    novoSubtipo.textContent = "Outros materiais";

    const materiaisCategoriaAtual = material.filter(
        item => item.categoria === vendaAtual.material.categoria
    );

    const botoesSwal = materiaisCategoriaAtual.map(mat => `<button class="registros__opcoes-btn swal__btn-material-existente"value="${mat.id_material_catalogo}">${mat.nome_padrao}</button>`).join(' ');
 
    novoSubtipo.addEventListener('click', async () => {
        Swal.fire({
            title: 'Algum destes materiais é o mesmo no qual você quer registrar?',
            html: botoesSwal + '<button class="registros__opcoes-btn swal__btn-material-novo">Criar novo material</button>',
            showCancelButton: true,
            showConfirmButton: false,
            cancelButtonText: 'Cancelar',
            color: "var(--verde-escuro-medio)",
            background: "var(--verde-claro-medio)",

            didOpen: () => {

                // adiciona evento de clique aos botões
                const botoes = Swal.getPopup().querySelectorAll('.registros__opcoes-btn');
                botoes.forEach(botao => {
                    // Verifica se o botão é de sinonimo ou novo material
                    if (botao.classList.contains('swal__btn-material-existente')) {
                        // Caso seja sinonimo
                        botao.addEventListener('click', () => {
                            console.log('caiu aqui 3')

                            // informações que serão passadas para o banco de dados
                            let valoresCadastro = {
                                nome_padrao: botao.value,
                                sinonimo: 'Poooo',
                            }
                            Swal.fire({
                                title: 'Escreva o nome que você usa',
                                html: `<input type="text" id="novoNomeMaterial" />`,
                                showCancelButton: true,
                                confirmButtonText: 'Registrar como sinônimo',
                                cancelButtonText: 'Cancelar',
                                color: "var(--verde-escuro-medio)",
                                background: "var(--verde-claro-medio)",
                                preConfirm: () => {
                                    const valor = document.getElementById('novoNomeMaterial').value;
                                    if (!valor) {
                                        Swal.showValidationMessage('Digite algo para o nome!');
                                    }
                                    valoresCadastro.sinonimo = valor // adiciona o sinonimo nas informações que serão passadas
                                    return valoresCadastro;
                                }
                            }).then(async () => {
                                try {
                                    console.log(JSON.stringify(valoresCadastro))

                                    const resposta = await fetch('/post/cadastrar-sinonimo', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify(valoresCadastro)
                                    });
                                    const data = await resposta.json();
                                    if (resposta.ok) {
                                        Swal.fire('Sucesso!', data.message, 'success');
                                    } else {
                                        Swal.fire('Erro!', data.message, 'error');
                                    }
                                } catch (error) {
                                    console.error(error); 
                                    Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
                                }

                            })



                            // Fazer um if de caso de td certo no cadastro
                            Swal.fire({
                                title: 'tudo certo'
                            })
                        })
                    }
                    else {

                    };
                });
            }
        })
    })

    compradorSection.appendChild(novoSubtipo)


    materiaisCategoriaAtual.forEach(item => {
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
            exibirVendedores();
            console.log(vendaAtual); // Apenas para visualização
        });
    });


}