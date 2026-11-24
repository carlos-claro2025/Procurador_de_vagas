#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maestro - Orquestrador de Recolocação Profissional
Fase 1: Saudação, verificação de perfil, quiz, persistência e menu principal.
"""

import os
import sys
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

    funcoes = FUNCOES_ALVO.get(area, {}).get(senioridade, [])
    data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    perfil = (
        f"nome_area: {area}\n"
        f"senioridade: {senioridade}\n"
        f"modalidade: {modalidade}\n"
        f"localizacao: {localizacao}\n"
        f"faixa_salarial: {faixa_salarial}\n"
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


def buscar_vagas(perfil_texto):
    carregar_env()
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Erro: FIRECRAWL_API_KEY não encontrada.")
        print("Configure o projeto com: firecrawl env")
        print()
        return

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
        print(f"Erro na busca do Firecrawl: {exc}")
        print()
        return

    vagas = resultado.web or []
    if not vagas:
        print("Nenhuma vaga foi encontrada.")
        print()
        return

    for indice, vaga in enumerate(vagas, 1):
        titulo = getattr(vaga, "title", None) or "Título não informado"
        url = getattr(vaga, "url", None) or "URL não informada"
        descricao = (
            getattr(vaga, "description", None)
            or getattr(vaga, "markdown", None)
            or ""
        )
        descricao = " ".join(descricao.split())
        if len(descricao) > 220:
            descricao = descricao[:217] + "..."

        print(texto_seguro_para_console(f"{indice}. {titulo}"))
        print(texto_seguro_para_console(f"URL: {url}"))
        if descricao:
            print(texto_seguro_para_console(f"Resumo: {descricao}"))
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
            print("Buscar cursos (CURATOR) - funcionalidade reservada para fase futura.")
            print()
        elif opcao == "C":
            print("Simular entrevista (COACH) - funcionalidade reservada para fase futura.")
            print()
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