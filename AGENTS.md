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
- **Prepara terreno** para agentes futuros (SCOUT, CURATOR, COACH)

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

5. **Delegação para Agentes Futuros**
   - **SCOUT**: Busca vagas de tecnologia (futuro)
   - **CURATOR**: Busca cursos e trilhas de aprendizado (futuro)
   - **COACH**: Simulações de entrevista e avaliação profissional (futuro)

## Detalhes Técnicos

### Arquivos Criados
- `data/user-profile.md`: Arquivo Markdown que armazena o perfil do usuário
- `maestro.py`: Implementação Python do agente Maestro

### Estrutura de Dados do Perfil
```markdown
nome_area: [área selecionada]
senioridade: [júnior/ pleno/ sênior]
modalidade: [remoto/ híbrido/ presencial/ tanto faz]
localizacao: [localização selecionada]
faixa_salarial: [faixa salarial selecionada]
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
- Visualização de perfil salvo
- Menu principal com 6 opções
- Refazer quiz (opção D)
- Preparação para integração dos agentes SCOUT, CURATOR e COACH

## Próximos Passos (Fases Futuras)
1. **Implementar o agente SCOUT** para buscar vagas de tecnologia
2. **Implementar o agente CURATOR** para buscar cursos e trilhas de aprendizado
3. **Implementar o agente COACH** para simulações de entrevista
4. **Adicionar funcionalidades de busca** nas opções A-C
5. **Melhorar persistência** com banco de dados (opcional)