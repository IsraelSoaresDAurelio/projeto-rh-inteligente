"""Carrega candidatos e vagas a partir de data/."""

from pathlib import Path

from config.settings import CANDIDATOS_DIR, VAGAS_DIR
from models.candidato import Candidato
from models.vaga import Vaga


def carregar_candidatos(diretorio: Path | None = None) -> list[Candidato]:
    pasta = diretorio or CANDIDATOS_DIR
    arquivos = sorted(pasta.glob("cand-*.json"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum currículo encontrado em {pasta}")
    return [Candidato.model_validate_json(path.read_text(encoding="utf-8")) for path in arquivos]


def carregar_vagas(diretorio: Path | None = None) -> list[Vaga]:
    pasta = diretorio or VAGAS_DIR
    arquivos = sorted(pasta.glob("vag-*.json"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhuma vaga encontrada em {pasta}")
    return [Vaga.model_validate_json(path.read_text(encoding="utf-8")) for path in arquivos]
