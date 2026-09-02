"""Motor de comparação: lê currículos e vagas, calcula ranking e persiste resultados."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from config.settings import RESULTADOS_DIR
from models.candidato import Candidato
from models.resultado import MatchCandidato, ResultadoVaga
from models.vaga import Vaga
from services.loader import carregar_candidatos, carregar_vagas
from services.scoring import pontuar


def comparar_vaga(vaga: Vaga, candidatos: list[Candidato]) -> ResultadoVaga:
    matches: list[MatchCandidato] = []

    for candidato in candidatos:
        score, breakdown, evidencias = pontuar(candidato, vaga)
        matches.append(
            MatchCandidato(
                posicao=0,
                candidato_id=candidato.id,
                nome=candidato.nome,
                nivel=candidato.nivel.value,
                area=candidato.area.value,
                cargo_desejado=candidato.cargo_desejado,
                anos_experiencia=candidato.anos_experiencia,
                score_total=score,
                breakdown=breakdown,
                **evidencias,
            )
        )

    matches.sort(key=lambda m: m.score_total, reverse=True)
    for idx, item in enumerate(matches, start=1):
        item.posicao = idx

    return ResultadoVaga(
        vaga_id=vaga.id,
        vaga_titulo=vaga.titulo,
        vaga_area=vaga.area,
        vaga_nivel=vaga.nivel.value,
        total_candidatos=len(matches),
        ranking=matches,
    )


def salvar_resultado(resultado: ResultadoVaga, output_dir: Path, top: int | None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = resultado.model_dump()
    if top is not None:
        payload["ranking"] = payload["ranking"][:top]
        payload["top_n"] = top
    path = output_dir / f"resultado_{resultado.vaga_id.lower()}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def salvar_csv_consolidado(resultados: list[ResultadoVaga], output_dir: Path, top: int | None) -> Path:
    linhas = []
    for resultado in resultados:
        ranking = resultado.ranking[:top] if top is not None else resultado.ranking
        for item in ranking:
            linhas.append(
                {
                    "vaga_id": resultado.vaga_id,
                    "vaga_titulo": resultado.vaga_titulo,
                    "vaga_area": resultado.vaga_area,
                    "vaga_nivel": resultado.vaga_nivel,
                    "posicao": item.posicao,
                    "candidato_id": item.candidato_id,
                    "nome": item.nome,
                    "area_candidato": item.area,
                    "nivel_candidato": item.nivel,
                    "cargo_desejado": item.cargo_desejado,
                    "anos_experiencia": item.anos_experiencia,
                    "score_total": item.score_total,
                    "score_tecnologias": item.breakdown.tecnologias,
                    "score_requisitos": item.breakdown.requisitos,
                    "score_experiencia": item.breakdown.experiencia,
                    "score_area": item.breakdown.area,
                    "skills_atendidas": ", ".join(item.skills_atendidas),
                    "skills_faltantes": ", ".join(item.skills_faltantes),
                }
            )

    path = output_dir / "ranking_consolidado.csv"
    pd.DataFrame(linhas).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def executar_matching(
    top: int = 30,
    vaga_id: str | None = None,
    output_dir: Path | None = None,
    candidatos_dir: Path | None = None,
    vagas_dir: Path | None = None,
) -> dict:
    """Compara todos os currículos com as vagas e grava em data/resultados/."""
    output_dir = output_dir or RESULTADOS_DIR
    candidatos = carregar_candidatos(candidatos_dir)
    vagas = carregar_vagas(vagas_dir)

    if vaga_id:
        vagas = [v for v in vagas if v.id.upper() == vaga_id.upper()]
        if not vagas:
            raise ValueError(f"Vaga não encontrada: {vaga_id}")

    resultados = [comparar_vaga(vaga, candidatos) for vaga in vagas]
    arquivos = [str(salvar_resultado(r, output_dir, top)) for r in resultados]
    csv_path = salvar_csv_consolidado(resultados, output_dir, top)

    resumo = {
        "vagas_processadas": len(resultados),
        "candidatos": len(candidatos),
        "top_n": top,
        "arquivos": arquivos,
        "csv": str(csv_path),
        "melhores": {
            r.vaga_id: {
                "titulo": r.vaga_titulo,
                "primeiro": r.ranking[0].nome if r.ranking else None,
                "score": r.ranking[0].score_total if r.ranking else None,
            }
            for r in resultados
        },
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(resumo, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return resumo


def main() -> None:
    parser = argparse.ArgumentParser(description="Motor de comparação candidato × vaga")
    parser.add_argument("--top", type=int, default=30, help="Quantos candidatos gravar por vaga")
    parser.add_argument("--vaga", type=str, default=None, help="Filtrar por id da vaga, ex: VAG-0001")
    args = parser.parse_args()

    resumo = executar_matching(top=args.top, vaga_id=args.vaga)
    print(f"Processadas {resumo['vagas_processadas']} vagas × {resumo['candidatos']} candidatos.")
    print(f"JSONs e CSV em: {RESULTADOS_DIR}")
    for vaga_id, info in resumo["melhores"].items():
        print(f"  {vaga_id} | {info['titulo']} -> 1o {info['primeiro']} ({info['score']})")


if __name__ == "__main__":
    main()
