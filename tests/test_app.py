"""Testes básicos do ponto de entrada."""

from app import main


def test_main_runs_without_error(capsys, monkeypatch, tmp_path):
    from models.candidato import AreaAtuacao, Candidato, Formacao, NivelExperiencia
    from models.vaga import ModalidadeTrabalho, Vaga

    cand_dir = tmp_path / "candidatos"
    vaga_dir = tmp_path / "vagas"
    out_dir = tmp_path / "resultados"
    cand_dir.mkdir()
    vaga_dir.mkdir()

    candidato = Candidato(
        id="CAND-0001",
        nome="Ana Dados",
        email="ana.dados001@email.com",
        telefone="(11) 99999-0000",
        cidade="São Paulo",
        estado="SP",
        nivel=NivelExperiencia.PLENO,
        area=AreaAtuacao.DADOS,
        cargo_desejado="Cientista de Dados",
        resumo="Python e SQL",
        anos_experiencia=4,
        formacao=[Formacao(instituicao="USP", curso="Estatística", nivel="Graduação", ano_conclusao=2018)],
        experiencias=[],
        habilidades=["Python", "SQL"],
        idiomas=["Português (nativo)"],
    )
    vaga = Vaga(
        id="VAG-0001",
        titulo="Analista de Dados",
        area="Análise de Dados",
        nivel=NivelExperiencia.JUNIOR,
        descricao="Análise",
        responsabilidades=["Analisar"],
        requisitos_obrigatorios=["SQL"],
        tecnologias=["SQL", "Python"],
        formacao_minima="Graduação",
        anos_minimos_experiencia=0,
        idiomas=["Português fluente"],
        modalidade=ModalidadeTrabalho.REMOTO,
        localizacao="Brasil",
    )
    (cand_dir / "cand-0001.json").write_text(candidato.model_dump_json(), encoding="utf-8")
    (vaga_dir / "vag-0001.json").write_text(vaga.model_dump_json(), encoding="utf-8")

    monkeypatch.setattr("app.executar_matching", lambda top=30: {
        "vagas_processadas": 1,
        "candidatos": 1,
    })
    monkeypatch.setattr("app.RESULTADOS_DIR", out_dir)

    main()
    captured = capsys.readouterr()
    assert "Agente Inteligente" in captured.out
