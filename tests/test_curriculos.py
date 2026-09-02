"""Testes do gerador de currículos sintéticos."""

import json
from pathlib import Path

import pandas as pd
import pytest

from generators.curriculos import executar_geracao, gerar_curriculos
from models.candidato import AreaAtuacao, NivelExperiencia


@pytest.fixture
def tmp_output(tmp_path: Path):
    return tmp_path / "candidatos"


def test_gerar_300_curriculos(tmp_output: Path):
    candidatos = gerar_curriculos(total=300, seed=123, output_dir=tmp_output)
    assert len(candidatos) == 300


def test_variacao_areas_e_niveis(tmp_output: Path):
    candidatos = gerar_curriculos(total=300, seed=123, output_dir=tmp_output)

    areas = {c.area for c in candidatos}
    niveis = {c.nivel for c in candidatos}

    assert areas == set(AreaAtuacao)
    assert niveis == set(NivelExperiencia)


def test_candidatos_unicos(tmp_output: Path):
    candidatos = gerar_curriculos(total=300, seed=123, output_dir=tmp_output)

    ids = [c.id for c in candidatos]
    nomes = [c.nome for c in candidatos]
    emails = [str(c.email) for c in candidatos]

    assert len(set(ids)) == 300
    assert len(set(nomes)) == 300
    assert len(set(emails)) == 300


def test_executar_geracao_cria_arquivos(tmp_output: Path, monkeypatch):
    monkeypatch.setattr("generators.curriculos.CANDIDATOS_DIR", tmp_output)

    resultado = executar_geracao(total=30, seed=99)

    json_files = list(tmp_output.glob("cand-*.json"))
    csv_path = tmp_output / "candidatos_consolidado.csv"
    metadata_path = tmp_output / "metadata.json"

    assert resultado["total"] == 30
    assert len(json_files) == 30
    assert csv_path.exists()
    assert metadata_path.exists()

    df = pd.read_csv(csv_path)
    assert len(df) == 30
    assert "area" in df.columns
    assert "nivel" in df.columns

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["total"] == 30
