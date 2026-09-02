"""Gera e persiste pareceres de IA para os candidatos mais bem ranqueados."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from config.settings import RESULTADOS_DIR
from integrations.llm import ClienteLLM, ClienteOllama, criar_cliente_llm
from models.analise import AnaliseVaga, ParecerCandidato
from models.candidato import Candidato
from models.resultado import MatchCandidato, ResultadoVaga
from models.vaga import Vaga
from services.loader import carregar_candidatos, carregar_vagas
from services.matching import comparar_vaga


def construir_contexto(vaga: Vaga, candidato: Candidato, match: MatchCandidato) -> dict:
    """Entrega ao LLM somente dados relevantes e o resultado auditável do motor."""
    return {
        "vaga": {
            "id": vaga.id,
            "titulo": vaga.titulo,
            "nivel": vaga.nivel.value,
            "descricao": vaga.descricao,
            "requisitos_obrigatorios": vaga.requisitos_obrigatorios,
            "desejaveis": vaga.desejaveis,
            "tecnologias": vaga.tecnologias,
            "anos_minimos_experiencia": vaga.anos_minimos_experiencia,
        },
        "candidato": {
            "id": candidato.id,
            "cargo_desejado": candidato.cargo_desejado,
            "nivel": candidato.nivel.value,
            "area": candidato.area.value,
            "anos_experiencia": candidato.anos_experiencia,
            "resumo": candidato.resumo,
            "habilidades": candidato.habilidades,
            "certificacoes": candidato.certificacoes,
            "idiomas": candidato.idiomas,
            "experiencias": [e.model_dump() for e in candidato.experiencias],
        },
        "matching_auditavel": {
            "posicao": match.posicao,
            "score_total": match.score_total,
            "breakdown": match.breakdown.model_dump(),
            "skills_atendidas": match.skills_atendidas,
            "skills_faltantes": match.skills_faltantes,
            "requisitos_atendidos": match.requisitos_atendidos,
            "requisitos_pendentes": match.requisitos_pendentes,
        },
    }


def analisar_resultado(
    resultado: ResultadoVaga,
    vaga: Vaga,
    candidatos: list[Candidato],
    llm: ClienteLLM | ClienteOllama,
    top: int = 10,
) -> AnaliseVaga:
    por_id = {candidato.id: candidato for candidato in candidatos}
    analises: dict[str, ParecerCandidato] = {}
    for match in resultado.ranking[:top]:
        candidato = por_id.get(match.candidato_id)
        if candidato is None:
            continue
        analises[match.candidato_id] = llm.gerar_parecer(construir_contexto(vaga, candidato, match))
    return AnaliseVaga(
        vaga_id=vaga.id,
        vaga_titulo=vaga.titulo,
        candidatos_analisados=len(analises),
        analises=analises,
    )


def executar_analises(
    vaga_id: str | None = None,
    top: int = 10,
    output_dir: Path | None = None,
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> list[Path]:
    """Analisa o top N de cada vaga e grava arquivos independentes dos rankings."""
    output_dir = output_dir or RESULTADOS_DIR
    candidatos = carregar_candidatos()
    vagas = carregar_vagas()
    if vaga_id:
        vagas = [vaga for vaga in vagas if vaga.id.upper() == vaga_id.upper()]
        if not vagas:
            raise ValueError(f"Vaga não encontrada: {vaga_id}")

    llm = criar_cliente_llm(provider=provider, model=model, base_url=base_url)
    paths: list[Path] = []
    for vaga in vagas:
        analise = analisar_resultado(comparar_vaga(vaga, candidatos), vaga, candidatos, llm, top)
        path = output_dir / f"analise_{vaga.id.lower()}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(analise.model_dump_json(indent=2), encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera pareceres de IA para o ranking de candidatos")
    parser.add_argument("--vaga", help="Filtrar por ID da vaga, por exemplo VAG-0001")
    parser.add_argument("--top", type=int, default=10, help="Quantidade de candidatos a analisar por vaga")
    args = parser.parse_args()
    paths = executar_analises(vaga_id=args.vaga, top=args.top)
    print(f"{len(paths)} arquivo(s) de análise gerado(s) em: {RESULTADOS_DIR}")


if __name__ == "__main__":
    main()
