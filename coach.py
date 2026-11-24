#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""COACH: simulador de entrevistas baseado no perfil do usuario."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_PATH = DATA_DIR / "user-profile.md"
RESULT_JSON = DATA_DIR / "interview-results.json"
RESULT_MD = DATA_DIR / "interview-results.md"


def parse_profile() -> dict:
    profile = {}
    if not PROFILE_PATH.exists():
        return profile

    functions = []
    in_functions = False
    for line in PROFILE_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and in_functions:
            functions.append(stripped[2:].strip())
            continue
        if stripped == "funcoes_alvo:":
            in_functions = True
            continue
        if in_functions:
            in_functions = False
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            profile[key.strip()] = value.strip()
            continue

        if line.startswith("  - ") and "funcoes_alvo" in profile:
            functions.append(line[4:].strip())
            continue
    if functions:
        profile["funcoes_alvo"] = functions
    return profile


def build_questions(profile: dict) -> list[dict]:
    area = profile.get("nome_area", "area escolhida")
    seniority = profile.get("senioridade", "nivel escolhido")
    role = profile.get("funcoes_alvo", "a vaga desejada")
    if isinstance(role, list):
        role = role[0] if role else "a vaga desejada"

    return [
        {
            "tipo": "apresentacao",
            "pergunta": "Fale sobre voce, sua trajetoria profissional e o que motivou sua candidatura.",
        },
        {
            "tipo": "vaga",
            "pergunta": f"Por que voce deseja atuar como {role}, na area de {area}?",
        },
        {
            "tipo": "experiencia",
            "pergunta": "Conte sobre uma situacao profissional ou academica em que voce precisou resolver um problema importante. Qual foi seu papel?",
        },
        {
            "tipo": "competencia",
            "pergunta": f"Para uma posicao {seniority.lower()}, quais competencias voce considera essenciais em {area}? De um exemplo pratico.",
        },
        {
            "tipo": "resultado",
            "pergunta": "Descreva uma entrega ou conquista da qual se orgulha. Como mediu o resultado?",
        },
        {
            "tipo": "comportamental",
            "pergunta": "Como voce reage quando recebe uma critica ou precisa trabalhar com uma equipe em desacordo?",
        },
        {
            "tipo": "problema",
            "pergunta": "Imagine que uma entrega esteja atrasada e o stakeholder esteja pressionando. Como voce priorizaria e comunicaria a situacao?",
        },
        {
            "tipo": "encerramento",
            "pergunta": "Por que o recrutador deveria escolher voce e quais pontos gostaria de esclarecer sobre a vaga?",
        },
    ]


def evaluate_answer(answer: str) -> dict:
    text = answer.lower()
    length = len(answer.strip())
    markers = {
        "situacao": sum(word in text for word in ("situacao", "contexto", "desafio", "quando")),
        "acao": sum(word in text for word in ("eu", "fiz", "implementei", "liderei", "resolvi")),
        "resultado": sum(word in text for word in ("resultado", "consegui", "reduziu", "melhorou", "alcancei", "percent")),
        "comunicacao": sum(word in text for word in ("comuniquei", "conversai", "stakeholder", "equipe")),
    }

    strengths = []
    improvements = []
    score = 0

    if length >= 180:
        strengths.append("Resposta detalhada")
        score += 2
    elif length >= 70:
        strengths.append("Resposta objetiva")
        score += 1
    else:
        improvements.append("Desenvolva melhor o contexto e a explicacao")

    if markers["situacao"]:
        strengths.append("Apresentou contexto")
        score += 1
    else:
        improvements.append("Explique a situacao ou o desafio")

    if markers["acao"]:
        strengths.append("Destacou sua responsabilidade")
        score += 2
    else:
        improvements.append("Use verbos de acao e explique o que voce fez")

    if markers["resultado"]:
        strengths.append("Indicou impacto ou resultado")
        score += 2
    else:
        improvements.append("Inclua um resultado mensuravel, quando possivel")

    if markers["comunicacao"]:
        strengths.append("Mostrou comunicacao")
        score += 1

    score = min(10, score)
    return {
        "nota": score,
        "pontos_fortes": strengths,
        "melhorias": improvements,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Simulacao de Entrevista - COACH",
        "",
        f"data: {payload['generated_at']}",
        f"area: {payload['profile'].get('nome_area', 'indisponivel')}",
        f"senioridade: {payload['profile'].get('senioridade', 'indisponivel')}",
        f"vaga: {payload['profile'].get('cargo_contexto', 'indisponivel')}",
        "",
    ]
    for answer in payload["answers"]:
        lines.extend([
            f"## {answer['numero']}. {answer['pergunta']}",
            f"- Tipo: {answer['tipo']}",
            f"- Resposta: {answer['resposta']}",
            f"- Nota: {answer['avaliacao']['nota']}/10",
        ])
        for strength in answer["avaliacao"]["pontos_fortes"]:
            lines.append(f"- Ponto forte: {strength}")
        for improvement in answer["avaliacao"]["melhorias"]:
            lines.append(f"- Melhorar: {improvement}")
        lines.append("")

    lines.extend([
        "## Resumo",
        f"- Nota geral: {payload['nota_geral']}/10",
        f"- Respostas: {payload['total_respostas']}",
        f"- Ponto forte mais observado: {payload['resumo'].get('ponto_forte', 'indisponivel')}",
        f"- Prioridade de melhoria: {payload['resumo'].get('melhoria', 'indisponivel')}",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    profile = parse_profile()
    if not profile:
        print("COACH: perfil nao encontrado. Execute o quiz do Maestro primeiro.")
        return 1

    roles = profile.get("funcoes_alvo")
    if isinstance(roles, list) and roles:
        role = roles[0]
    elif isinstance(roles, str):
        role = roles
    else:
        role = "a vaga desejada"
    profile["cargo_contexto"] = role

    questions = build_questions(profile)
    print("=== COACH - SIMULACAO DE ENTREVISTA ===")
    print("Responda naturalmente. Digite FIM para encerrar a simulacao.")
    print()

    answers = []
    for index, question in enumerate(questions, 1):
        print(f"{index}. {question['pergunta']}")
        try:
            answer = input("> ").strip()
        except EOFError:
            answer = ""
        if answer.upper() == "FIM":
            break
        if not answer:
            answer = "Sem resposta nesta etapa."

        evaluation = evaluate_answer(answer)
        answers.append({
            "numero": index,
            "tipo": question["tipo"],
            "pergunta": question["pergunta"],
            "resposta": answer,
            "avaliacao": evaluation,
        })
        print(f"Feedback: {evaluation['nota']}/10")
        for improvement in evaluation["melhorias"]:
            print(f"- Melhorar: {improvement}")
        print()

    if not answers:
        print("Nenhuma resposta registrada.")
        return 0

    scores = [answer["avaliacao"]["nota"] for answer in answers]
    general_score = round(sum(scores) / len(scores), 1)

    strength_counts = {}
    improvement_counts = {}
    for answer in answers:
        evaluation = answer["avaliacao"]
        for strength in evaluation["pontos_fortes"]:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        for improvement in evaluation["melhorias"]:
            improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1

    top_strength = max(strength_counts, key=strength_counts.get) if strength_counts else "indisponivel"
    top_improvement = (
        max(improvement_counts, key=improvement_counts.get)
        if improvement_counts
        else "indisponivel"
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "profile": profile,
        "answers": answers,
        "total_respostas": len(answers),
        "nota_geral": general_score,
        "resumo": {
            "ponto_forte": top_strength,
            "melhoria": top_improvement,
        },
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    RESULT_MD.write_text(render_markdown(payload), encoding="utf-8")

    print("=== RESULTADO DA ENTREVISTA ===")
    print(f"Nota geral: {general_score}/10")
    print(f"Ponto forte mais observado: {top_strength}")
    print(f"Prioridade de melhoria: {top_improvement}")
    print(f"Resultados salvos em: {RESULT_JSON.relative_to(PROJECT_ROOT)}")
    print(f"Resumo salvo em: {RESULT_MD.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
