---
name: scout
description: Procura vagas públicas em InfoJobs, VAGAS e Indeed, usa o Firecrawl CLI como método principal e ferramentas nativas de acesso web como fallback.
---

# Skill Scout

Use esta skill quando o usuário pedir para buscar vagas na internet ou quando outro agente precisar descobrir vagas com critérios de cargo, localidade, modalidade ou senioridade.

## Objetivo

Localizar vagas em sites públicos de emprego, validar que as oportunidades existem e devolver dados normalizados com a URL original.

Prioridade de fontes:

1. InfoJobs
2. VAGAS
3. Indeed

## Procedimento obrigatório

### 1. Interpretar os critérios

Obtenha ou derive:

- cargo ou palavras-chave;
- localidade;
- modalidade, quando informada;
- senioridade, quando informada;
- limite de tempo ou data de publicação;
- número máximo de vagas.

Nunca altere uma exigência de forma silenciosa. Se estiver usando uma alternativa ampla, indique isso no resultado.
Normalize os critérios antes da busca e mantenha a data máxima como filtro explícito. Se cargo, localidade ou limite de resultados não puder ser determinado, peça os dados que faltam antes de consultar as fontes.

### 2. Executar o Firecrawl CLI

Verifique o CLI:

```powershell
firecrawl status
```

Use o comando de busca para descobrir resultados:

```powershell
firecrawl search "cargo localidade site:infojobs.com.br" --limit 10 --json
```

Repita com o domínio da fonte correspondente:

```powershell
firecrawl search "cargo localidade site:vagas.com.br" --limit 10 --json
firecrawl search "cargo localidade site:indeed.com.br" --limit 10 --json
```

Para uma vaga já localizada, extraia o conteúdo principal:

```powershell
firecrawl scrape "URL_DA_VAGA" --json --only-main-content --format markdown
```

Use `--wait-for` para páginas dinâmicas quando houver indicação de que o conteúdo demora a aparecer. Use `--actions` ou `firecrawl interact` apenas em ciclos posteriores quando o conteúdo exigir navegação, seleção ou preenchimento.

Não execute ações que violem termos do site, restrições de acesso ou autenticações. Não contorne bloqueios, CAPTCHA ou paywalls.
Execute pelo menos uma consulta para cada fonte prioritária, mesmo que uma fonte anterior falhe. Restrinja cada consulta ao domínio da fonte e use `--limit` para respeitar o limite solicitado. Use `--scrape` na descoberta apenas quando isso reduzir uma etapa sem ocultar a URL original.

### 3. Detectar falha do Firecrawl

Considere fallback quando ocorrer uma destas condições:

- comando não encontrado;
- falha de autenticação;
- timeout repetido;
- erro de rede persistente;
- página inválida ou bloqueada pelo provedor;
- resultado vazio em uma fonte que não pode ser confirmado por scraping.

Em caso de timeout, registre a URL e tente uma única vez com parâmetros menores. Em caso de autenticação inválida ou comando indisponível, não tente corrigir credenciais automaticamente.
O fallback não é aplicado apenas porque o primeiro resultado foi imperfeito. É aplicado quando o método primário não consegue concluir a coleta.

### 4. Usar o acesso web nativo como fallback

Se o Firecrawl CLI falhar:

1. Use a ferramenta nativa de busca web para localizar páginas relevantes.
2. Abra os resultados oficiais ou links diretos disponíveis.
3. Extraia apenas dados presentes na página.
4. Preserve a URL original.
5. Registre `collected_by: "native-web"`.

Não use o fallback para repetir indefinidamente uma consulta já concluída pelo Firecrawl.

Se uma ferramenta nativa também falhar, registre o erro exato no resultado e continue nas demais fontes. Se nenhuma ferramenta conseguir confirmar a página, descarte o resultado em vez de transformá-lo em uma vaga.

## Extração

Cada vaga deve conter:

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

Regras:

- `description` não pode ser preenchida com texto promocional não relacionado à vaga.
- `salary` só pode ser preenchido quando divulgado ou calculado explicitamente pelo site.
- `work_mode` só é inferida remotamente se a própria página usar esse sentido.
- Campos não confirmados são `null` ou `não informado`.
- Nunca invente nome de empresa, localidade, senioridade ou data.
- `source` deve corresponder ao domínio realmente confirmado.
- `url` deve ser o link original da oportunidade, não o link de uma página de resultados.
- `collected_at` deve ser uma data e hora ISO 8601 gerada no momento da coleta.

## Deduplicação

Remova duplicatas usando:

1. URL normalizada, removendo parâmetros de rastreamento;
2. combinação normalizada de título + empresa + localidade;
3. identificador da vaga quando disponível.

Não remova duas vagas apenas por terem o mesmo título; preserve empresas, localidades ou IDs diferentes.
Ao normalizar URLs, preserve protocolo, domínio, caminho e parâmetros funcionais. Considere equivalentes apenas parâmetros de rastreamento conhecidos, como `utm_*`, `ref` e `source`.

## Resposta

Retorne:

- resumo breve da consulta;
- lista das vagas normalizadas;
- método usado em cada vaga;
- fontes que falharam;
- avisos sobre dados ausentes ou limitações.

Se nenhuma vaga puder ser confirmada, informe isso claramente e não transforme snippets ou resultados de busca em vagas sem abrir a página.
Inclua as falhas em uma coleção `errors`, com `source`, `stage`, `message` e `url` quando houver. Uma falha em uma fonte não deve apagar vagas confirmadas por outras fontes.

Formato mínimo da resposta:

```json
{
  "query": {
    "role": "string",
    "location": "string ou null",
    "work_mode": "string ou null",
    "seniority": "string ou null",
    "max_posted_at": "string ou null",
    "limit": "number"
  },
  "jobs": [],
  "errors": [
    {
      "source": "infojobs | vagas | indeed",
      "stage": "status | search | scrape | fallback",
      "message": "erro exato",
      "url": "https://... ou null"
    }
  ],
  "warnings": ["string"]
}
```

## Validação mínima

- Executar pelo menos uma busca em cada fonte prioritária.
- Confirmar que o link abre ou que o resultado é válido.
- Validar os campos obrigatórios.
- Testar o fallback desativando deliberadamente o uso do Firecrawl CLI ou simulando uma falha.
- Confirmar que nenhuma chave ou segredo foi incluído no texto ou nos arquivos.

Teste controlado sugerido:

1. Use uma consulta curta, como `desenvolvedor backend São Paulo`, com limite pequeno.
2. Execute uma busca separada para `infojobs.com.br`, `vagas.com.br` e `indeed.com.br`.
3. Para cada resultado, abra a página antes de incluir a vaga.
4. Simule a indisponibilidade do Firecrawl e confirme `collected_by: "native-web"` ou um erro explícito.
5. Verifique que duas URLs com parâmetros de rastreamento produzem uma única vaga quando todo o restante for equivalente.
