# Procurador de Vagas

Orquestrador de recolocação profissional com um agente **Maestro** que conhece o perfil do usuário e prepara o terreno para agentes especializados em busca de vagas, cursos e simulação de entrevistas.

## Funcionalidades

- **Saudação inicial**: apresenta o Maestro e inicia o fluxo de atendimento.
- **Verificação de perfil**: detecta se já existe um perfil salvo em `data/user-profile.md`.
- **Quiz de perfil (5 perguntas)**: coleta área principal, senioridade, modalidade, localização e faixa salarial.
- **Mapeamento automático de funções-alvo**: gera cargos compatíveis com base na área e senioridade informadas.
- **Persistência em Markdown**: salva e carrega o perfil do usuário em `data/user-profile.md`.
- **Menu principal interativo**:
  - `A) Buscar vagas (SCOUT)` — reservado para fase futura
  - `B) Buscar cursos (CURATOR)` — reservado para fase futura
  - `C) Simular entrevista (COACH)` — reservado para fase futura
  - `D) Refazer quiz`
  - `E) Ver perfil salvo`
  - `F) Sair`
- **Preparação para agentes futuros**: estrutura pronta para integração dos agentes SCOUT, CURATOR e COACH.

## Linguagens e Tecnologias

- **Python 3**: linguagem principal da implementação (`maestro.py`).
- **Markdown**: usado para documentação (`README.md`, `AGENTS.md`, `plano.md`) e persistência do perfil (`data/user-profile.md`).

## Estrutura do Projeto

- `maestro.py` — implementação do agente Maestro (fluxo principal, quiz, menu e persistência).
- `AGENTS.md` — especificação do agente orquestrador e diretrizes de comportamento.
- `plano.md` — plano de arquitetura e evolução do projeto.
- `data/user-profile.md` — perfil salvo do usuário (gerado após o quiz).
- `.env.example` — exemplo de variáveis de ambiente.
- `requirements.txt` — dependências do projeto.

## Como Executar

1. Certifique-se de ter o **Python 3** instalado.
2. (Opcional) Crie e ative um ambiente virtual.
3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute o Maestro:

   ```bash
   python maestro.py
   ```

## Status do Projeto

- **Fase 1 (concluída)**: Maestro funcional com saudação, quiz, persistência de perfil, menu principal e preparação para agentes futuros.
- **Fases futuras**: implementação dos agentes SCOUT (busca de vagas), CURATOR (cursos) e COACH (simulação de entrevistas).