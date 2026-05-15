"""
Crew de análise energética — baseado em crewAI.py.example (Agent, Task, Crew, Process + Groq).
"""

from __future__ import annotations

import json
import re
from typing import Any

from crewai import Agent, Crew, Process, Task

from IA.config import IASettings, configure_groq_env


def _parse_crew_output(raw: str) -> dict[str, Any]:
    text = str(raw).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {
        "analysis": text,
        "report": text,
        "savings_suggestions": [],
        "waste_detection": [],
    }


def _normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [line.strip("-• ").strip() for line in value.splitlines() if line.strip()]
    return [str(value)]


def run_energy_insights(context: str, settings: IASettings | None = None) -> dict[str, Any]:
    cfg = configure_groq_env(settings)

    analyst = Agent(
        role="Analista de Eficiência Energética — Campus IoT",
        goal=(
            "Produzir análise objetiva e acionável do consumo de iluminação do campus, "
            "com foco em salas, horários e desperdício fora do funcionamento informado."
        ),
        backstory=(
            "Você analisa exclusivamente os dados do sistema Campus IoT. "
            "Respostas curtas, técnicas, em português do Brasil, sem texto genérico."
        ),
        verbose=cfg.verbose,
        allow_delegation=False,
        llm=cfg.groq_model,
    )

    insight_task = Task(
        description=(
            "Com base APENAS nos dados do Campus IoT abaixo, responda em JSON válido (sem markdown) com:\n"
            '- "analysis": string curta (máx. 8 linhas) citando: (1) salas com MAIOR consumo em kWh/R$; '
            "(2) faixas de horário com menor e maior consumo; (3) tendência do período.\n"
            '- "report": string objetiva (máx. 12 linhas) para gestão, só fatos do sistema.\n'
            '- "savings_suggestions": array de até 6 strings — ações concretas ligadas aos dados.\n'
            '- "waste_detection": array de até 6 strings — desperdício (ex.: lâmpadas ligadas fora do '
            "horário de funcionamento do campus, salas com consumo alto sem uso esperado).\n\n"
            "Regras: cite nomes de salas e valores kWh/R$ quando existirem; compare com o contexto "
            "operacional se fornecido; não invente dados ausentes; seja direto.\n\n"
            f"DADOS:\n{context}"
        ),
        expected_output='JSON com "analysis", "report", "savings_suggestions", "waste_detection".',
        agent=analyst,
    )

    crew = Crew(
        agents=[analyst],
        tasks=[insight_task],
        process=Process.sequential,
        verbose=cfg.verbose,
    )

    result = crew.kickoff()
    parsed = _parse_crew_output(str(result))

    return {
        "analysis": str(parsed.get("analysis", "")),
        "report": str(parsed.get("report", "")),
        "savings_suggestions": _normalize_list(parsed.get("savings_suggestions")),
        "waste_detection": _normalize_list(parsed.get("waste_detection")),
        "model": cfg.groq_model,
    }
