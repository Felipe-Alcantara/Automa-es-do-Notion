#!/usr/bin/env python3
"""Cria, sem duplicar, o lote investigado de tarefas pessoais de 18/08/2026.

Uso:
    python3 criar_tarefas_investigadas_2026_08_18.py

O script consulta a database antes de criar cada título, portanto pode ser
executado novamente depois de uma falha de rede. Propriedades e conteúdo
nascem na mesma chamada ``notion-tasks criar``; as relações são idempotentes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


PERFIL = "home-pessoal"
DATABASE_ID = "30296e2d-cd39-4cf3-8bbd-3fb2f53c0195"
AREA_ARTIGOS = "1fe91f95-497e-802d-b069-dfc0f91d0634"
AREA_PRODUTOS = "1fe91f95-497e-8123-92b5-e7afa33f97e1"
PROJETO_FELIXO = "38e91f95-497e-81d9-8770-fd20886c9232"

TAREFA_PRISMA_EXISTENTE = "3b891f95-497e-8166-8a24-c381eb186093"
TAREFA_AUDIOFY_FLAVIA = "3a691f95-497e-815a-abd1-fdf6b9a52939"
TAREFA_AUDIOFY_CAMERON = "3a691f95-497e-8137-82d8-f135d9e635e0"


@dataclass(frozen=True)
class Tarefa:
    chave: str
    titulo: str
    esforco: str
    prioridade: str
    area: str
    referencia: str
    conteudo: str
    projeto: str | None = None


def executar(*argumentos: str) -> dict[str, Any]:
    resultado = subprocess.run(
        ["notion-tasks", "--json", "--perfil", PERFIL, *argumentos],
        check=False,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip() or resultado.stdout.strip())
    try:
        resposta = json.loads(resultado.stdout)
    except json.JSONDecodeError as erro:
        raise RuntimeError(f"Saída não JSON de {' '.join(argumentos)}: {resultado.stdout}") from erro
    if not resposta.get("ok"):
        raise RuntimeError(str(resposta))
    return resposta


def ids_por_titulo() -> dict[str, str]:
    dados = executar("linhas", DATABASE_ID).get("dados", {})
    linhas = dados.get("linhas", []) if isinstance(dados, dict) else []
    encontrados: dict[str, str] = {}
    for linha in linhas:
        if not isinstance(linha, dict):
            continue
        titulo = linha.get("titulo") or linha.get("Tarefa")
        identificador = linha.get("id")
        if isinstance(titulo, str) and isinstance(identificador, str):
            encontrados[titulo] = identificador
    return encontrados


def id_criado(resposta: dict[str, Any]) -> str:
    dados = resposta.get("dados", {})
    if isinstance(dados, dict) and isinstance(dados.get("id"), str):
        return dados["id"]
    raise RuntimeError(f"A criação não devolveu o id da página: {resposta}")


def garantir_tarefa(tarefa: Tarefa, existentes: dict[str, str]) -> str:
    existente = existentes.get(tarefa.titulo)
    if existente:
        print(f"[pula] {tarefa.titulo} ({existente})")
        return existente

    argumentos = [
        "criar",
        tarefa.titulo,
        "--status",
        "Entrada",
        "--duracao",
        tarefa.esforco,
        "--area",
        tarefa.area,
        "--set",
        f"Prioridade={tarefa.prioridade}",
        "--set",
        f"URL de referência={tarefa.referencia}",
    ]
    if tarefa.projeto:
        argumentos.extend(["--set", f"Projeto={tarefa.projeto}"])
    argumentos.extend(["--conteudo", tarefa.conteudo])
    criado = id_criado(executar(*argumentos))
    existentes[tarefa.titulo] = criado
    print(f"[cria] {tarefa.titulo} ({criado})")
    return criado


def relacionar(a: str, b: str) -> None:
    executar("relacionar", a, b, "--coluna", "Subtarefas relacionadas")
    print(f"[relaciona] {a} <-> {b}")


TAREFAS = (
    Tarefa(
        chave="luna",
        titulo="Escrever o artigo “Minha experiência com GPT-5.6 Luna: explícito vence implícito”",
        esforco="Muitas horas",
        prioridade="Média",
        area=AREA_ARTIGOS,
        referencia="https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/",
        conteudo="""## Contexto

Anotação original: *“Minha Experiencia com o Luna: Explícito > Implícito”*. O artigo é um relato técnico pessoal sobre como trabalhar bem com o **GPT-5.6 Luna**, contrastando instruções explícitas com pressupostos implícitos e a ideia de que programação cotidiana não exige usar sempre um modelo de fronteira como Claude Fable.

Fontes primárias já conferidas: [lançamento da família GPT-5.6](https://openai.com/index/gpt-5-6/), [preço/desempenho do Luna](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/) e [catálogo do modelo](https://developers.openai.com/api/docs/models/gpt-5.6-luna). Em 30/07/2026, a OpenAI reduziu o preço do Luna em 80%; o catálogo o posiciona para alto volume e custo sensível, com janela de 1,05 milhão de tokens e preço de US$ 0,20/MTok de entrada e US$ 1,20/MTok de saída. Esses números precisam ser datados no artigo, não apresentados como permanentes.

## O que a investigação encontrou

- Não foi encontrado, nos repositórios lidos, um diário de prompts, custos ou comparativo pessoal que sustente frases quantitativas sobre “minha experiência”. O texto deve separar **experimento reproduzível**, observação pessoal e fato do fornecedor.

- A tese “explícito > implícito” é publicável como argumento editorial, mas precisa mostrar contraexemplos: instrução excessiva pode aumentar custo, engessar a solução ou repetir informação que o contexto já fornece.

- O artigo histórico sobre LLMs criado neste mesmo lote é relacionado porque oferece o pano de fundo da evolução de capacidade/preço; ele não substitui a evidência prática do Luna.

## O que fazer

1. Criar um caderno de evidências com 6–10 tarefas reais comparáveis: objetivo, contexto entregue, prompt explícito/implícito, modelo, data, tentativas, tempo, custo e resultado revisado por humano. Remover nomes de clientes, chaves, caminhos privados e conversas pessoais antes de usar como exemplo.

1. Definir “eficiente e funcional” por critérios observáveis: taxa de conclusão aceita, retrabalho humano, latência e custo por tarefa. Não escolher o vencedor apenas pela impressão do autor.

1. Escrever o roteiro: o problema de depender do implícito; o que tornou a instrução explícita; quando Luna foi suficiente; quando subir para Terra/Sol ou outro modelo foi racional; limites da comparação; conclusão editorial.

1. Tratar “nenhum programador precisa de um Claude Fable” como provocação, não como fato universal: delimitar classe de trabalho, risco de erro, autonomia e orçamento que tornam um modelo maior justificável.

1. Criar uma linha na database de Artigos, escrever o rascunho lá, fazer revisão factual/linguística e só então preparar publicação no blog.

## Pontos de atenção

- Capturar versão, data, plano/limite e configuração de raciocínio: preços, limites e comportamento do modelo mudam.

- Não expor prompts de sistema, dados de terceiros, IDs de sessão ou qualquer segredo para tornar o relato mais convincente.

- Não atribuir à OpenAI uma conclusão que é do autor; links primários sustentam características do produto, não a vivência pessoal.

## Critérios de aceite

- Rascunho com tese, contraargumento e pelo menos 6 comparações reproduzíveis ou declaradas explicitamente como anedóticas.

- Toda afirmação de preço, capacidade ou disponibilidade tem fonte primária e data.

- A recomendação de modelo é condicionada a risco/custo/escala, sem vender Luna como solução universal.

- Linha da database de Artigos criada com estado editorial rastreável e revisão concluída antes da publicação.

---

## 🔗 Tarefas relacionadas

- **Pesquisar e estruturar o artigo “A história dos LLMs contemporâneos: do GPT-3 ao Claude Mythos”** — compartilha a base factual de evolução de modelos; esta tarefa usa essa linha do tempo apenas como contexto, enquanto o foco aqui é experiência e método de trabalho com Luna.""",
    ),
    Tarefa(
        chave="codex",
        titulo="Felixo AI Core — trocar a conta do Codex sem romper a sessão do canvas",
        esforco="Muitas horas",
        prioridade="Alta",
        area=AREA_ARTIGOS,
        projeto=PROJETO_FELIXO,
        referencia="https://github.com/Felipe-Alcantara/Felixo-AI-Core",
        conteudo="""## Contexto

Quando uma conta do Codex atingir limite, deve ser possível ver qual conta está autenticada e trocar para outra sem obrigar a pessoa a reconstruir o trabalho no canvas. A referência de UX é a extensão do VS Code: a troca de credencial não deve apagar a continuidade lógica da sessão no repositório.

Repositório: [Felixo-AI-Core](https://github.com/Felipe-Alcantara/Felixo-AI-Core).

## O que a investigação encontrou

Esta não é uma feature inexistente: há uma primeira implementação parcial.

- `app/electron/core/official-cli-catalog.cjs:31–44` declara, **somente para Codex**, `codex login status` e `codex logout`.

- `app/electron/services/official-cli-service.cjs:93–172` consulta apenas o estado `logged_in/logged_out/unknown`, executa logout e abre o login em **terminal externo**. O parser em `:304–325` não obtém identidade, plano ou conta ativa.

- `app/src/features/chat/components/ModelManagerModal.tsx:189–264` e `:551–579` expõem os botões “Status da conta” e “Trocar conta”. Portanto o pedido real é completar e tornar seguro o fluxo, não duplicar botões.

- O canvas já mantém a identidade da PTY separada do componente em `terminal-session-store.ts:236–289` (`ptySessionId = canvas:<id>`). Isso preserva o processo na navegação/remount, mas não prova que uma CLI já em execução aceitará credenciais trocadas. Não prometer “mesma sessão” antes de medir essa fronteira da CLI.

Os commits recentes do repositório incluem `abfae67` (contexto por arquivo), `cb5d3e8` (Vite órfão) e `9dc9592` (atualização macOS), então a mudança precisa evitar interferir em sessões de terminal e no launcher que estão sendo estabilizados agora.

## O que fazer

1. Confirmar no Codex CLI instalado e na documentação oficial quais dados de identidade/status são disponíveis sem ler arquivo de credencial diretamente. Nunca persistir token, cookie ou e-mail em log/telemetria.

1. Mapear, com experimento manual controlado, os três estados: sessão Codex ociosa, sessão em execução e sessão encerrada. Para cada um, verificar o que acontece após logout/login em outra conta, inclusive se o processo antigo conserva autorização, falha, ou precisa de restart explícito.

1. Definir contrato de UX: mostrar identidade somente quando a CLI a fornecer; avisar o efeito sobre terminais ativos; permitir cancelar; e oferecer retomar/reiniciar o terminal com o mesmo `canvas:<id>` quando isso for necessário. Não matar PTYs silenciosamente.

1. Evoluir catálogo, serviço/IPC, preload e UI respeitando as camadas existentes. A operação de conta fica no serviço oficial; a UI não executa shell nem interpreta credenciais.

1. Registrar a limitação real: preservar o cartão/histórico do canvas não equivale a preservar autenticação ou contexto interno de um processo Codex que já nasceu com outra conta.

1. Cobrir contrato e regressões: parsing de status/identidade, plataforma Windows (`.cmd`), falha/timeout de logout, cancelamento, sessão viva e reinício deliberado. Fazer verificação manual objetiva no Linux, macOS e Windows com duas contas autorizadas, sem expor seus dados.

1. Atualizar `README.md` e `IA.md` com fluxo, impacto em sessões abertas, limitação e comandos de recuperação; rodar o gate documentado (`npm test`, lint, build e testes do launcher).

## Pontos de atenção

- “Trocar conta” é ação sensível: logout não pode ocorrer em clique acidental, nem uma resposta de status pode vazar stdout que contenha token.

- Não deduzir identidade por caminho em `~/.codex` nem armazenar múltiplos segredos no app. A fonte de verdade deve ser a CLI/fluxo OAuth.

- Uma sessão em andamento pode ter efeitos externos; a interface deve priorizar esperar/cancelar conscientemente em vez de prometer continuidade impossível.

## Critérios de aceite

- A tela informa estado e identidade da conta apenas quando a CLI a disponibiliza, sem segredo em UI, log ou teste.

- A troca exige confirmação e deixa explícito o tratamento de cada terminal ativo.

- Após o fluxo, o canvas mantém o nó, diretório e histórico; quando o Codex exigir novo processo, o reinício é explícito e reaproveita a configuração do terminal.

- Casos de sucesso, erro, timeout e Windows são automatizados; execução manual com duas contas é registrada para Linux, macOS e Windows.

- README/IA.md descrevem comportamento e risco residual, e o gate do projeto passa.""",
    ),
    Tarefa(
        chave="historia",
        titulo="Pesquisar e estruturar o artigo “A história dos LLMs contemporâneos: do GPT-3 ao Claude Mythos”",
        esforco="Muitas horas",
        prioridade="Média",
        area=AREA_ARTIGOS,
        referencia="https://openai.com/index/language-models-are-few-shot-learners/",
        conteudo="""## Contexto

Produzir pesquisa e registros que sustentem um artigo sobre a evolução contemporânea dos LLMs, do GPT-3 ao Claude Mythos, sem transformar uma linha do tempo de lançamentos em narrativa de marketing.

Fontes primárias já identificadas: [GPT-3 / *Language models are few-shot learners*](https://openai.com/index/language-models-are-few-shot-learners/) (28/05/2020, 175 bilhões de parâmetros), [introdução do Claude](https://www.anthropic.com/news/introducing-claude) (14/03/2023), [família Claude 3](https://www.anthropic.com/news/claude-3-family) (04/03/2024), [Claude 4](https://www.anthropic.com/news/claude-4) (22/05/2025) e [Claude Mythos Preview](https://www.anthropic.com/research/mythos-preview) (07/04/2026).

## O que a investigação encontrou

- O título não usa um nome inventado: a Anthropic publicou material oficial sobre **Claude Mythos Preview**. A fonte também diz que ele não é lançamento geral; está restrito ao programa defensivo Project Glasswing. O artigo não pode tratá-lo como produto disponível ao público.

- GPT-3 é um bom marco inicial por documentar a virada do few-shot via texto, mas não é o começo histórico dos LLMs. A introdução deve declarar que “contemporânea” é um recorte editorial iniciado em 2020, não uma história total do campo.

- A tarefa do artigo sobre GPT-5.6 Luna é relacionada: ela oferece um caso prático de custo/uso no fim da linha do tempo, mas não deve contaminar a seção histórica com opinião pessoal.

## O que fazer

1. Montar uma base de fontes com URL primária, data de publicação, data do evento, tipo (paper, lançamento, system card), modelo/família, disponibilidade, preço/contexto quando aplicável, e trecho/paráfrase que sustenta cada afirmação.

1. Delimitar o recorte: GPT-3 → instrução/few-shot; ChatGPT e uso conversacional; Claude e alinhamento/constitucionalidade; multimodalidade, janelas de contexto, tool use, agentes/coding; famílias custo/velocidade; segurança e acesso restrito no Mythos. Incluir os saltos que forem materialmente necessários, em vez de selecionar apenas vencedores.

1. Separar três camadas no roteiro: fatos de lançamento, interpretações técnicas e consequências sociais/profissionais. Toda inferência deve apontar seus fatos de base e grau de certeza.

1. Fazer revisão cruzada de datas, nomes, preços e disponibilidade contra a fonte primária mais recente. Se uma página tiver sido atualizada, preservar no registro a data da atualização e a versão consultada.

1. Registrar controvérsias e limites: benchmark não mede valor de produto; contexto anunciado não equivale a compreensão; maior capacidade traz custo, segurança e acesso desigual.

1. Escrever outline, bibliografia comentada e primeiro rascunho na database de Artigos; revisar antes de qualquer publicação.

## Pontos de atenção

- Não confundir data de paper, preview, disponibilidade API e disponibilidade em chat.

- Não usar ranking de benchmark como substituto de evidência de trabalho real.

- Citações de fontes secundárias podem contextualizar recepção, mas fatos de produto devem manter fonte primária.

## Critérios de aceite

- Linha do tempo com cada marco verificável por URL primária, data e nota de disponibilidade.

- Roteiro diferencia fato, inferência e opinião; Claude Mythos Preview é descrito com sua restrição de acesso.

- Há contrapontos técnicos e sociais, não só narrativa de escala crescente.

- Rascunho e bibliografia estão registrados na database de Artigos e passam por revisão factual.

---

## 🔗 Tarefas relacionadas

- **Escrever o artigo “Minha experiência com GPT-5.6 Luna: explícito vence implícito”** — fornece a aplicação prática no presente da linha do tempo; a relação evita repetir pesquisa de fontes, sem misturar o relato pessoal com a cronologia.""",
    ),
    Tarefa(
        chave="prisma_backlog",
        titulo="Prisma — consolidar estado atual e gerar backlog validado com GPT-5.6 Sol",
        esforco="Dias",
        prioridade="Alta",
        area=AREA_PRODUTOS,
        referencia="https://github.com/flaviavs-commits/Meu-Ecoo-Prisma",
        conteudo="""## Contexto

A lista de tarefas pessoal não acompanha o projeto principal Prisma porque o desenvolvimento ocorre no Mac de trabalho. Esta tarefa é uma investigação controlada usando GPT-5.6 Sol para ler o acervo do Prisma, separar decisão vigente de documento histórico e produzir backlog executável, documentação atualizada e rastreável.

Repositório: [flaviavs-commits/Meu-Ecoo-Prisma](https://github.com/flaviavs-commits/Meu-Ecoo-Prisma) (público). Esta investigação consultou uma cópia temporária de leitura do `main` em 18/08/2026: **160 commits**, HEAD `87776bf` (`docs(diretor): registra bloqueio de publicacao`). O checkout do Mac de trabalho não está neste computador e deve ser a fonte operacional a inventariar antes de qualquer conclusão.

## O que a investigação encontrou

- O `AGENTS.md` ainda diz que “o backend ainda não existe em código”, mas o `README.md` e o histórico mais recente contradizem isso: há Django/DRF, integração do Resumo (`347074b`), painel do diretor (`76a09e9`) e operações de chave OpenRouter (`4eed55e`). A tarefa deve registrar esta divergência e corrigir documentos apenas com evidência, nunca escolher o texto mais conveniente.

- `IA.md` de 17/08 marca a publicação do frontend funcional do Resumo e o painel acadêmico como concluídos/localmente publicados, mas registra bloqueio externo de deploy Railway por upstream GitHub. Portanto “feito” precisa ser classificado em código, publicado, validado remotamente e bloqueado — não num único booleano.

- `docs/backend/contratos/API-MODULOS-IA.md:32–35` registra Resumo integrado e Simulado/Flashcards/Áudio-revisão como esqueletos. Em `:40–50`, a documentação corrige uma premissa antiga: Audiofy é o motor real de Áudio-revisão, não apenas referência de terceiro.

- A relação com a tarefa existente [Prisma — Resumo com IA](https://app.notion.com/p/Prisma-Resumo-com-IA-ler-organizar-e-desenvolver-o-m-dulo-entregue-pela-equipe-3b891f95497e81668a24c381eb186093) é de causa compartilhada: o novo backlog precisa absorver seu estado atualizado, não recriar uma tarefa baseada no snapshot anterior.

## O que fazer

1. No Mac de trabalho, criar inventário somente leitura: branch/commit, `git status`, remotes, `git log --oneline`, árvore de documentos, módulos, deploys conhecidos e comandos de validação. Guardar hashes/data de cada fonte analisada.

1. Ler, nesta ordem, `AGENTS.md`, o guia mínimo de qualidade sincronizado, resumo vivo de `IA.md`, `README.md`, `docs/backend/README.md`, protocolo de agente e somente as etapas/contratos relacionados ao achado. Usar GPT-5.6 Sol como analisador, mas não enviar `.env`, credenciais, dados de aluno ou conteúdo privado ao modelo.

1. Construir matriz de evidências por afirmação: documento que a declara, código/commit/teste/deploy que a confirma ou contradiz, estado (vigente, histórica, pendente, bloqueada, divergente) e ação recomendada.

1. Atualizar ou arquivar documentação apenas quando a matriz provar obsolescência. Preservar decisões e histórico no `IA.md` por entrada datada; não apagar texto antigo para “limpar”. Divergências sem prova ficam explicitamente aguardando decisão/validação.

1. Converter cada lacuna comprovada em tarefa independente nesta database: título acionável, contexto, arquivos/funções/commit, dependências, riscos, passos e critérios de aceite. Relacionar tarefas por módulo e contrato em vez de criar uma task-monstro.

1. Priorizar a fila com base em risco ao usuário/segredo/dados, bloqueio de produção, dependência técnica e valor de demonstração. Não usar apenas ordem do documento ou entusiasmo do modelo.

1. Produzir relatório de consolidação com contagem de itens por estado e ligações para decisões, depois rodar os gates aplicáveis em modo leitura/validação e registrar o que não pôde ser executado.

## Pontos de atenção

- O repositório é público: nunca copiar segredo, URL interna, e-mail de usuário, dump ou configuração de Railway para prompt, task ou documentação pública.

- O modelo pode resumir errado documentos que se contradizem; commit, teste e deploy observável têm precedência sobre texto narrativo.

- Não tratar mockup estático como fluxo autenticado; o próprio README diferencia `/app/` de rotas efetivamente conectadas.

- Não remover documentação ou tarefas por parecer “antiga”; marcar histórico e pedir decisão quando a mudança de produto não for dedutível.

## Critérios de aceite

- Inventário do checkout do Mac com commit, branch, estado limpo/sujo, fontes e data da leitura.

- Matriz de evidências cobre todos os módulos e classifica cada afirmação como vigente, histórica, pendente, bloqueada ou divergente.

- Backlog criado no Notion em tarefas atômicas, com relações/dependências e critérios verificáveis; nenhuma tarefa repete um trabalho já concluído sem justificar regressão.

- IA.md/docs atualizados por adição datada e com links para a evidência; nenhuma exclusão de decisão histórica ocorre sem autorização explícita.

- Relatório final lista validações executadas, pendências externas e risco residual.

---

## 🔗 Tarefas relacionadas

- [Prisma — Resumo com IA: ler, organizar e desenvolver o módulo entregue pela equipe](https://app.notion.com/p/Prisma-Resumo-com-IA-ler-organizar-e-desenvolver-o-m-dulo-entregue-pela-equipe-3b891f95497e81668a24c381eb186093) — mesma fonte e mesmo contrato de módulos; o backlog deve reconciliar o estado atual do Resumo antes de gerar novas ações.

- **Prisma/MeuEcoo — preparar versão demonstrável e pacote editorial para o vídeo de investidores** — é dependente deste diagnóstico: gravação e roteiro só podem prometer funcionalidades que a matriz classificou como demonstráveis.""",
    ),
    Tarefa(
        chave="video",
        titulo="Prisma/MeuEcoo — preparar versão demonstrável e pacote editorial para o vídeo de investidores",
        esforco="Dias",
        prioridade="Alta",
        area=AREA_PRODUTOS,
        referencia="https://github.com/Felipe-Alcantara/Audiofy-Content-AI",
        conteudo="""## Contexto

Depois de consolidar o estado real do Prisma, preparar a demonstração e os materiais para um vídeo de investidores sobre **Prisma** e o ecossistema **MeuEcoo**. O áudio será gerado pelo [Audiofy Content AI](https://github.com/Felipe-Alcantara/Audiofy-Content-AI); o plano operacional comunicado à Flávia é: capturar telas com Screen Studio, produzir textos por funcionalidade/tela, revisão e aprovação do Tiago, gerar áudio, montar o vídeo e, se necessário, passar a edição de sincronização ao Mateus.

Esta tarefa depende de **Prisma — consolidar estado atual e gerar backlog validado com GPT-5.6 Sol**. Não iniciar gravação dizendo que algo está pronto antes de essa análise separar código, deploy, mockup e bloqueio externo.

## O que a investigação encontrou

- O Prisma público está no commit `87776bf` e declara backend/Resumo/painel do diretor recentes, mas o `IA.md` também registra bloqueio de deploy Railway em 17/08. Isso impede transformar tela ou código local em promessa de produção sem validação.

- `docs/backend/contratos/API-MODULOS-IA.md:40–50` corrige a decisão anterior: o Audiofy é o motor real planejado para Áudio-revisão. Portanto o vídeo deve apresentá-lo como integração planejada/validada no estágio que a matriz do Prisma confirmar, não como recurso já disponível ao aluno sem prova.

- O Audiofy já possui roteiro factual para [Flávia](https://github.com/Felipe-Alcantara/Audiofy-Content-AI/blob/main/docs/APRESENTACAO-AUDIOFY-FLAVIA.md) e [Cameron](https://github.com/Felipe-Alcantara/Audiofy-Content-AI/blob/main/docs/PRESENTATION-AUDIOFY-CAMERON.md). O `IA.md` do Audiofy registra 12 episódios, 5h40min55s, 50.024 palavras e US$ 6,85 (US$ 0,57 por episódio; US$ 0,02/min) como base factual em 17/08. Reaproveitar estes números exige manter data, fonte e mesmo enquadramento nas apresentações.

- Não foram encontrados no repositório do Prisma materiais de captura, pasta de Drive compartilhada, aprovação do Tiago nem brief de edição do Mateus. Esses itens são entradas a obter e confirmar, não fatos a presumir.

## O que fazer

1. Consumir a matriz de evidências da tarefa anterior e congelar uma lista de cenas: funcionalidade, rota/ambiente, papel demonstrado, estado (produção, validação controlada, mockup) e prova. Excluir ou rotular explicitamente tudo que não estiver demonstrável.

1. Confirmar com a pessoa responsável onde os arquivos serão guardados, quem pode ver o Drive e qual versão é aprovada para gravação. Não enviar dados de alunos, tokens, URLs privadas ou telas administrativas sensíveis ao editor/Drive.

1. Produzir uma fonte factual única para Prisma + MeuEcoo + Audiofy: problema, público, telas, funcionalidades, números, riscos, próximos passos e linguagem proibida (por exemplo, não chamar mockup de integração). Derivar dela os textos de narração e textos de tela, em vez de escrever versões conflitantes.

1. Pedir ao Tiago revisão objetiva do roteiro: checklist por afirmação, aprovação/rejeição, alterações e data. Sem aprovação, marcar o texto como rascunho e não gerar versão final de áudio.

1. Gerar no Audiofy um episódio/trechos de narração a partir do roteiro aprovado, seguindo `AGENTS.md`: conteúdo auditável, custo/voz/modelo registrados, direitos de música conferidos e revisão humana do áudio. Rodar `python scripts/check_quality.py` se houver alteração no repositório; se for só operação, registrar comando, perfil, custo e artefatos gerados.

1. Capturar no Screen Studio somente os fluxos aprovados, com resolução, duração e origem listadas em manifesto. Gravar novamente qualquer cena cuja rota, idioma ou dado de demonstração divergir do roteiro.

1. Montar o vídeo com timeline que vincule cada trecho de áudio à cena e ao roteiro; entregar ao Mateus, se necessário, um pacote autocontido (áudios aprovados, capturas, roteiro versionado, fontes e instruções de sincronização), sem segredos.

1. Fazer revisão final com Tiago/Flávia: checar áudio, sincronização, acessibilidade básica (legendas se exigidas), números, nomes, estado das features e autorização de publicação. Registrar versão, aprovador e riscos que permanecerem.

## Pontos de atenção

- “Site alinhado” não pode significar alterar produção só para filmar. Toda mudança de código deve passar pelo padrão de qualidade, testes e validação proporcional; se não estiver pronta, o caminho correto é remover a cena ou rotulá-la como visão.

- Não gastar créditos de áudio antes de o texto estar aprovado. Regravação por roteiro errado é custo e também cria versões ambíguas.

- A divisão Tiago/Mateus é de responsabilidade editorial: Tiago aprova conteúdo; Mateus pode sincronizar edição, não aprovar afirmação de produto em nome dele.

- O cronograma “hoje/amanhã” depende de disponibilidade humana e permissão do Drive; registrar bloqueio em vez de declarar prazo cumprido por inferência.

## Critérios de aceite

- Cada cena do vídeo possui rota, estado técnico, evidência e rótulo honesto; nenhuma feature mockada ou bloqueada é vendida como disponível.

- Existe fonte factual única, roteiro versionado e revisão do Tiago registrada antes do áudio final.

- Áudios gerados pelo Audiofy têm artefatos, custo/modelo/voz e revisão humana rastreáveis; nenhuma credencial ou dado pessoal foi incluído.

- Pacote de captura/edição contém manifesto de arquivos, timeline de áudio→cena e instruções suficientes para o Mateus continuar sem reinterpretar o produto.

- Versão final foi revisada pelos responsáveis definidos, com decisões, pendências e autorização de envio registradas.

---

## 🔗 Tarefas relacionadas

- **Prisma — consolidar estado atual e gerar backlog validado com GPT-5.6 Sol** — dependência direta: a matriz define o que é seguro demonstrar e o que precisa ser rotulado ou removido.

- [Prisma — Resumo com IA: ler, organizar e desenvolver o módulo entregue pela equipe](https://app.notion.com/p/Prisma-Resumo-com-IA-ler-organizar-e-desenvolver-o-m-dulo-entregue-pela-equipe-3b891f95497e81668a24c381eb186093) — compartilha o contrato de módulos de IA e evita apresentar o estágio do Resumo com base em documentação antiga.

- [Audiofy Content AI — apresentação para a Flávia](https://app.notion.com/p/Audiofy-Content-AI-Criar-a-apresenta-o-do-aplicativo-para-a-Fl-via-3a691f95497e815aabd1fdf6b9a52939) e [versão para Cameron](https://app.notion.com/p/Audiofy-Content-AI-Criar-a-apresenta-o-do-aplicativo-para-o-Cameron-em-ingl-s-3a691f95497e813782d8f135d9e635e0) — reutilizar a fonte factual já validada e manter números/risco consistentes entre os materiais de investidores.""",
    ),
)


def main() -> int:
    existentes = ids_por_titulo()
    ids = {tarefa.chave: garantir_tarefa(tarefa, existentes) for tarefa in TAREFAS}

    for a, b in (
        (ids["luna"], ids["historia"]),
        (ids["prisma_backlog"], TAREFA_PRISMA_EXISTENTE),
        (ids["prisma_backlog"], ids["video"]),
        (ids["video"], TAREFA_PRISMA_EXISTENTE),
        (ids["video"], TAREFA_AUDIOFY_FLAVIA),
        (ids["video"], TAREFA_AUDIOFY_CAMERON),
    ):
        relacionar(a, b)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise SystemExit(1)
