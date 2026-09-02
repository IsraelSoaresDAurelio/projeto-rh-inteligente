"""Testes do gerador de vagas fictícias."""

import json
from pathlib import Path

import pytest

from generators.gerar_vagas import executar_geracao, gerar_vagas
from models.vaga import Vaga


AREAS_ESPERADAS = {
    "Inteligência Artificial",
    "Ciência de Dados",
    "Engenharia de Dados",
    "Desenvolvimento Python",
    "RH",
    "Compliance",
    "Power BI",
    "Automação",
    "Cloud",
    "Análise de Dados",
}

CAMPOS_OBRIGATORIOS = {
    "id", "titulo", "area", "nivel", "descricao", "responsabilidades",
    "requisitos_obrigatorios", "desejaveis", "tecnologias", "formacao_minima",
    "anos_minimos_experiencia", "idiomas", "modalidade", "localizacao",
}


def test_gerar_pelo_menos_10_vagas():
    vagas = gerar_vagas()
    assert len(vagas) >= 10


def test_areas_variadas():
    vagas = gerar_vagas()
    areas = {v.area for v in vagas}
    assert AREAS_ESPERADAS.issubset(areas)


def test_campos_obrigatorios():
    vagas = gerar_vagas()
    for vaga in vagas:
        dados = vaga.model_dump()
        assert CAMPOS_OBRIGATORIOS.issubset(dados.keys())
        assert dados["responsabilidades"]
        assert dados["requisitos_obrigatorios"]
        assert dados["tecnologias"]


def test_executar_geracao_cria_arquivos(tmp_path: Path):
    resultado = executar_geracao(output_dir=tmp_path)

    json_files = list(tmp_path.glob("vag-*.json"))
    consolidado = tmp_path / "vagas_consolidado.json"
    metadata = tmp_path / "metadata.json"

    assert resultado["total"] >= 10
    assert len(json_files) >= 10
    assert consolidado.exists()
    assert metadata.exists()

    dados = json.loads(consolidado.read_text(encoding="utf-8"))
    assert len(dados) >= 10
    assert all(isinstance(item, dict) for item in dados)
