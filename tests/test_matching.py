"""Testes do motor de comparação e scoring."""

from pathlib import Path

import pandas as pd

from models.candidato import AreaAtuacao, Candidato, Formacao, NivelExperiencia
from models.vaga import ModalidadeTrabalho, Vaga
from services.matching import comparar_vaga, executar_matching
from services.scoring import pontuar


def _candidato(**kwargs) -> Candidato:
    base = dict(
        id="CAND-TEST",
        nome="Ana Dados",
        email="ana.dados001@email.com",
        telefone="(11) 99999-0000",
        cidade="São Paulo",
        estado="SP",
        nivel=NivelExperiencia.PLENO,
        area=AreaAtuacao.DADOS,
        cargo_desejado="Cientista de Dados Pleno",
        resumo="Profissional de dados com Python, SQL e Power BI.",
        anos_experiencia=4,
        formacao=[Formacao(instituicao="USP", curso="Estatística", nivel="Graduação", ano_conclusao=2018)],
        experiencias=[],
        habilidades=["Python", "SQL", "Pandas", "Power BI", "Machine Learning"],
        certificacoes=["Google Data Analytics"],
        idiomas=["Português (nativo)", "Inglês (avançado)"],
    )
    base.update(kwargs)
    return Candidato(**base)


def _vaga(**kwargs) -> Vaga:
    base = dict(
        id="VAG-TEST",
        titulo="Cientista de Dados",
        area="Ciência de Dados",
        nivel=NivelExperiencia.PLENO,
        descricao="Modelos e análises",
        responsabilidades=["Analisar dados"],
        requisitos_obrigatorios=["Experiência com Python e SQL"],
        desejaveis=["Power BI"],
        tecnologias=["Python", "SQL", "Pandas"],
        formacao_minima="Graduação em Estatística ou Computação",
        anos_minimos_experiencia=3,
        idiomas=["Português fluente", "Inglês intermediário"],
        modalidade=ModalidadeTrabalho.REMOTO,
        localizacao="Brasil (remoto)",
    )
    base.update(kwargs)
    return Vaga(**base)


def test_candidato_alinhado_tem_score_alto():
    score, breakdown, evidencias = pontuar(_candidato(), _vaga())
    assert score >= 70
    assert "Python" in evidencias["skills_atendidas"]
    assert breakdown.area == 100


def test_candidato_de_outra_area_fica_abaixo():
    rh = _candidato(
        id="CAND-RH",
        area=AreaAtuacao.RH,
        cargo_desejado="Analista de RH",
        habilidades=["Recrutamento e Seleção", "CLT", "eSocial"],
        certificacoes=[],
        resumo="Profissional de RH",
        formacao=[Formacao(instituicao="PUC", curso="Psicologia", nivel="Graduação", ano_conclusao=2019)],
    )
    score_dados, _, _ = pontuar(_candidato(), _vaga())
    score_rh, _, _ = pontuar(rh, _vaga())
    assert score_dados > score_rh


def test_ranking_ordena_por_score():
    forte = _candidato(id="CAND-A")
    fraco = _candidato(
        id="CAND-B",
        nome="Bruno RH",
        email="bruno.rh002@email.com",
        area=AreaAtuacao.RH,
        nivel=NivelExperiencia.JUNIOR,
        anos_experiencia=1,
        habilidades=["Recrutamento e Seleção"],
        resumo="Assistente de RH",
        cargo_desejado="Assistente de RH",
    )
    resultado = comparar_vaga(_vaga(), [fraco, forte])
    assert resultado.ranking[0].candidato_id == "CAND-A"
    assert resultado.ranking[0].posicao == 1
    assert resultado.ranking[1].posicao == 2


def test_executar_matching_grava_arquivos(tmp_path: Path):
    cand_dir = tmp_path / "candidatos"
    vaga_dir = tmp_path / "vagas"
    out_dir = tmp_path / "resultados"
    cand_dir.mkdir()
    vaga_dir.mkdir()

    _candidato(id="CAND-0001").model_dump_json()
    (cand_dir / "cand-0001.json").write_text(_candidato(id="CAND-0001").model_dump_json(), encoding="utf-8")
    (vaga_dir / "vag-0001.json").write_text(_vaga(id="VAG-0001").model_dump_json(), encoding="utf-8")

    resumo = executar_matching(
        top=10,
        output_dir=out_dir,
        candidatos_dir=cand_dir,
        vagas_dir=vaga_dir,
    )

    json_path = out_dir / "resultado_vag-0001.json"
    csv_path = out_dir / "ranking_consolidado.csv"
    assert json_path.exists()
    assert csv_path.exists()
    assert resumo["vagas_processadas"] == 1
    df = pd.read_csv(csv_path)
    assert len(df) == 1
    assert df.iloc[0]["score_total"] > 0
