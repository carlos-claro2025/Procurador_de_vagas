# Plano da Aula 3 - Agente CURATOR

## Objetivo

Planejar a terceira fase do projeto **Procurador de Vagas**: criar o agente **CURATOR**, responsável por localizar cursos que ajudem o usuário a completar as habilidades exigidas nas vagas encontradas pelo agente **SCOUT**.

Este documento continua a implementação já planejada em `plano.md` e `plano-aula-2.md`.

## Ponto de partida

As fases anteriores já estabelecem:

- `maestro.py` como ponto de interação do usuário.
- `AGENTS.md` como especificação operacional do orquestrador.
- Perfil persistido do usuário, com área, senioridade, modalidade, localização e faixa salarial.
- Lista de funções-alvo derivada do perfil.
- Agente **SCOUT**, planejado para buscar vagas em portais como InfoJobs, VAGAS e Indeed.
- Uma skill reutilizável em `.github/skills/scout/SKILL.md`.
- O menu principal do Maestro com a opção **B) Buscar cursos (CURATOR)** reservada para esta fase.

O CURATOR não deve substituir o SCOUT nem criar vagas fictícias. Ele deve consumir o resultado normalizado de vagas já encontrado e indicar cursos que realmente existam nas plataformas consultadas.

## Agente CURATOR

O CURATOR é um agente especializado em:

1. Ler o perfil do usuário.
2. Ler as vagas encontradas pelo SCOUT.
3. Identificar competências repetidas ou relevantes nessas vagas.
4. Separar competências já presentes no perfil das habilidades faltantes.
5. Buscar cursos públicos correspondentes na Alura e na DIO.
6. Normalizar os resultados em uma lista comparável.
7. Entregar cursos e justificativas ao Maestro sem inventar informações.

## Entradas

### Perfil do usuário

O CURATOR deve reutilizar o perfil persistido pelo Maestro, por exemplo:

```markdown
nome_area: Desenvolvimento Backend
senioridade: Pleno
modalidade: Remoto
localizacao: São Paulo - SP
faixa_salarial: 8k a 12k CLT
funcoes_alvo:
  - Desenvolvedor Backend
  - Engenheiro de Software
  - Desenvolvedor API
```

### Resultado do SCOUT

O CURATOR deve aceitar o esquema normalizado produzido pelo SCOUT:

```text
titulo
empresa
local
modalidade
senioridade
descricao
requisitos
url
fonte
data_coleta
```

O conjunto esperado de requisitos inclui tecnologias, metodologias, certificações e competências comportamentais úteis para o usuário.

## Sequência de análise

O CURATOR deve seguir esta ordem:

1. Reunir os requisitos das vagas relevantes.
2. Normalizar termos equivalentes.
   - Exemplo: `JavaScript`, `JS` e `Javascript` representam a mesma competência.
   - Exemplo: `AWS` e `Amazon Web Services` devem ser associados.
3. Contar a frequência de cada habilidade nas vagas analisadas.
4. Comparar as habilidades encontradas com o perfil e as informações disponíveis sobre conhecimentos do usuário.
5. Definir uma prioridade:
   - alta: habilidade exigida em várias vagas ou em vaga diretamente alinhada ao perfil;
   - média: habilidade complementar comum no mercado;
   - baixa: habilidade específica ou pouco repetida.
6. Gerar termos de busca por habilidade faltante.
7. Consultar a Alura e a DIO.
8. Validar título, descrição, plataforma e URL de cada curso.
9. Remover duplicados e cursos sem página pública verificável.
10. Ordenar os cursos pela prioridade da lacuna e pela qualidade da correspondência.

## Navegação na Alura

O fluxo principal deve utilizar o **Firecrawl CLI**, seguindo o padrão já definido na skill do Scout.

O CURATOR deve navegar no catálogo de cursos da Alura em `https://www.alura.com.br/` e localizar resultados relacionados às lacunas do usuário.

O procedimento deve incluir:

1. Buscar cada termo prioritário no catálogo da Alura.
2. Extrair da página título, descrição curta, categoria, carga horária quando disponível e URL.
3. Confirmar que a URL pertence ao domínio da Alura.
4. Consultar uma página individual quando o resultado da busca não tiver dados suficientes.
5. Descartar anúncios, landing pages sem curso ou links genéricos.
6. Registrar o motivo quando não houver correspondência confiável.

Exemplo de termos derivados de vagas:

- Docker
- AWS
- Kubernetes
- Inglês para tecnologia
- Power BI
- Testes automatizados
- Arquitetura de APIs
- Segurança da informação

Os termos reais devem ser derivados das vagas, não definidos por uma lista fixa.

## Navegação na DIO

A plataforma oficial utilizada será a **DIO**, em `https://www.dio.me/`.

O CURATOR deve executar no catálogo da DIO o mesmo padrão de busca, validação e normalização usado na Alura:

1. Buscar o termo da lacuna no catálogo ou na pesquisa da DIO.
2. Extrair título, plataforma, descrição ou resumo disponível, nível, carga horária e URL.
3. Confirmar que o link leva a uma página de curso ou formação da DIO.
4. Diferenciar curso, bootcamp e formação no campo `tipo`.
5. Não confundir certificados, artigos, lives ou desafios com cursos.
6. Registrar quando o conteúdo estiver apenas em página promocional ou exigir acesso adicional.

Se o nome público correto da plataforma impedir a resolução de um curso, o CURATOR deve deixar o campo indisponível em vez de inventar.

## Integração do Firecrawl

Criar a skill:

```text
.github/skills/curator/SKILL.md
```

A skill deve conter:

- Quando ativar o CURATOR.
- Entradas esperadas do perfil e do SCOUT.
- Procedimento principal com Firecrawl CLI.
- Regras de navegação da Alura.
- Regras de navegação da DIO.
- Fallback para ferramenta nativa de acesso web.
- Fluxo de extração e validação das páginas.
- Limitações de dados, bloqueios e páginas dinâmicas.
- Esquema de saída.
- Regras para não inventar cursos ou atribuir cobertura incorreta.

O Firecrawl continua sendo o método preferencial. Caso a CLI não esteja disponível ou falhe, o fallback deve usar a ferramenta nativa de acesso web sem deixar de registrar a origem e o método utilizado.

## Fallback nativo

O fallback deve ser usado apenas quando:

- o Firecrawl CLI não estiver instalado;
- o comando falhar;
- o catálogo estiver bloqueado pelo Firecrawl;
- o resultado estiver incompleto ou não puder ser validado.

O fallback deve seguir o mesmo esquema de saída e as mesmas verificações. O agente deve informar no relatório que a coleta foi feita por acesso web nativo.

## Esquema de saída

Cada resultado deve seguir este formato normalizado:

```text
lacuna
prioridade_lacuna
frequencia_nas_vagas
titulo
plataforma
tipo
nivel
carga_horaria
descricao
url
origem_busca
motivo_recomendacao
data_coleta
```

Campos não verificáveis devem ser registrados como `indisponível`, não como texto presumido.

## Agrupamento recomendado

O resultado final deve ser apresentado ao usuário por prioridade:

1. **Cursos prioritários**: habilidades exigidas em várias vagas ou diretamente ligadas às funções-alvo.
2. **Cursos complementares**: boas correspondências para aumentar a competitividade.
3. **Cursos opcionais**: habilidades específicas de poucas vagas ou interesse complementar.
4. **Não encontrados**: lacunas para as quais não foi possível obter um curso verificável.

Cada curso deve informar por que foi recomendado, por exemplo:

- aparece em três das cinco vagas consultadas;
- cobre diretamente a lacuna identificada;
- possui título correspondente à tecnologia exigida;
- oferece nível compatível com a senioridade do usuário.

## Persistência

O CURATOR deve criar ou atualizar os dados em um arquivo previsível, por exemplo:

```text
data/course-results.md
```

Opcionalmente, os dados brutos podem ser armazenados em uma pasta separada:

```text
data/courses/<coleta>/
```

A implementação não deve sobrescrever o perfil do usuário nem os resultados do SCOUT.

## Integração com o Maestro

Ao finalizar a fase de implementação, a opção **B) Buscar cursos (CURATOR)** deve deixar de ser reservada.

O fluxo esperado é:

1. O usuário escolhe a opção B no menu.
2. O Maestro delega a tarefa ao CURATOR.
3. O CURATOR confirma que existe perfil.
4. O CURATOR verifica se existem resultados recentes do SCOUT.
5. Se não existirem vagas:
   - orienta o usuário a executar primeiro a opção A;
   - ou solicita uma busca curta de vagas antes da curadoria.
6. O CURATOR apresenta as lacunas e os cursos encontrados.
7. O Maestro oferece a opção de repetir a busca ou voltar ao menu principal.

O Maestro deve manter o menu geral e não conter a lógica de scraping.

## Arquivos previstos

Fase de planejamento já concluída:

- `plano-aula-3.md`

Arquivos a serem criados ou alterados na implementação:

- `.github/skills/curator/SKILL.md`
- `AGENTS.md`
- `maestro.py`
- `data/course-results.md` ou estrutura equivalente

Arquivos anteriores devem ser preservados:

- `plano.md`
- `plano-aula-2.md`
- `.github/skills/scout/SKILL.md`
- `maestro.py`
- `AGENTS.md`

## Segurança e confiabilidade

- Não armazenar credenciais em arquivos do projeto.
- Não reutilizar cookies ou sessões pessoais de forma persistente.
- Não acessar páginas privadas além do necessário para a consulta pública.
- Respeitar bloqueios, CAPTCHA e limites das plataformas.
- Nunca afirmar que um curso existe sem confirmar a página.
- Nunca atribuir carga horária, nível ou descrição sem evidência.
- Registrar erros com fonte, URL consultada e método utilizado.
- Não deixar o programa falhar silenciosamente.
- Fazer timeout e limite de tentativas em todas as consultas.

## Critérios de aceitação

1. Existe uma skill funcional em `.github/skills/curator/SKILL.md`.
2. O CURATOR usa o perfil persistido pelo Maestro.
3. O CURATOR usa os requisitos das vagas produzidas pelo SCOUT.
4. O CURATOR identifica lacunas por frequência e relevância.
5. O agente navega em `alura.com.br` usando Firecrawl CLI como método principal.
6. O agente navega em `dio.me` usando Firecrawl CLI como método principal.
7. Existe fallback documentado para acesso web nativo.
8. Os cursos são validados individualmente antes de serem apresentados.
9. Duplicados são removidos.
10. Dados não confirmados aparecem como `indisponível`.
11. O Maestro conecta a opção B ao CURATOR.
12. O usuário recebe cursos separados por prioridade.
13. Cada curso possui justificativa baseada nas vagas analisadas.
14. A busca registra claramente origem, data e método de coleta.
15. Uma busca sem resultados explicita que nenhuma correspondência foi encontrada.
