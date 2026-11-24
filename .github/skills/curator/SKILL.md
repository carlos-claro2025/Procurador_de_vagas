---
name: curator
description: Identifica lacunas entre o perfil e os requisitos das vagas, busca cursos verificados na Alura e DIO com Firecrawl CLI e salva resultados normalizados.
---

# Skill CURATOR

Use esta skill para complementar as habilidades do usuario com cursos encontrados em catalogos publicos.

## Objetivo

Ler o perfil em `data/user-profile.md`, analisar os resultados do SCOUT em `data/job-results.json` ou `data/scout-results.json`, identificar lacunas e localizar cursos publicos na Alura e na DIO.

## Metodo principal

Use o Firecrawl CLI:

```powershell
firecrawl search "curso Docker site:alura.com.br" --limit 3 --json -o .firecrawl/curator-alura-search.json
firecrawl search "curso Docker site:dio.me" --limit 3 --json -o .firecrawl/curator-dio-search.json
```

Valide todos os resultados:

- A URL deve pertencer ao dominio confirmado da plataforma.
- O resultado deve apontar para curso, trilha ou formacao.
- O titulo deve representar uma correspondencia real com a lacuna.
- Nao considere artigos, lives, desafios ou paginas promocionais como cursos sem confirmacao.
- Nao invente carga horaria, nivel, descricao ou certificado.

Use `firecrawl scrape "<url>" --json --only-main-content --format markdown -o .firecrawl/arquivo.md` para confirmar uma pagina individual quando a pesquisa tiver titulo, mas faltar dados suficientes.

## Fallback

Ative o fallback somente quando o Firecrawl CLI estiver ausente, autenticacao estiver bloqueada, houver timeout persistente ou a pagina nao puder ser validada.

O fallback usa a ferramenta nativa de acesso web e deve respeitar as mesmas regras de dominio, validacao e formato.

Registre `native-web` na origem e informe qualquer falha em `errors`. Nao contorne CAPTCHA, paywall ou restricoes.

## Fluxo

1. Verifique `data/user-profile.md`.
2. Verifique os resultados normalizados do SCOUT.
3. Reuna e normalize requisitos das vagas.
4. Leia `competencias_dominadas` do perfil. Solicite somente quando o campo estiver ausente.
5. Remova competencias conhecidas e priorize lacunas frequentes.
6. Consulte Alura e DIO para cada lacuna.
7. Remova duplicatas por titulo e URL.
8. Salve `data/course-results.json` e `data/course-results.md`.
9. Informe lacunas nao encontradas e erros separadamente.

## Entradas aceitas do SCOUT

Formato principal:

```json
{
  "jobs": [
    {
      "title": "string",
      "requirements": ["string"],
      "description": "string",
      "url": "https://..."
    }
  ]
}
```

## Campos normalizados

```json
{
  "lacuna": "string",
  "prioridade_lacuna": "alta | media | baixa",
  "frequencia_nas_vagas": "string",
  "titulo": "string",
  "plataforma": "Alura | DIO",
  "tipo": "string",
  "nivel": "string",
  "carga_horaria": "string",
  "descricao": "string",
  "url": "https://...",
  "origem_busca": "firecrawl-cli | native-web",
  "motivo_recomendacao": "string",
  "data_coleta": "ISO 8601"
}
```

Campos nao confirmados devem usar `indisponivel`.

## Regras

- Nunca inventar cursos, URLs, cargas horarias ou niveis.
- Nunca apresentar como curso um resultado que nao aponta para uma pagina verificada.
- Nunca sobrescrever o perfil ou os resultados do SCOUT.
- Respeitar limites de tempo e quantidade de consultas.
- Registrar toda falha de origem, etapa e mensagem.
- Preservar cursos encontrados por uma plataforma quando a outra falhar.
