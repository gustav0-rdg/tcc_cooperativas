import { getSubtipos } from "../../api/getSubTipos.js";
import { material } from "../registrar_venda.js";

import { vendaAtual } from "../registrar_venda.js";
import { exibirVendedores } from "./exibirVendedores.js";
const etapaSection = document.querySelector('.registros__etapa');
const opcoesSection = document.querySelector('.registros__opcoes');
const compradorSection = document.querySelector('.registros__comprador');

let valoresCadastro = {
    nome_padrao: undefined,
    sinonimo: undefined,
    id_material_catalogo: undefined, // Adicionei isso
}


// Estilos para o swal
const swalStyles = `
  .swal-content-container {
    display: flex;
    flex-direction: column;
    gap: 15px; /* Um espaçamento geral */
    text-align: left; /* Alinha todo o conteúdo à esquerda */
  }

  .swal-input-label {
    font-size: 1em;
    font-weight: 600;
    color: var(--verde-escuro-medio);
    margin-bottom: -10px; /* Puxa o input para mais perto */
  }

  .swal-input-field {
    width: 100% !important; 
    margin: 0;
    border-radius: 6px !important; 
    background-color: var(--verde-claro);
  }
    .swal-input-field::placeholder{
    color: var(--ver-escuro-medio)}

  /* A lista de materiais */
  .swal-material-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 180px; 
    overflow-y: auto;
    border: 1px solid #ddd;
    padding: 12px;
    border-radius: 6px; 
    background: rgba(255,255,255,0.5); 
  }

  /* Cada opção de rádio (o "botão" que você queria) */
  .swal-radio-option {
    display: flex;
    align-items: center;
    gap: 10px; /* Espaço entre o rádio e o texto */
    cursor: pointer;
    padding: 8px;
    border-radius: 4px; /* Raio menor para os itens */
    transition: background-color 0.2s;
  }
  .swal-radio-option:hover {
    background-color: rgba(0,0,0,0.05);
  }
  .swal-radio-option input[type="radio"] {
    margin: 0;
    flex-shrink: 0; 
  }
  .swal-radio-option label {
    font-weight: 500;
    cursor: pointer;
  }

  .swal-divider {
    display: flex;
    align-items: center;
    text-align: center;
    color: var(--preto);
    gap: 10px;
    font-weight: bold;
    font-size: 0.9em;
    margin: 0;
  }
  .swal-divider::before,
  .swal-divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid var(--verde-escuro);
  }
`;


export async function exibirSubtipos() {
    compradorSection.innerHTML = '';
    const subtipos = await getSubtipos(vendaAtual.material.id_categoria)

    // Debugging (mantido)
    console.log(subtipos, material.id_material_catalogo, material, vendaAtual.material.id_categoria)

    etapaSection.innerHTML = `
        <div class="etapa__progresso">
            <h1>Venda de ${vendaAtual.material.categoria}</h1>
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

    const materiaisCategoriaAtual = subtipos.filter(
        item => item.id_material_base === vendaAtual.material.id_categoria
    );

// Gerando os radios de opção
    const botoesSwalHtml = materiaisCategoriaAtual.map(mat => `
        <div class="swal-radio-option">
            <input type="radio" 
                   name="materialOpcao" 
                   id="mat-${mat.id_material_catalogo}" 
                   value="${mat.id_material_catalogo}" 
                   data-id-catalogo="${mat.id_material_catalogo}">
            <label for="mat-${mat.id_material_catalogo}">${mat.nome_especifico}</label>
        </div>
    `).join('');


    novoSubtipo.addEventListener('click', async () => {
        
        Swal.fire({
            title: 'Vincular ou Criar Material',
            icon: 'question',
            width: '550px',
            html: `
              <style>${swalStyles}</style> <div class="swal-content-container">
                
                <label for="novoNomeMaterial" class="swal-input-label">
                  Qual nome você usa na sua região?
                </label>
                <input type="text" 
                       placeholder="Ex: Garrafa PET, Papelão Klabin" 
                       id="novoNomeMaterial" 
                       class="swal2-input swal-input-field">
                
                <p style="margin: 5px 0 -5px 0; font-weight: 600;">Este material é o mesmo que algum abaixo?</p>
                
                <div id="listaMateriais" class="swal-material-list">
                  ${botoesSwalHtml} </div>
                
                <div class="swal-divider">ou</div>
                
                <div class="swal-radio-option" style="padding: 10px; background: rgba(0,0,0,0.05); border-radius: 6px;">
                  <input type="radio" name="materialOpcao" id="criar" value="criar">
                  <label for="criar">É um material novo (não está na lista)</label>
                </div>
        
              </div>
            `,
            showCancelButton: true,
            showConfirmButton: true,
            confirmButtonText: 'Confirmar',
            cancelButtonText: 'Cancelar',
            color: "var(--verde-escuro-medio)",
            background: "var(--verde-claro-medio)",
            confirmButtonColor: "#1E8449",
            cancelButtonColor: "#7DCEA0",
            preConfirm: async () => {
                const valor = document.getElementById('novoNomeMaterial').value.trim();
                const selecionado = document.querySelector('input[name="materialOpcao"]:checked');

                if (!valor) {
                    Swal.showValidationMessage('Digite o nome do material usado na sua região!');
                    return false;
                }

                if (!selecionado) {
                    Swal.showValidationMessage('Selecione uma das opções da lista ou "Material Novo"!');
                    return false;
                }

                // Se for "criar", chama função para cadastrar novo material
                if (selecionado.value === 'criar') {
                    await cadastrarNovoMaterial(valor, vendaAtual.material.id_categoria);
                
                } else {
                    // =========================================================================
                    // 4. CORREÇÃO NA LÓGICA DE SALVAR
                    // Corrigi a lógica para pegar o ID e o NOME corretamente.
                    // =========================================================================
                    
                    // Pegamos o ID do material padrão pelo 'data-id-catalogo'
                    const idMaterialPadrao = selecionado.dataset.idCatalogo; 
                    const nomeMaterialPadrao = selecionado.value; // O valor agora é o nome

                    // Atualiza o objeto global que será enviado
                    valoresCadastro.nome_padrao = nomeMaterialPadrao;
                    valoresCadastro.sinonimo = valor;
                    valoresCadastro.id_material_catalogo = idMaterialPadrao; // << Ponto chave

                    await cadastrarSinonimo(valoresCadastro);
                }

                return true;
            }
        });
    });
    
    // Adiciona o botão "Outros materiais" na tela
    compradorSection.appendChild(novoSubtipo)

    // Adiciona os botões de materiais existentes
    materiaisCategoriaAtual.forEach(item => {
        const div = document.createElement('button');
        div.className = "registros__opcoes-btn";
        div.setAttribute('data-value', `${item.nome_especifico}`);
        div.innerHTML = `
                <h1>${item.nome_especifico}</h1>
                <small>${vendaAtual.material.categoria}</small>
            `;
        opcoesSection.appendChild(div);

        // Adicionando o evento de clique para o material
        div.addEventListener('click', () => {
            vendaAtual.material.subtipo = item.nome_especifico; // Atualiza o material no objeto vendaAtual
            vendaAtual.material.id_material_catalogo = item.id_material_catalogo; // Guarda o ID também

            exibirVendedores();
            console.log(vendaAtual); // Apenas para visualização
        });
    });
}


async function cadastrarSinonimo(valoresCadastro) {
    try {
        const resposta = await fetch('/post/cadastrar-sinonimo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // O objeto valoresCadastro agora contém (nome_padrao, sinonimo, id_material_catalogo)
            body: JSON.stringify(valoresCadastro) 
        });

        const data = await resposta.json();

        if (resposta.ok) {
            await Swal.fire('✅ Sucesso!', data.message, 'success');
        } else {
            await Swal.fire('❌ Erro!', data.message, 'error');
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
    }
    finally {
        exibirSubtipos() // Recarrega a lista
    }
}

async function cadastrarNovoMaterial(nomeMaterial, id_material_base) {
    try {
        const resposta = await fetch('/post/cadastrar-subtipo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome_especifico: nomeMaterial, id_material_base: id_material_base })
        });

        const data = await resposta.json();

        if (resposta.ok) {
            await Swal.fire('🎉 Material cadastrado!', data.message, 'success');
        } else {
            await Swal.fire('❌ Erro!', data.message, 'error');
        }
    } catch (error) {
        console.error(error);
        Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
    }
    finally {
        exibirSubtipos() // Recarrega a lista
    }
}