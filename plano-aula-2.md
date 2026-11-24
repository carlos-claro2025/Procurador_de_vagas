# Plano Aula 2 - Agente Scout

## Objetivo

Criar o agente **Scout**, responsável por descobrir vagas em sites públicos de emprego, extrair os dados relevantes e organizar os resultados em um formato consistente para as próximas etapas do projeto Procurador de Vagas.

O primeiro ciclo deve ter como fontes prioritárias **InfoJobs**, **VAGAS** e **Indeed**. O agente deve funcionar como um procedimento reutilizável, não como uma busca manual isolada.

## Base e contexto

Este plano complementa o planejamento principal da aplicação. No worktree atual, `wplano.md` não está presente; portanto, o alcance deste documento mantém o objetivo já definido pelo README: localizar vagas na internet e preparar uma estrutura clara para implementação posterior.

## Entregáveis

1. Skill do agente Scout em `.github/skills/scout/SKILL.md`.
2. Procedimento de busca com Firecrawl CLI como método principal.
3. Procedimento de fallback com as ferramentas nativas de acesso web.
4. Esquema normalizado de uma vaga.
5. Plano de validação com exemplos reais ou simulados.

## Responsabilidades do Scout

- Receber critérios de busca: cargo, palavras-chave, localidade, modalidade, senioridade e data máxima.
- Buscar vagas em fontes públicas.
- Abrir páginas de vagas relevantes.
- Extrair título, empresa, local, modalidade, descrição, requisitos, salário quando divulgado, data e link.
- Remover anúncios duplicados.
- Ignorar resultados sem página válida ou sem dados mínimos.
- Devolver um conjunto ordenado, com a fonte e o link original.
- Registrar falhas sem interromper a busca nas demais fontes.

## Estratégia de execução

### 1. Preparação

- Validar o comando `firecrawl`.
- Confirmar disponibilidade da chave ou configuração por meio de `firecrawl status`.
- Não registrar API keys ou tokens no repositório.
- Confirmar os critérios e montar uma consulta curta e específica.

### 2. Método principal: Firecrawl CLI

- Usar `firecrawl search` para descobrir páginas de vagas.
- Preferir consultas que incluam o cargo, a cidade e o nome do site.
- Restringir por localidade e período quando possível.
- Usar `--json`, `--limit` e `--scrape` somente quando necessário.
- Usar `firecrawl scrape --json --only-main-content --format markdown` para páginas já conhecidas.
- Quando uma página exigir navegação ou formulário, usar `firecrawl interact` no ciclo seguinte.

Exemplo conceitual:

```powershell
firecrawl search "vaga desenvolvedor backend São Paulo site:infojobs.com.br" --limit 10 --json
firecrawl scrape "URL_DA_VAGA" --json --only-main-content --format markdown
```

### 3. Fallback nativo

- Se o CLI não estiver instalado, não autenticar ou falhar repetidamente, usar a ferramenta nativa de busca web.
- Abrir as páginas oficiais ou os links encontrados.
- Extrair o mesmo conteúdo usando a forma disponível de acesso web.
- Indicar no resultado que a coleta foi feita pelo fallback.
- Não inventar dados ausentes nem inferir salário, modalidade ou senioridade sem evidência.

### 4. Fontes por prioridade

| Ordem | Fonte | Observação |
|---|---|---|
| 1 | InfoJobs | Buscar vagas e abrir a página pública da oportunidade |
| 2 | VAGAS | Buscar vagas e evitar depender apenas do snippet |
| 3 | Indeed | Buscar vagas e confirmar empresa, localidade e link |

As fontes podem ser ampliadas depois da validação inicial.

## Esquema normalizado

Cada vaga deve seguir esta estrutura:

```json
{
  "title": "string",
  "company": "string ou null",
  "location": "string ou null",
  "work_mode": "presencial | híbrido | remoto | não informado",
  "seniority": "string ou null",
  "salary": "string ou null",
  "description": "string",
  "requirements": ["string"],
  "posted_at": "string ou null",
  "source": "infojobs | vagas | indeed",
  "url": "https://...",
  "collected_by": "firecrawl-cli | native-web",
  "collected_at": "ISO 8601"
}
```

## Tratamento de falhas

- Timeout: registrar a URL e tentar uma única vez com parâmetros menores.
- Falha de autenticação: ativar o fallback nativo.
- Página dinâmica: usar scraping com mais tempo de espera ou `interact` no ciclo seguinte.
- Página bloqueada: não contornar restrições; registrar como bloqueada e seguir.
- Dados ambíguos: preservar `null` ou informar `não identificado`.
- Fonte indisponível: continuar a busca nas demais fontes.

## Fluxo do agente

1. Receber critérios.
2. Normalizar os termos de busca.
3. Testar o Firecrawl CLI.
4. Executar a descoberta em cada fonte.
5. Scrape das páginas confirmadas.
6. Extrair e normalizar os dados.
7. Remover duplicatas por URL normalizada e por combinação título + empresa + local.
8. Validar campos obrigatórios.
9. Devolver os resultados e os erros.

## Critérios de aceite

- Gera pelo menos uma busca válida para cada fonte planejada.
- Produz vagas normalizadas sem perder o link original.
- Não duplica a mesma vaga por URL ou pelo conjunto título, empresa e local.
- Usa o fallback quando o Firecrawl CLI falha.
- Distingue informação explícita de inferência ou ausência.
- Não coloca credenciais em arquivos ou resultados.
- Continua a execução quando uma fonte falha.

## Sequência de implementação

1. Criar o arquivo da skill Scout.
2. Documentar os comandos e o esquema normalizado.
3. Fazer um teste controlado com uma consulta por fonte.
4. Executar a busca real e revisar a qualidade dos dados.
5. Ajustar consultas, normalização e regras de duplicidade.
6. Registrar erros e limites por site.
7. Integrar o Scout ao fluxo do Procurador de Vagas somente após os critérios de aceite serem atendidos.

