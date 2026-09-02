from generators.curriculos_documentos import gerar_documentos


def test_gerar_documentos_pdf(tmp_path):
    arquivos = gerar_documentos(total=2, formato="pdf", output_dir=tmp_path)

    assert len(arquivos) == 2
    assert all(path.suffix == ".pdf" and path.exists() for path in arquivos)
