# AGENTS.md - Orquestrador de Recolocação Profissional

## Visão Geral
Este documento descreve o **Maestro**, o agente orquestrador principal que recebe demandas do usuário e delega para agentes especializados. O Maestro é a única interface com o usuário e controla todo o fluxo de trabalho.

## Estrutura do Maestro

### Papel Principal
- **Ponto de entrada único** para o usuário
- **Gerencia fluxo de conversa** e delegação para agentes
- **Carrega e salva perfil do usuário** em `data/user-profile.md`
- **Aplica quiz de perfil** para coletar preferências
- **Exibe menu principal** com 6 opções (A-F)
- **Delega tarefas ao SCOUT, CURATOR e prepara o COACH**

### Fluxo de Trabalho
1. **Saudação Inicial**
   - "Olá! Sou o Maestro, seu assistente de recolocação profissional."
   - "Vou conhecer seu perfil e ajudar a direcionar sua carreira."
   - "Vamos começar?"

2. **Verificação de Perfil**
   - Verifica existência de `data/user-profile.md`
   - Se existir: pula para o Menu Principal
   - Se não existir: aplica o Quiz de Perfil

3. **Quiz de Perfil (5 Perguntas)**
   - Pergunta 1: Área principal (19 opções)
   - Pergunta 2: Nível de senioridade (3 opções)
   - Pergunta 3: Modalidade preferida (4 opções)
   - Pergunta 4: Localização preferida (texto livre)
   - Pergunta 5: Faixa salarial desejada (texto livre)
   - Pergunta 6: Competências já dominadas (texto livre, opcional)

4. **Menu Principal**
   ```
   === MENU PRINCIPAL ===
   A) Buscar vagas (SCOUT)
   B) Buscar cursos (CURATOR)
   C) Simular entrevista (COACH)
   D) Refazer quiz
   E) Ver perfil salvo
   F) Sair
   ```

5. **Delegação para Agentes Especializados**
   - **SCOUT**: Implementado na opção A e busca vagas com Firecrawl
   - **CURATOR**: Implementado na opção B e busca cursos na Alura e DIO
   - **COACH**: Implementado na opção C e realiza simulações personalizadas

## Detalhes Técnicos

### Arquivos Criados
- `data/user-profile.md`: Arquivo Markdown que armazena o perfil do usuário
- `maestro.py`: Implementação Python do agente Maestro
- `curator.py`: Implementação Python do agente CURATOR
- `coach.py`: Implementação Python do agente COACH
- `requirements.txt`: Dependências Python do projeto
- `.env.example`: Modelo de configuração da chave Firecrawl
- `.github/skills/scout/SKILL.md`: Procedimento operacional do SCOUT
- `.github/skills/curator/SKILL.md`: Procedimento operacional do CURATOR
- `.github/skills/coach/SKILL.md`: Procedimento operacional do COACH

### Estrutura de Dados do Perfil
```markdown
nome_area: [área selecionada]
senioridade: [júnior/ pleno/ sênior]
modalidade: [remoto/ híbrido/ presencial/ tanto faz]
localizacao: [localização selecionada]
faixa_salarial: [faixa salarial selecionada]
competencias_dominadas: [competências separadas por vírgula ou Nenhuma]
funcoes_alvo:
  - [função 1]
  - [função 2]
  - [função 3]
data_atualizacao: [data e hora]
```

### Funcionalidades Implementadas
- Saudação inicial
- Verificação de perfil existente
- Quiz de 5 perguntas com validação
- Persistência em Markdown
- Geração automática de funções-alvo
- Persistência das competências dominadas no perfil
- Visualização de perfil salvo
- Menu principal com 6 opções
- Refazer quiz (opção D)
- Busca de vagas integrada ao SCOUT pela opção A
- Busca de cursos integrada ao CURATOR pela opção B
- Seleção numerada de cursos com abertura dos detalhes da página
- Simulação de entrevistas integrada ao COACH pela opção C
- Avaliação de respostas e feedback estruturado

## Próximos Passos
1. Melhorar persistência com banco de dados (opcional)