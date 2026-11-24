# Procurador de Vagas

Orquestrador de recolocação profissional com um agente **Maestro** que conhece o perfil do usuário e delega tarefas para agentes especializados: **SCOUT** (vagas), **CURATOR** (cursos) e **COACH** (simulação de entrevistas).

## Funcionalidades

- **Saudação inicial**: apresenta o Maestro e inicia o fluxo de atendimento.
- **Verificação de perfil**: detecta se já existe um perfil salvo em `data/user-profile.md`.
- **Quiz de perfil**: coleta área principal, senioridade, modalidade, localização, faixa salarial e competências dominadas.
- **Mapeamento automático de funções-alvo**: gera cargos compatíveis com base na área e senioridade informadas.
- **Persistência em Markdown**: salva e carrega o perfil do usuário em `data/user-profile.md`.
- **Menu principal interativo**:
  - `A) Buscar vagas (SCOUT)` — busca vagas com base no perfil
  - `B) Buscar cursos (CURATOR)` — busca cursos na Alura e DIO
  - `C) Simular entrevista (COACH)` — simulações personalizadas com feedback
  - `D) Refazer quiz`
  - `E) Ver perfil salvo`
  - `F) Sair`
- **SCOUT**: busca e apresenta vagas de tecnologia com base no perfil do usuário.
- **CURATOR**: busca cursos, permite seleção numerada e exibe detalhes da página.
- **COACH**: realiza simulações de entrevista e fornece avaliação estruturada.

## Linguagens e Tecnologias

- **Python 3**: linguagem principal da implementação (`maestro.py`, `curator.py`, `coach.py`).
- **Markdown**: documentação (`README.md`, `AGENTS.md`, planos) e persistência do perfil (`data/user-profile.md`).
- **Firecrawl**: integração para busca/coleta de conteúdo web (SCOUT/CURATOR), configurada via `.env`.

## Estrutura do Projeto

- `maestro.py` — orquestrador principal (fluxo, quiz, menu, delegação).
- `curator.py` — agente CURATOR (busca de cursos).
- `coach.py` — agente COACH (simulação de entrevistas).
- `AGENTS.md` — especificação dos agentes e diretrizes de comportamento.
- `plano.md` — plano principal do orquestrador.
- `plano-aula-2.md` — plano do agente SCOUT.
- `plano-aula-3.md` — plano do agente CURATOR.
- `.github/skills/scout/SKILL.md` — procedimento operacional do SCOUT.
- `.github/skills/curator/SKILL.md` — procedimento operacional do CURATOR.
- `.github/skills/coach/SKILL.md` — procedimento operacional do COACH.
- `data/` — perfil do usuário e resultados gerados (jobs/courses/interviews).
- `.env.example` — modelo de configuração (ex.: `FIRECRAWL_API_KEY`).
- `requirements.txt` — dependências Python.

## Como Executar

1. Certifique-se de ter o **Python 3** instalado.
2. (Opcional) Crie e ative um ambiente virtual.
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:

   ```bash
   copy .env.example .env
   ```

   Edite `.env` e defina `FIRECRAWL_API_KEY`.

5. Execute o Maestro:

   ```bash
   python maestro.py
   ```

## Status do Projeto

- **Fase 1**: Maestro com saudação, quiz, persistência de perfil e menu principal.
- **Fase 2**: SCOUT integrado para busca de vagas.
- **Fase 3**: CURATOR integrado para busca de cursos.
- **Fase 4**: COACH integrado para simulação de entrevistas.
- **Evolução futura**: melhorias de persistência, ranking/recomendações e refinamento dos agentes.