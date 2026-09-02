"""Gerador de currículos sintéticos para candidatos."""

import json
import random
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd

from config.settings import CANDIDATOS_DIR
from generators.datasets import (
    AREA_CONFIG,
    CIDADES,
    EMPRESAS,
    IDIOMAS_OPCOES,
    INSTITUICOES,
    NIVEL_ANOS,
    NIVEL_QTD_EXP,
    NIVEL_QTD_HAB,
    NOMES,
    RESUMOS,
    SOBRENOMES,
)
from models.candidato import (
    AreaAtuacao,
    Candidato,
    Experiencia,
    Formacao,
    NivelExperiencia,
)

AREAS = list(AreaAtuacao)
NIVEIS = list(NivelExperiencia)
TOTAL_PADRAO = 300


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_text.lower())


def _gerar_nome_unico(usados: set[str], rng: random.Random) -> str:
    while True:
        if rng.random() < 0.6:
            nome = rng.choice(NOMES)
        else:
            primeiro = rng.choice(NOMES).split()[0]
            sobrenome = rng.choice(SOBRENOMES)
            nome = f"{primeiro} {sobrenome}"
        if nome not in usados:
            usados.add(nome)
            return nome


def _gerar_email(nome: str, idx: int) -> str:
    base = _slugify(nome.split()[0])
    sobrenome = _slugify(nome.split()[-1]) if len(nome.split()) > 1 else "candidato"
    return f"{base}.{sobrenome}{idx:03d}@email.com"


def _gerar_telefone(rng: random.Random) -> str:
    ddd = rng.choice(["11", "21", "31", "41", "51", "61", "71", "81", "85", "48"])
    prefixo = rng.randint(90000, 99999)
    sufixo = rng.randint(1000, 9999)
    return f"({ddd}) 9{prefixo}-{sufixo}"


def _gerar_formacao(area: str, nivel: str, rng: random.Random) -> list[Formacao]:
    config = AREA_CONFIG[area]
    curso = rng.choice(config["cursos"])
    instituicao = rng.choice(INSTITUICOES)
    ano_base = {"junior": 2022, "pleno": 2016, "senior": 2010}[nivel]
    ano = rng.randint(ano_base - 2, ano_base + 2)

    formacoes = [
        Formacao(
            instituicao=instituicao,
            curso=curso,
            nivel="Graduação",
            ano_conclusao=ano,
            status="concluido",
        )
    ]

    if nivel in ("pleno", "senior") and rng.random() < 0.45:
        formacoes.append(
            Formacao(
                instituicao=rng.choice(INSTITUICOES),
                curso=rng.choice(["MBA em Gestão", "Especialização", "Pós-graduação"]),
                nivel="Pós-graduação",
                ano_conclusao=ano + rng.randint(3, 8),
                status="concluido",
            )
        )

    return formacoes


def _gerar_experiencias(
    area: str, nivel: str, anos: int, rng: random.Random
) -> list[Experiencia]:
    config = AREA_CONFIG[area]
    qtd_min, qtd_max = NIVEL_QTD_EXP[nivel]
    qtd = rng.randint(qtd_min, qtd_max)
    experiencias: list[Experiencia] = []
    ano_atual = datetime.now().year
    ano_fim = ano_atual - rng.randint(0, 1)

    for i in range(qtd):
        duracao = max(1, anos // qtd + rng.randint(-1, 1))
        inicio_ano = ano_fim - duracao
        cargo = rng.choice(config["cargos"][nivel])
        if i > 0 and nivel != "junior":
            cargo = rng.choice(config["cargos"][nivel if i < qtd - 1 else nivel])

        experiencias.append(
            Experiencia(
                empresa=rng.choice(EMPRESAS),
                cargo=cargo,
                inicio=f"{rng.randint(1, 12):02d}/{inicio_ano}",
                fim=f"{rng.randint(1, 12):02d}/{ano_fim}" if i == 0 else f"{rng.randint(1, 12):02d}/{ano_fim}",
                descricao=rng.choice([
                    "Atuação em projetos multidisciplinares com foco em resultados.",
                    "Responsável por melhorias de processo e entregas contínuas.",
                    "Participação ativa em iniciativas estratégicas da área.",
                    "Interface com stakeholders e acompanhamento de indicadores.",
                ]),
            )
        )
        ano_fim = inicio_ano - rng.randint(0, 1)

    return list(reversed(experiencias))


def _gerar_habilidades(area: str, nivel: str, rng: random.Random) -> list[str]:
    config = AREA_CONFIG[area]
    qtd_min, qtd_max = NIVEL_QTD_HAB[nivel]
    qtd = rng.randint(qtd_min, qtd_max)
    return rng.sample(config["habilidades_base"], k=min(qtd, len(config["habilidades_base"])))


def _gerar_certificacoes(area: str, nivel: str, rng: random.Random) -> list[str]:
    config = AREA_CONFIG[area]
    max_cert = {"junior": 1, "pleno": 2, "senior": 3}[nivel]
    qtd = rng.randint(0, max_cert)
    if qtd == 0:
        return []
    return rng.sample(config["certificacoes"], k=min(qtd, len(config["certificacoes"])))


def gerar_candidato(
    idx: int,
    area: AreaAtuacao,
    nivel: NivelExperiencia,
    rng: random.Random,
    nomes_usados: set[str],
) -> Candidato:
    area_str = area.value
    nivel_str = nivel.value
    nome = _gerar_nome_unico(nomes_usados, rng)
    cidade, estado = rng.choice(CIDADES)
    anos_min, anos_max = NIVEL_ANOS[nivel_str]
    anos = rng.randint(anos_min, anos_max)

    return Candidato(
        id=f"CAND-{idx:04d}",
        nome=nome,
        email=_gerar_email(nome, idx),
        telefone=_gerar_telefone(rng),
        cidade=cidade,
        estado=estado,
        nivel=nivel,
        area=area,
        cargo_desejado=rng.choice(AREA_CONFIG[area_str]["cargos"][nivel_str]),
        resumo=RESUMOS[area_str][nivel_str],
        anos_experiencia=anos,
        formacao=_gerar_formacao(area_str, nivel_str, rng),
        experiencias=_gerar_experiencias(area_str, nivel_str, anos, rng),
        habilidades=_gerar_habilidades(area_str, nivel_str, rng),
        certificacoes=_gerar_certificacoes(area_str, nivel_str, rng),
        idiomas=rng.choice(IDIOMAS_OPCOES),
    )


def gerar_curriculos(
    total: int = TOTAL_PADRAO,
    seed: int = 42,
    output_dir: Path | None = None,
) -> list[Candidato]:
    """Gera currículos sintéticos distribuídos entre áreas e níveis."""
    rng = random.Random(seed)
    output_dir = output_dir or CANDIDATOS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    combinacoes = [(area, nivel) for area in AREAS for nivel in NIVEIS]
    base_por_combo = total // len(combinacoes)
    resto = total % len(combinacoes)

    distribuicao: list[tuple[AreaAtuacao, NivelExperiencia]] = []
    for i, combo in enumerate(combinacoes):
        qtd = base_por_combo + (1 if i < resto else 0)
        distribuicao.extend([combo] * qtd)

    rng.shuffle(distribuicao)

    nomes_usados: set[str] = set()
    candidatos: list[Candidato] = []

    for idx, (area, nivel) in enumerate(distribuicao, start=1):
        candidatos.append(gerar_candidato(idx, area, nivel, rng, nomes_usados))

    return candidatos


def salvar_json_individual(candidatos: list[Candidato], output_dir: Path | None = None) -> Path:
    """Salva cada candidato em um arquivo JSON separado."""
    output_dir = output_dir or CANDIDATOS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    for candidato in candidatos:
        arquivo = output_dir / f"{candidato.id.lower()}.json"
        arquivo.write_text(
            candidato.model_dump_json(indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return output_dir


def salvar_csv_consolidado(candidatos: list[Candidato], output_dir: Path | None = None) -> Path:
    """Salva todos os candidatos em um único CSV consolidado."""
    output_dir = output_dir or CANDIDATOS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    linhas = []
    for c in candidatos:
        linhas.append({
            "id": c.id,
            "nome": c.nome,
            "email": str(c.email),
            "telefone": c.telefone,
            "cidade": c.cidade,
            "estado": c.estado,
            "nivel": c.nivel.value,
            "area": c.area.value,
            "cargo_desejado": c.cargo_desejado,
            "resumo": c.resumo,
            "anos_experiencia": c.anos_experiencia,
            "formacao": " | ".join(
                f"{f.curso} ({f.instituicao}, {f.ano_conclusao})" for f in c.formacao
            ),
            "experiencias": " | ".join(
                f"{e.cargo} @ {e.empresa} ({e.inicio}-{e.fim or 'atual'})" for e in c.experiencias
            ),
            "habilidades": ", ".join(c.habilidades),
            "certificacoes": ", ".join(c.certificacoes),
            "idiomas": ", ".join(c.idiomas),
        })

    csv_path = output_dir / "candidatos_consolidado.csv"
    pd.DataFrame(linhas).to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def executar_geracao(total: int = TOTAL_PADRAO, seed: int = 42) -> dict:
    """Executa geração completa: JSONs individuais + CSV consolidado."""
    candidatos = gerar_curriculos(total=total, seed=seed)
    json_dir = salvar_json_individual(candidatos)
    csv_path = salvar_csv_consolidado(candidatos)

    resumo = {
        "total": len(candidatos),
        "json_dir": str(json_dir),
        "csv_path": str(csv_path),
        "por_area": {},
        "por_nivel": {},
    }

    for c in candidatos:
        resumo["por_area"][c.area.value] = resumo["por_area"].get(c.area.value, 0) + 1
        resumo["por_nivel"][c.nivel.value] = resumo["por_nivel"].get(c.nivel.value, 0) + 1

    metadata_path = CANDIDATOS_DIR / "metadata.json"
    metadata_path.write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")

    return resumo


if __name__ == "__main__":
    resultado = executar_geracao()
    print(f"Gerados {resultado['total']} currículos sintéticos.")
    print(f"JSONs em: {resultado['json_dir']}")
    print(f"CSV consolidado: {resultado['csv_path']}")
    print(f"Por área: {resultado['por_area']}")
    print(f"Por nível: {resultado['por_nivel']}")
