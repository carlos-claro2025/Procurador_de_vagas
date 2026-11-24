#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maestro - Orquestrador de Recolocação Profissional
Fase 1: Saudação, verificação de perfil, quiz, persistência e menu principal.
"""

import os
import subprocess
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PROFILE_PATH = os.path.join(DATA_DIR, "user-profile.md")

AREAS = [
    "Desenvolvimento Backend",
    "Desenvolvimento Frontend",
    "Ciência de Dados",
    "Engenharia de Dados",
    "Business Intelligence",
    "Inteligência Artificial",
    "Mobile",
    "DevOps",
    "Full Stack",
    "Governança de Dados",
    "Design UX",
    "Design UI",
    "QA/Testes",
    "Marketing Digital",
    "Marketing de Mídias Sociais",
    "Growth Marketing",
    "Gestão de Produtos",
    "Cibersegurança",
    "Outro",
]

SENIORIDADES = ["Júnior", "Pleno", "Sênior"]

MODALIDADES = ["Remoto", "Híbrido", "Presencial", "Tanto faz"]


def carregar_env():
    env_path = Path(PROJECT_ROOT) / ".env"
    if not env_path.exists():
        return
    with open(env_path, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip("\"'"))


def executar_coach():
    print("Executando COACH...")
    try:
        resultado = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, "coach.py")],
            cwd=PROJECT_ROOT,
            timeout=900,
        )
        if resultado.returncode != 0:
            print("O COACH encerrou com um erro.")
    except subprocess.TimeoutExpired:
        print("A simulacao excedeu o tempo limite.")
    except OSError as exc:
        print(f"Nao foi possivel iniciar o COACH: {exc}")
    print()


def exibir_detalhes_curso(curso):
    titulo = curso.get("titulo") or "Titulo indisponivel"
    url = curso.get("url")
    if not url:
        print("Erro: este curso nao possui uma URL valida.")
        print()
        return

    executable = shutil.which("firecrawl")
    if executable is None:
        print("Erro: Firecrawl CLI nao encontrado.")
        print()
        return

    cache_dir = os.path.join(PROJECT_ROOT, ".firecrawl")
    os.makedirs(cache_dir, exist_ok=True)
    output_path = os.path.join(cache_dir, "course-detail.md")
    child_env = os.environ.copy()
    child_env.pop("FIRECRAWL_API_KEY", None)

    print(f"CURATOR - abrindo o curso: {titulo}")
    print(f"Plataforma: {curso.get('plataforma', 'indisponivel')}")
    print(f"URL: {url}")
    print()
    try:
        resultado = subprocess.run(
            [
                executable,
                "scrape",
                url,
                "--json",
                "--only-main-content",
                "--format",
                "markdown",
                "-o",
                output_path,
            ],
            cwd=PROJECT_ROOT,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("Erro: o tempo limite foi excedido ao abrir os detalhes do curso.")
        print()
        return

    if resultado.returncode != 0:
        mensagem = (resultado.stderr or resultado.stdout or "erro desconhecido").strip()
        print(f"Erro ao abrir os detalhes do curso: {mensagem[:500]}")
        print()
        return

    try:
        with open(output_path, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()
    except OSError as exc:
        print(f"Erro ao ler os detalhes do curso: {exc}")
        print()
        return

    if conteudo.startswith("{"):
        try:
            payload = json.loads(conteudo)
            if isinstance(payload, dict):
                data = payload.get("data")
                nested_markdown = data.get("markdown") if isinstance(data, dict) else None
                conteudo = (
                    payload.get("markdown")
                    or payload.get("content")
                    or nested_markdown
                    or conteudo
                )
        except json.JSONDecodeError:
            pass

    if not conteudo:
        print("Nao foi possivel obter o conteudo detalhado deste curso.")
        print()
        return

    limite = 12000
    trecho = " ".join(conteudo.split())
    if len(trecho) > limite:
        trecho = trecho[:limite].rstrip() + "..."

    print("=== DETALHES DO CURSO ===")
    print(texto_seguro_para_console(trecho))
    print()


def executar_curator():
    print("Executando CURATOR...")
    try:
        resultado = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, "curator.py")],
            cwd=PROJECT_ROOT,
            timeout=300,
        )
        if resultado.returncode != 0:
            print("O CURATOR encerrou com um erro.")
            print()
            return
    except subprocess.TimeoutExpired:
        print("A busca do CURATOR excedeu o tempo limite.")
        print()
        return
    except OSError as exc:
        print(f"Nao foi possivel iniciar o CURATOR: {exc}")
        print()
        return

    resultado_path = os.path.join(DATA_DIR, "course-results.json")
    if not os.path.exists(resultado_path):
        print("Nenhum resultado de curso foi salvo.")
        print()
        return

    try:
        with open(resultado_path, "r", encoding="utf-8") as arquivo:
            payload = json.load(arquivo)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Erro ao ler os resultados do CURATOR: {exc}")
        print()
        return

    cursos = payload.get("courses", []) if isinstance(payload, dict) else []
    if not cursos:
        print("Nenhum curso encontrado para selecionar.")
        print()
        return

    print("=== CURSOS ENCONTRADOS ===")
    for indice, curso in enumerate(cursos, 1):
        print(f"{indice}. {curso.get('titulo', 'Titulo indisponivel')} "
              f"- {curso.get('plataforma', 'Plataforma indisponivel')}")
        print(f"   Lacuna: {curso.get('lacuna', 'indisponivel')}")
        print(f"   URL: {curso.get('url', 'indisponivel')}")
    print()
    print("Digite o numero do curso para ver os detalhes.")
    print("Digite V para voltar ao menu.")
    while True:
        escolha = input("Curso selecionado: ").strip().upper()
        if escolha == "V":
            print()
            return
        try:
            indice = int(escolha)
            if 1 <= indice <= len(cursos):
                exibir_detalhes_curso(cursos[indice - 1])
                print("Digite o numero de outro curso ou V para voltar ao menu.")
                continue
        except ValueError:
            pass
        print("Opcao invalida. Escolha um numero da lista ou V.")

FUNCOES_ALVO = {
    "Desenvolvimento Backend": {
        "Júnior": [
            "Desenvolvedor Backend Júnior",
            "Desenvolvedor Java Júnior",
            "Desenvolvedor Node.js Júnior",
        ],
        "Pleno": [
            "Desenvolvedor Backend",
            "Engenheiro de Software",
            "Desenvolvedor API",
        ],
        "Sênior": [
            "Engenheiro Backend Sênior",
            "Arquiteto de Software",
            "Líder Técnico Backend",
        ],
    },
    "Desenvolvimento Frontend": {
        "Júnior": [
            "Desenvolvedor Frontend Júnior",
            "Desenvolvedor React Júnior",
            "Desenvolvedor Web Júnior",
        ],
        "Pleno": [
            "Desenvolvedor Frontend",
            "Desenvolvedor React",
            "Engenheiro Frontend",
        ],
        "Sênior": [
            "Engenheiro Frontend Sênior",
            "Tech Lead Frontend",
            "Arquiteto Frontend",
        ],
    },
    "Ciência de Dados": {
        "Júnior": [
            "Cientista de Dados Júnior",
            "Analista de Dados Júnior",
            "Assistente de Dados",
        ],
        "Pleno": [
            "Cientista de Dados",
            "Analista Avançado de Dados",
            "Especialista em Analytics",
        ],
        "Sênior": [
            "Cientista de Dados Sênior",
            "Líder de Dados",
            "Head de Data Science",
        ],
    },
    "Engenharia de Dados": {
        "Júnior": [
            "Engenheiro de Dados Júnior",
            "Analista ETL",
            "Desenvolvedor Data Pipeline",
        ],
        "Pleno": [
            "Engenheiro de Dados",
            "Data Engineer",
            "Especialista em Integração de Dados",
        ],
        "Sênior": [
            "Engenheiro de Dados Sênior",
            "Arquiteto de Dados",
            "Líder de Engenharia de Dados",
        ],
    },
    "Business Intelligence": {
        "Júnior": [
            "Analista BI Júnior",
            "Analista de Relatórios",
            "Assistente BI",
        ],
        "Pleno": [
            "Analista BI",
            "Especialista Power BI",
            "Consultor BI",
        ],
        "Sênior": [
            "Especialista BI Sênior",
            "Arquiteto BI",
            "Head de Analytics",
        ],
    },
    "Inteligência Artificial": {
        "Júnior": [
            "Analista de IA Júnior",
            "Desenvolvedor IA Júnior",
            "Assistente de Machine Learning",
        ],
        "Pleno": [
            "Engenheiro de Machine Learning",
            "Especialista em IA",
            "Engenheiro LLM",
        ],
        "Sênior": [
            "Engenheiro de IA Sênior",
            "Arquiteto de IA",
            "Head de Inteligência Artificial",
        ],
    },
    "Mobile": {
        "Júnior": [
            "Desenvolvedor Mobile Júnior",
            "Desenvolvedor Android Júnior",
            "Desenvolvedor iOS Júnior",
        ],
        "Pleno": [
            "Desenvolvedor iOS",
            "Desenvolvedor Android",
            "Desenvolvedor React Native",
        ],
        "Sênior": [
            "Engenheiro Mobile Sênior",
            "Arquiteto Mobile",
            "Líder Flutter",
        ],
    },
    "DevOps": {
        "Júnior": [
            "Engenheiro DevOps Júnior",
            "Suporte Cloud",
            "SysAdmin",
        ],
        "Pleno": [
            "Engenheiro DevOps",
            "Engenheiro Cloud",
            "SRE",
        ],
        "Sênior": [
            "Engenheiro DevOps Sênior",
            "Arquiteto Cloud",
            "Líder de Plataforma",
        ],
    },
    "Full Stack": {
        "Júnior": [
            "Desenvolvedor Full Stack",
            "Desenvolvedor Web Júnior",
        ],
        "Pleno": [
            "Engenheiro Full Stack",
            "Desenvolvedor de Aplicações Web",
        ],
        "Sênior": [
            "Engenheiro Full Stack Sênior",
            "Líder Técnico",
            "Arquiteto de Soluções",
        ],
    },
    "Governança de Dados": {
        "Júnior": [
            "Analista de Governança de Dados Júnior",
            "Gestor de Dados Júnior",
            "Assistente de Compliance",
        ],
        "Pleno": [
            "Analista de Governança de Dados",
            "DPO",
            "Analista de Qualidade de Dados",
        ],
        "Sênior": [
            "Head de Governança de Dados",
            "Chief Data Officer",
            "Líder de Arquitetura de Dados",
        ],
    },
    "Design UX": {
        "Júnior": [
            "Designer UX Júnior",
            "Assistente UI/UX",
            "Pesquisador UX Jr",
        ],
        "Pleno": [
            "Designer UX",
            "Pesquisador UX",
            "Designer de Produto",
        ],
        "Sênior": [
            "Designer UX Sênior",
            "Líder UX",
            "Head de UX",
        ],
    },
    "Design UI": {
        "Júnior": [
            "Designer UI Júnior",
            "Designer Visual Jr",
            "Assistente de Design System",
        ],
        "Pleno": [
            "Designer UI",
            "Product Designer",
            "Especialista em Design System",
        ],
        "Sênior": [
            "Designer UI Sênior",
            "Head de Design Visual",
            "Líder de Produto Digital",
        ],
    },
    "QA/Testes": {
        "Júnior": [
            "Analista QA Júnior",
            "Testador de Software",
            "Assistente de Qualidade",
        ],
        "Pleno": [
            "Analista QA",
            "Engenheiro de Testes",
            "Especialista em Automação",
        ],
        "Sênior": [
            "QA Lead",
            "Arquiteto de Qualidade",
            "Head de QA",
        ],
    },
    "Marketing Digital": {
        "Júnior": [
            "Assistente de Marketing Digital",
            "Analista Jr de Marketing",
            "Assistente de Performance",
        ],
        "Pleno": [
            "Analista de Marketing Digital",
            "Especialista em Performance",
            "Especialista SEO",
        ],
        "Sênior": [
            "Head de Marketing Digital",
            "Diretor de Marketing",
            "Líder de Aquisição",
        ],
    },
    "Marketing de Mídias Sociais": {
        "Júnior": [
            "Assistente de Mídias Sociais",
            "Criador de Conteúdo Jr",
            "Community Manager Jr",
        ],
        "Pleno": [
            "Gerente de Mídias Sociais",
            "Estrategista de Conteúdo",
            "Analista de Marketing Digital",
        ],
        "Sênior": [
            "Head de Mídias Sociais",
            "Diretor de Mídias Sociais",
            "Líder Estrategista de Marca",
        ],
    },
    "Growth Marketing": {
        "Júnior": [
            "Assistente de Growth Marketing",
            "Analista de Marketing Jr",
            "Marketing de Performance Jr",
        ],
        "Pleno": [
            "Growth Marketer",
            "Gerente de Marketing de Performance",
            "Especialista CRO",
        ],
        "Sênior": [
            "Head de Growth",
            "Diretor de Growth",
            "VP de Marketing",
        ],
    },
    "Gestão de Produtos": {
        "Júnior": [
            "Analista de Produto",
            "Product Owner Jr",
            "Gerente de Produto Associado",
        ],
        "Pleno": [
            "Product Owner",
            "Gerente de Produto",
            "Gerente de Produto Técnico",
        ],
        "Sênior": [
            "Head de Produto",
            "Gerente de Produto Sênior",
            "VP de Produto",
        ],
    },
    "Cibersegurança": {
        "Júnior": [
            "Analista de Segurança Júnior",
            "Analista SOC",
            "Assistente de Segurança da Informação",
        ],
        "Pleno": [
            "Engenheiro de Segurança",
            "Pentester",
            "Consultor de Segurança",
        ],
        "Sênior": [
            "Engenheiro de Segurança Sênior",
            "CISO",
            "Líder Arquiteto de Segurança",
        ],
    },
    "Outro": {
        "Júnior": ["Estagiário", "Assistente", "Trainee"],
        "Pleno": ["Analista", "Especialista"],
        "Sênior": ["Sênior", "Líder", "Coordenador"],
    },
}


def garantir_diretorio_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def perfil_existe():
    return os.path.exists(PROFILE_PATH)


def carregar_perfil():
    if not perfil_existe():
        return None
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def salvar_perfil(perfil):
    garantir_diretorio_data()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        f.write(perfil)


def saudacao():
    print("Olá! Sou o Maestro, seu assistente de recolocação profissional.")
    print("Vou conhecer seu perfil e ajudar a direcionar sua carreira.")
    print("Vamos começar?")
    print()


def fazer_pergunta(texto, opcoes=None):
    print(texto)
    if opcoes:
        for i, opcao in enumerate(opcoes, 1):
            print(f"{i}) {opcao}")
    while True:
        resposta = input("> ").strip()
        if opcoes:
            try:
                indice = int(resposta) - 1
                if 0 <= indice < len(opcoes):
                    return opcoes[indice]
            except ValueError:
                pass
            print("Opção inválida. Tente novamente.")
        else:
            if resposta:
                return resposta
            print("Resposta não pode estar vazia. Tente novamente.")


def aplicar_quiz():
    print("=== QUIZ DE PERFIL ===")
    print("Responda as perguntas abaixo para montar seu perfil.")
    print()

    area = fazer_pergunta("Pergunta 1 - Qual é sua área principal?", AREAS)
    print()
    senioridade = fazer_pergunta("Pergunta 2 - Qual seu nível atual?", SENIORIDADES)
    print()
    modalidade = fazer_pergunta("Pergunta 3 - Qual sua modalidade preferida?", MODALIDADES)
    print()
    localizacao = fazer_pergunta("Pergunta 4 - Qual sua localização preferida?")
    print()
    faixa_salarial = fazer_pergunta("Pergunta 5 - Qual sua faixa salarial desejada?")
    print()

    competencias_existentes = []
    perfil_atual = carregar_perfil()
    if perfil_atual:
        dentro_competencias = False
        for linha in perfil_atual.splitlines():
            if linha.strip() == "competencias_dominadas:":
                dentro_competencias = True
            elif dentro_competencias and linha.startswith("  - "):
                competencias_existentes.append(linha[4:].strip())
            elif dentro_competencias:
                break
            elif linha.startswith("competencias_dominadas:"):
                valor = linha.split(":", 1)[1].strip()
                if valor:
                    competencias_existentes.extend(
                        item.strip() for item in valor.split(",") if item.strip()
                    )

    texto_competencias = ", ".join(competencias_existentes)
    if texto_competencias:
        print("Pergunta 6 - Quais competencias voce ja domina?")
        print(f"Atual: {texto_competencias}")
        print("Separe por virgula ou pressione Enter para manter.")
        resposta_competencias = input("> ").strip()
        competencias = resposta_competencias if resposta_competencias else texto_competencias
    else:
        print("Pergunta 6 - Quais competencias voce ja domina?")
        print("Separe por virgula ou pressione Enter para nenhuma.")
        competencias = input("> ").strip()
    print()

    funcoes = FUNCOES_ALVO.get(area, {}).get(senioridade, [])
    data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    perfil = (
        f"nome_area: {area}\n"
        f"senioridade: {senioridade}\n"
        f"modalidade: {modalidade}\n"
        f"localizacao: {localizacao}\n"
        f"faixa_salarial: {faixa_salarial}\n"
        f"competencias_dominadas: {competencias.strip() if competencias.strip().lower() not in ('', 'nenhuma') else 'Nenhuma'}\n"
        f"funcoes_alvo:\n"
    )
    for funcao in funcoes:
        perfil += f"  - {funcao}\n"
    perfil += f"data_atualizacao: {data_atualizacao}\n"

    salvar_perfil(perfil)
    print("Perfil salvo com sucesso!")
    print()
    return perfil


def gerar_funcoes_alvo(area, senioridade):
    return FUNCOES_ALVO.get(area, {}).get(senioridade, [])


def exibir_perfil(perfil_texto):
    print("=== SEU PERFIL SALVO ===")
    print(perfil_texto)
    print()


def exibir_menu_principal():
    print("=== MENU PRINCIPAL ===")
    print("A) Buscar vagas (SCOUT)")
    print("B) Buscar cursos (CURATOR)")
    print("C) Simular entrevista (COACH)")
    print("D) Refazer quiz")
    print("E) Ver perfil salvo")
    print("F) Sair")
    print()


def ler_funcoes_alvo(perfil_texto):
    funcoes = []
    dentro_da_lista = False
    for linha in perfil_texto.splitlines():
        if linha.strip() == "funcoes_alvo:":
            dentro_da_lista = True
        elif dentro_da_lista and linha.startswith("  - "):
            funcoes.append(linha[4:].strip())
        elif dentro_da_lista:
            break
    return funcoes


def montar_query_vagas(perfil_texto):
    dados = {}
    for linha in perfil_texto.splitlines():
        if ":" in linha and not linha.startswith("  - "):
            chave, valor = linha.split(":", 1)
            dados[chave.strip()] = valor.strip()

    funcoes = ler_funcoes_alvo(perfil_texto)
    cargos = " OR ".join(funcoes[:3])
    modalidade = dados.get("modalidade", "")
    localizacao = dados.get("localizacao", "")

    partes = [
        f"vagas emprego Brasil ({cargos})",
        f"modalidade {modalidade}" if modalidade and modalidade != "Tanto faz" else "",
        localizacao if localizacao else "",
    ]
    return " ".join(parte for parte in partes if parte)


def texto_seguro_para_console(texto):
    if texto is None:
        return ""
    return str(texto)


def vaga_para_dicionario(vaga, indice=None):
    if isinstance(vaga, dict):
        item = vaga
        titulo = item.get("title") or item.get("titulo") or "Titulo nao informado"
        url = item.get("url") or "URL nao informada"
        descricao = item.get("description") or item.get("descricao") or ""
    else:
        titulo = getattr(vaga, "title", None) or "Titulo nao informado"
        url = getattr(vaga, "url", None) or "URL nao informada"
        descricao = (
            getattr(vaga, "description", None)
            or getattr(vaga, "markdown", None)
            or ""
        )
        item = {
            "title": titulo,
            "company": getattr(vaga, "company", None),
            "location": getattr(vaga, "location", None),
            "work_mode": getattr(vaga, "work_mode", None),
            "seniority": getattr(vaga, "seniority", None),
            "salary": getattr(vaga, "salary", None),
            "requirements": getattr(vaga, "requirements", []) or [],
            "posted_at": getattr(vaga, "posted_at", None),
            "source": getattr(vaga, "source", None),
            "collected_by": getattr(vaga, "collected_by", None),
            "collected_at": getattr(vaga, "collected_at", None),
            "url": url,
        }

    descricao = " ".join(str(descricao).split())
    if len(descricao) > 500:
        descricao = descricao[:497].rstrip() + "..."

    result = {"title": titulo, "description": descricao, "url": url}
    for key in (
        "company", "location", "work_mode", "seniority", "salary",
        "requirements", "posted_at", "source", "collected_by", "collected_at",
    ):
        result[key] = item.get(key) if isinstance(item, dict) else None
    if indice is not None:
        result = {"numero": indice, **result}
    return result


def exibir_resultado_vagas(vagas):
    print("=== RESULTADO SCOUT (JSON) ===")
    formato_json = {
        "total": len(vagas),
        "jobs": [
            vaga_para_dicionario(vaga, indice)
            for indice, vaga in enumerate(vagas, 1)
        ],
    }
    print(json.dumps(formato_json, ensure_ascii=False, indent=2))
    print()


def exibir_detalhes_vaga(client, vaga):
    titulo = getattr(vaga, "title", None) or "Título não informado"
    url = getattr(vaga, "url", None)

    if not url or url == "URL não informada":
        print("Erro: esta vaga não possui uma URL válida.")
        print()
        return

    print(f"SCOUT - abrindo a vaga: {titulo}")
    print(f"URL: {url}")
    print()

    try:
        documento = client.scrape(
            url,
            formats=["markdown"],
            only_main_content=True,
            max_age=0,
            timeout=300000,
        )
    except Exception as exc:
        print(f"Erro ao abrir os detalhes da vaga: {exc}")
        print()
        return

    conteudo = getattr(documento, "markdown", None)
    if not conteudo:
        print("Não foi possível obter o conteúdo detalhado desta vaga.")
        print()
        return

    linhas = " ".join(conteudo.split()).split()
    trecho = " ".join(linhas)
    limite = 12000
    if len(trecho) > limite:
        trecho = trecho[:limite].rstrip() + "..."

    print("=== DETALHES DA VAGA ===")
    print(texto_seguro_para_console(trecho))
    print()


def exibir_detalhes_vaga_por_cli(vaga):
    titulo = vaga.get("title") or "Titulo nao informado"
    url = vaga.get("url")
    if not url:
        print("Erro: esta vaga nao possui uma URL valida.")
        print()
        return

    executable = shutil.which("firecrawl")
    if executable is None:
        print("Erro: Firecrawl CLI nao encontrado.")
        print()
        return

    cache_dir = os.path.join(PROJECT_ROOT, ".firecrawl")
    os.makedirs(cache_dir, exist_ok=True)
    output_path = os.path.join(cache_dir, "job-detail.md")
    child_env = os.environ.copy()
    child_env.pop("FIRECRAWL_API_KEY", None)

    print(f"SCOUT - abrindo a vaga: {titulo}")
    print(f"URL: {url}")
    print()
    try:
        resultado = subprocess.run(
            [
                executable,
                "scrape",
                url,
                "--json",
                "--only-main-content",
                "--format",
                "markdown",
                "-o",
                output_path,
            ],
            cwd=PROJECT_ROOT,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("Erro: o tempo limite foi excedido ao abrir os detalhes da vaga.")
        print()
        return

    if resultado.returncode != 0:
        mensagem = (resultado.stderr or resultado.stdout or "erro desconhecido").strip()
        print(f"Erro ao abrir os detalhes da vaga: {mensagem[:500]}")
        print()
        return

    try:
        with open(output_path, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()
    except OSError as exc:
        print(f"Erro ao ler os detalhes da vaga: {exc}")
        print()
        return

    if conteudo.startswith("{"):
        try:
            payload = json.loads(conteudo)
            if isinstance(payload, dict):
                data = payload.get("data")
                nested_markdown = data.get("markdown") if isinstance(data, dict) else None
                conteudo = (
                    payload.get("markdown")
                    or payload.get("content")
                    or nested_markdown
                    or conteudo
                )
        except json.JSONDecodeError:
            pass

    if not conteudo:
        print("Nao foi possivel obter o conteudo detalhado desta vaga.")
        print()
        return

    limite = 12000
    trecho = " ".join(conteudo.split())
    if len(trecho) > limite:
        trecho = trecho[:limite].rstrip() + "..."

    print("=== DETALHES DA VAGA ===")
    print(texto_seguro_para_console(trecho))
    print()


def buscar_vagas_por_cli(perfil_texto):
    executable = shutil.which("firecrawl")
    if executable is None:
        print("Erro: Firecrawl CLI nao encontrado.")
        print("Instale com: npm install -g firecrawl-cli@latest")
        print()
        return

    query = montar_query_vagas(perfil_texto)
    child_env = os.environ.copy()
    child_env.pop("FIRECRAWL_API_KEY", None)
    cache_dir = os.path.join(PROJECT_ROOT, ".firecrawl")
    os.makedirs(cache_dir, exist_ok=True)
    output_path = os.path.join(cache_dir, "scout-results.json")

    print(f"SCOUT - buscando vagas pelo CLI: {query}")
    print()
    try:
        resultado = subprocess.run(
            [
                executable,
                "search",
                query,
                "--limit",
                "10",
                "--json",
                "-o",
                output_path,
            ],
            cwd=PROJECT_ROOT,
            env=child_env,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("Erro: a busca pelo Firecrawl CLI excedeu o tempo limite.")
        print()
        return

    if resultado.returncode != 0:
        mensagem = (resultado.stderr or resultado.stdout or "erro desconhecido").strip()
        print(f"Erro no Firecrawl CLI: {mensagem[:500]}")
        print()
        return

    if not os.path.exists(output_path):
        print("Erro: o Firecrawl CLI nao gravou o resultado da busca.")
        print()
        return

    try:
        payload = json.loads(open(output_path, "r", encoding="utf-8").read())
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Erro ao ler o resultado do SCOUT: {exc}")
        print()
        return

    web_items = payload.get("data", {}).get("web", []) if isinstance(payload, dict) else []
    if not isinstance(web_items, list):
        web_items = []

    vagas = []
    for item in web_items:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        if not isinstance(url, str) or not url:
            continue
        vagas.append({
            "title": item.get("title") or "Titulo nao informado",
            "company": None,
            "location": None,
            "work_mode": "nao informado",
            "seniority": None,
            "salary": None,
            "description": item.get("description") or item.get("markdown") or "",
            "requirements": [],
            "posted_at": None,
            "source": "native-web",
            "url": url,
            "collected_by": "firecrawl-cli",
            "collected_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    if not vagas:
        print("Nenhuma vaga foi encontrada pelo Firecrawl CLI.")
        print()
        return

    garantir_diretorio_data()
    job_output = os.path.join(DATA_DIR, "job-results.json")
    with open(job_output, "w", encoding="utf-8") as arquivo:
        json.dump({"jobs": vagas}, arquivo, ensure_ascii=False, indent=2)

    exibir_resultado_vagas(vagas)

    print(f"Resultados normalizados salvos em: data/job-results.json")
    print()
    print("Digite o numero da vaga para ver os detalhes.")
    print("Digite V para voltar ao menu.")
    while True:
        escolha = input("Vaga selecionada: ").strip().upper()
        if escolha == "V":
            print()
            return
        try:
            indice = int(escolha)
            if 1 <= indice <= len(vagas):
                exibir_detalhes_vaga_por_cli(vagas[indice - 1])
                print("Digite o numero de outra vaga ou V para voltar ao menu.")
                continue
        except ValueError:
            pass
        print("Opcao invalida. Escolha um numero da lista ou V.")


def buscar_vagas(perfil_texto):
    carregar_env()
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        return buscar_vagas_por_cli(perfil_texto)

    try:
        from firecrawl import Firecrawl
    except ImportError as exc:
        print(f"Erro ao carregar o SDK do Firecrawl: {exc}")
        print("Execute: python -m pip install -r requirements.txt")
        print()
        return

    query = montar_query_vagas(perfil_texto)
    print(f"SCOUT - buscando vagas para: {query}")
    print()

    try:
        client = Firecrawl(api_key=api_key)
        resultado = client.search(
            query,
            sources=["web"],
            limit=10,
            location="Goiânia, Brazil",
            timeout=300000,
        )
    except Exception as exc:
        mensagem = str(exc)
        if "unauthorized" in mensagem.lower() or "invalid token" in mensagem.lower():
            print("Token do SDK inválido. Usando o Firecrawl CLI autenticado.")
            print()
            return buscar_vagas_por_cli(perfil_texto)
        print(f"Erro na busca do Firecrawl: {mensagem}")
        print()
        return

    vagas = resultado.web or []
    if not vagas:
        print("Nenhuma vaga foi encontrada.")
        print()
        return

    garantir_diretorio_data()
    job_output = os.path.join(DATA_DIR, "job-results.json")
    vagas_normalizadas = [
        vaga_para_dicionario(vaga)
        for vaga in vagas
    ]
    with open(job_output, "w", encoding="utf-8") as arquivo:
        json.dump({"jobs": vagas_normalizadas}, arquivo, ensure_ascii=False, indent=2)
    exibir_resultado_vagas(vagas)
    print("Resultados normalizados salvos em: data/job-results.json")
    print()

    print("Digite o número da vaga para ver os detalhes.")
    print("Digite V para voltar ao menu.")
    while True:
        escolha = input("Vaga selecionada: ").strip().upper()
        if escolha == "V":
            print()
            return
        try:
            indice = int(escolha)
            if 1 <= indice <= len(vagas):
                exibir_detalhes_vaga(client, vagas[indice - 1])
                print("Digite o número de outra vaga ou V para voltar ao menu.")
                continue
        except ValueError:
            pass
        print("Opção inválida. Escolha 1 a 10 ou V.")


def main():
    saudacao()

    if not perfil_existe():
        aplicar_quiz()
    else:
        print("Perfil existente encontrado. Pulando quiz.")
        print()

    perfil = carregar_perfil()
    exibir_perfil(perfil)

    while True:
        exibir_menu_principal()
        opcao = input("Escolha uma opção: ").strip().upper()
        print()

        if opcao == "A":
            buscar_vagas(perfil)
        elif opcao == "B":
            executar_curator()
        elif opcao == "C":
            executar_coach()
        elif opcao == "D":
            aplicar_quiz()
            perfil = carregar_perfil()
            exibir_perfil(perfil)
        elif opcao == "E":
            exibir_perfil(perfil)
        elif opcao == "F":
            print("Obrigado por usar o Maestro. Até a próxima!")
            break
        else:
            print("Opção inválida. Tente novamente.")
            print()


if __name__ == "__main__":
    main()