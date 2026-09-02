"""Testes da ingestão local de currículos."""

from services.ingestao_curriculos import executar_ingestao, processar_arquivo


def test_processar_txt_preserva_texto_e_rastreabilidade(tmp_path):
    arquivo = tmp_path / "ana_silva.txt"
    arquivo.write_text("Ana Silva\nPython, SQL e Power BI", encoding="utf-8")

    curriculo = processar_arquivo(arquivo)

    assert curriculo.arquivo_origem == "ana_silva.txt"
    assert curriculo.formato == "txt"
    assert "Python" in curriculo.texto
    assert len(curriculo.hash_sha256) == 64


def test_executar_ingestao_grava_json_e_ignora_formato_desconhecido(tmp_path):
    entrada = tmp_path / "entrada"
    saida = tmp_path / "saida"
    entrada.mkdir()
    (entrada / "curriculo.txt").write_text("Profissional de dados", encoding="utf-8")
    (entrada / "arquivo.exe").write_bytes(b"nao processar")

    gerados, avisos = executar_ingestao(entrada, saida)

    assert len(gerados) == 1
    assert gerados[0].exists()
    assert "Profissional de dados" in gerados[0].read_text(encoding="utf-8")
    assert len(avisos) == 1
