#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CURATOR: identifies skill gaps and searches Alura and DIO courses."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_PATH = DATA_DIR / "user-profile.md"
COURSE_RESULTS_PATH = DATA_DIR / "course-results.md"
COURSE_RESULTS_JSON_PATH = DATA_DIR / "course-results.json"
JOB_RESULT_PATHS = (
    DATA_DIR / "job-results.json",
    DATA_DIR / "scout-results.json",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(value: str) -> str:
    return " ".join(value.strip().lower().replace("/", " ").split())


def parse_profile(path: Path) -> dict:
    profile = {}
    if not path.exists():
        return profile

    current_key = None
    functions = []
    competencies = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("  - ") and current_key == "competencias_dominadas":
            competencies.append(line[4:].strip())
            continue
        if line.startswith("  - ") and current_key == "funcoes_alvo":
            functions.append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "competencias_dominadas":
                profile[key] = value
                current_key = key
                continue
            if key == "funcoes_alvo":
                current_key = key
                continue
            profile[key] = value
            current_key = None
    if functions:
        profile["funcoes_alvo"] = functions
    if competencies:
        profile["competencias_dominadas"] = ", ".join(competencies)
    return profile


def load_job_results() -> tuple[list[dict], list[str]]:
    for path in JOB_RESULT_PATHS:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return [], [f"{path}: JSON invalido ({exc.msg})"]

        jobs = payload.get("jobs", []) if isinstance(payload, dict) else payload
        if isinstance(jobs, list):
            return [job for job in jobs if isinstance(job, dict)], []
    return [], []


def extract_requirements(jobs: Iterable[dict]) -> list[str]:
    found: list[str] = []
    seen = set()
    for job in jobs:
        values = []
        requirements = job.get("requirements", [])
        if isinstance(requirements, list):
            values.extend(str(item) for item in requirements)
        elif isinstance(requirements, str):
            values.extend(part.strip() for part in requirements.replace("\n", ",").split(","))

        for key in ("description", "title"):
            value = job.get(key)
            if isinstance(value, str):
                values.append(value)

        for value in values:
            cleaned = " ".join(value.strip().split())
            key = normalize_text(cleaned)
            if cleaned and key not in seen:
                seen.add(key)
                found.append(cleaned)
    return found


def split_known_skills(raw: str) -> set[str]:
    return {
        normalize_text(item)
        for item in raw.replace(";", ",").split(",")
        if item.strip()
    }


def save_known_skills(skills: Iterable[str]) -> None:
    cleaned = []
    seen = set()
    for skill in skills:
        value = str(skill).strip()
        key = normalize_text(value)
        if value and key not in seen:
            seen.add(key)
            cleaned.append(value)

    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PROFILE_PATH.exists():
        return

    lines = PROFILE_PATH.read_text(encoding="utf-8").splitlines()
    value = ", ".join(cleaned) if cleaned else "Nenhuma"
    updated = []
    found = False
    skip_list = False
    for line in lines:
        if line.startswith("competencias_dominadas:"):
            updated.append(f"competencias_dominadas: {value}")
            found = True
            skip_list = True
            continue
        if skip_list and line.startswith("  - ") and line.strip():
            continue
        if skip_list:
            skip_list = False
        if line.strip() == "funcoes_alvo:" and not found:
            updated.append(f"competencias_dominadas: {value}")
            found = True
        updated.append(line)

    if not found:
        updated.append(f"competencias_dominadas: {value}")

    PROFILE_PATH.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def choose_gap_terms(jobs: list[dict], known_skills: set[str], limit: int) -> list[str]:
    priority_terms = (
        "docker", "kubernetes", "aws", "azure", "gcp", "java", "python",
        "javascript", "typescript", "react", "node.js", "nodejs", "sql",
        "power bi", "tableau", "git", "terraform", "ci/cd", "linux",
        "testes automatizados", "selenium", "cypress", "cybersecurity",
        "seguranca da informacao", "machine learning", "inteligencia artificial",
        "processamento de linguagem natural", "arquitetura", "api", "ingles",
    )

    corpus = []
    for job in jobs:
        requirements = job.get("requirements", [])
        if isinstance(requirements, list):
            corpus.extend(str(item) for item in requirements)
        elif isinstance(requirements, str):
            corpus.append(requirements)
        for key in ("title", "description"):
            value = job.get(key)
            if isinstance(value, str):
                corpus.append(value)

    text = normalize_text(" ".join(corpus))
    gaps = []
    for term in priority_terms:
        normalized_term = normalize_text(term)
        if normalized_term in known_skills:
            continue
        if normalized_term not in text:
            continue
        frequency = text.count(normalized_term)
        gaps.append((frequency, term))

    gaps.sort(key=lambda item: (-item[0], item[1]))
    return [term for _, term in gaps[:limit]]


def extract_search_items(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    for key in ("data", "results", "web"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = value.get("results") or value.get("web")
            if isinstance(nested, list):
                return [item for item in nested if isinstance(item, dict)]
    return []


def run_firecrawl_search(query: str, platform: str, limit: int) -> tuple[list[dict], list[str]]:
    firecrawl_executable = shutil.which("firecrawl")
    if firecrawl_executable is None:
        return [], [f"{platform}: Firecrawl CLI nao encontrado"]

    cache_dir = PROJECT_ROOT / ".firecrawl"
    cache_dir.mkdir(parents=True, exist_ok=True)
    child_env = os.environ.copy()
    child_env.pop("FIRECRAWL_API_KEY", None)
    output_path = cache_dir / f"curator-{platform}-search.json"

    command = [
        firecrawl_executable, "search", query,
        "--limit", str(limit),
        "--json",
        "-o", str(output_path),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            env=child_env,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        return [], [f"{platform}: timeout ao executar o Firecrawl"]

    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "erro desconhecido").strip()
        return [], [f"{platform}: Firecrawl falhou ({message[:300]})"]

    output_path = PROJECT_ROOT / ".firecrawl" / f"curator-{platform}-search.json"
    if not output_path.exists():
        return [], [f"{platform}: resultado JSON nao foi gravado"]
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], [f"{platform}: resposta JSON invalida ({exc.msg})"]

    domain = "alura.com.br" if platform == "alura" else "dio.me"
    items = []
    for item in extract_search_items(payload):
        url = item.get("url") or item.get("link")
        if not isinstance(url, str):
            continue
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if domain not in hostname:
            continue
        path = parsed.path.lower()
        if any(segment in path for segment in (
            "/artigos/", "/blog/", "/podcast/", "/live/",
            "/eventos/", "/certificados/",
        )):
            continue
        if platform == "dio" and not any(segment in path for segment in (
            "/curso", "/course", "/courses", "/formacao", "/bootcamp",
        )):
            continue
        if platform == "alura" and "/curso-" not in path and "/cursos-" not in path and "/formacao-" not in path:
            continue
        title = item.get("title") or item.get("name")
        description = item.get("description") or item.get("markdown") or ""
        if not isinstance(title, str) or not title.strip():
            title = "Titulo indisponivel"
        items.append({
            "title": title.strip(),
            "url": url,
            "description": str(description).strip()[:500] if description else "indisponivel",
        })
    return items[:limit], []


def deduplicate_courses(courses: list[dict]) -> list[dict]:
    unique = []
    seen = set()
    for course in courses:
        key = normalize_text(course["titulo"]) + "|" + normalize_text(course["url"])
        if key not in seen:
            seen.add(key)
            unique.append(course)
    return unique


def run_curator(
    gap_terms: list[str],
    gap_limit: int,
    course_limit: int,
    known_skills: set[str],
) -> dict:
    courses = []
    errors = []
    warnings = []

    for gap in gap_terms[:gap_limit]:
        if gap.lower() in known_skills:
            continue

        for platform in ("alura", "dio"):
            domain = "alura.com.br" if platform == "alura" else "dio.me"
            query = f'curso "{gap}" site:{domain}'
            found, failures = run_firecrawl_search(query, platform, course_limit)
            errors.extend(failures)
            for item in found:
                courses.append({
                    "lacuna": gap,
                    "prioridade_lacuna": "alta",
                    "frequencia_nas_vagas": "indisponivel",
                    "titulo": item["title"],
                    "plataforma": "Alura" if platform == "alura" else "DIO",
                    "tipo": "indisponivel",
                    "nivel": "indisponivel",
                    "carga_horaria": "indisponivel",
                    "descricao": item["description"],
                    "url": item["url"],
                    "origem_busca": "firecrawl-cli",
                    "motivo_recomendacao": f"Resultado publico relacionado a lacuna: {gap}",
                    "data_coleta": now_iso(),
                })

    courses = deduplicate_courses(courses)
    if not courses:
        warnings.append("Nenhum curso publicamente verificavel foi encontrado.")

    return {
        "generated_at": now_iso(),
        "gaps": gap_terms[:gap_limit],
        "courses": courses,
        "errors": errors,
        "warnings": warnings,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Resultados do CURATOR",
        "",
        f"data_coleta: {payload['generated_at']}",
        "",
        "## Lacunas identificadas",
        "",
    ]
    if payload["gaps"]:
        lines.extend(f"- {gap}" for gap in payload["gaps"])
    else:
        lines.append("- Nenhuma lacuna foi identificada.")

    lines.extend(["", "## Cursos encontrados", ""])
    if payload["courses"]:
        for course in payload["courses"]:
            lines.extend([
                f"### {course['titulo']}",
                f"- lacuna: {course['lacuna']}",
                f"- plataforma: {course['plataforma']}",
                f"- tipo: {course['tipo']}",
                f"- nivel: {course['nivel']}",
                f"- carga_horaria: {course['carga_horaria']}",
                f"- descricao: {course['descricao']}",
                f"- url: {course['url']}",
                f"- origem_busca: {course['origem_busca']}",
                f"- motivo_recomendacao: {course['motivo_recomendacao']}",
                f"- data_coleta: {course['data_coleta']}",
                "",
            ])
    else:
        lines.append("Nenhum curso publicamente verificavel foi encontrado.")

    if payload["errors"]:
        lines.extend(["", "## Erros", ""])
        lines.extend(f"- {error}" for error in payload["errors"])
    if payload["warnings"]:
        lines.extend(["", "## Avisos", ""])
        lines.extend(f"- {warning}" for warning in payload["warnings"])
    return "\n".join(lines).rstrip() + "\n"


def save_results(payload: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / ".gitkeep").touch(exist_ok=True)
    COURSE_RESULTS_JSON_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    COURSE_RESULTS_PATH.write_text(render_markdown(payload), encoding="utf-8")


def print_summary(payload: dict) -> None:
    print("=== CURATOR - CURSOS COMPLEMENTARES ===")
    print()
    if payload["gaps"]:
        print("Lacunas identificadas:")
        for gap in payload["gaps"]:
            print(f"- {gap}")
    else:
        print("Nenhuma lacuna identificada.")

    print()
    if payload["courses"]:
        print("Cursos encontrados:")
        for course in payload["courses"]:
            print(f"- {course['titulo']} ({course['plataforma']}): {course['url']}")
            print(f"  Lacuna: {course['lacuna']}")
    else:
        print("Nenhum curso publicamente verificavel foi encontrado.")

    for warning in payload["warnings"]:
        print(f"Aviso: {warning}")
    for error in payload["errors"]:
        print(f"Erro: {error}")

    print()
    print(f"Resultados salvos em: {COURSE_RESULTS_PATH.relative_to(PROJECT_ROOT)}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="CURATOR - busca cursos complementares")
    parser.add_argument("--known-skills", default="", help="Competencias ja dominadas separadas por virgula")
    parser.add_argument("--gap-limit", type=int, default=5)
    parser.add_argument("--course-limit", type=int, default=3)
    parser.add_argument("--gap", action="append", default=[], help="Lacuna explicita para busca")
    args = parser.parse_args()

    if not 1 <= args.gap_limit <= 10:
        print("Erro: --gap-limit deve estar entre 1 e 10.")
        return 2
    if not 1 <= args.course_limit <= 10:
        print("Erro: --course-limit deve estar entre 1 e 10.")
        return 2

    profile = parse_profile(PROFILE_PATH)
    if not profile:
        print("Erro: perfil nao encontrado. Execute o Maestro e complete o quiz.")
        return 1

    jobs, job_errors = load_job_results()
    if job_errors:
        print(f"Erro: {job_errors[0]}")
        return 1
    if not jobs and not args.gap:
        print("Nenhum resultado do SCOUT encontrado.")
        print("Execute a busca de vagas primeiro ou use --gap \"tecnologia\".")
        return 1

    known_skills = split_known_skills(args.known_skills)
    if args.known_skills:
        save_known_skills(
            item.strip() for item in args.known_skills.replace(";", ",").split(",") if item.strip()
        )
    saved_skills = profile.get("competencias_dominadas", "").strip()
    if not args.known_skills and saved_skills:
        if saved_skills.lower() not in ("nenhuma", "nenhum", "não informado", "indisponivel"):
            known_skills.update(split_known_skills(saved_skills))

    gaps = args.gap if args.gap else choose_gap_terms(jobs, known_skills, args.gap_limit)
    if not gaps:
        gaps = choose_gap_terms(jobs, known_skills, args.gap_limit)

    # Pergunta somente quando nao houver competencias salvas no perfil.
    if not args.known_skills and not saved_skills:
        print("Informe suas competencias ja dominadas separadas por virgula.")
        print("Pressione Enter para continuar sem informar competencias.")
        try:
            supplied = input("> ").strip()
        except EOFError:
            supplied = ""
        if supplied:
            save_known_skills(
                item.strip() for item in supplied.replace(";", ",").split(",") if item.strip()
            )
        known_skills.update(split_known_skills(supplied))
        gaps = args.gap if args.gap else choose_gap_terms(jobs, known_skills, args.gap_limit)

    payload = run_curator(gaps, args.gap_limit, args.course_limit, known_skills)
    save_results(payload)
    print_summary(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
