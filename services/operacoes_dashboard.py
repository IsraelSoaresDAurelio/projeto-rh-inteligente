"""Operações locais disparadas pelo dashboard de recrutamento."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterable

from config.settings import CURRICULOS_ENTRADA_DIR, VAGAS_DIR
from models.vaga import Vaga
from services.database import registrar_evento_auditoria
from services.ingestao_curriculos import FORMATOS_SUPORTADOS


def _nome_seguro(nome: str) -> str:
    """Remove caminhos e caracteres impróprios de um nome recebido pelo upload."""
    base = Path(nome).name.replace("\\", "_").replace("/", "_")
    return re.sub(r"[^\w. -]", "_", base, flags=re.UNICODE).strip(" .") or "curriculo"


def salvar_curriculos_enviados(
    arquivos: Iterable[Any],
    destino: Path | None = None,
) -> tuple[list[Path], list[str]]:
    """Persiste uploads aceitos e registra somente metadados de rastreabilidade."""
    destino = destino or CURRICULOS_ENTRADA_DIR
    destino.mkdir(parents=True, exist_ok=True)
    salvos: list[Path] = []
    avisos: list[str] = []

    for arquivo in arquivos:
        nome = _nome_seguro(str(arquivo.name))
        extensao = Path(nome).suffix.lower()
        if extensao not in FORMATOS_SUPORTADOS:
            avisos.append(f"{nome}: formato não suportado.")
            continue
        conteudo = arquivo.getvalue()
        if not conteudo:
            avisos.append(f"{nome}: arquivo vazio.")
            continue
        digest = hashlib.sha256(conteudo).hexdigest()
        caminho = destino / f"{Path(nome).stem}_{digest[:8]}{extensao}"
        caminho.write_bytes(conteudo)
        salvos.append(caminho)
        registrar_evento_auditoria(
            "curriculo_enviado",
            caminho.name,
            {"sha256": digest, "tamanho_bytes": len(conteudo), "formato": extensao.lstrip(".")},
        )
    return salvos, avisos


def _proximo_id_vaga(diretorio: Path) -> str:
    maiores_ids = []
    for path in diretorio.glob("vag-*.json"):
        correspondencia = re.fullmatch(r"vag-(\d+)", path.stem, flags=re.IGNORECASE)
        if correspondencia:
            maiores_ids.append(int(correspondencia.group(1)))
    return f"VAG-{max(maiores_ids, default=0) + 1:04d}"


def criar_vaga_pelo_dashboard(dados: dict[str, Any], diretorio: Path | None = None) -> tuple[Vaga, Path]:
    """Valida, persiste e audita uma nova vaga criada na interface."""
    diretorio = diretorio or VAGAS_DIR
    diretorio.mkdir(parents=True, exist_ok=True)
    vaga = Vaga(id=_proximo_id_vaga(diretorio), **dados)
    caminho = diretorio / f"{vaga.id.lower()}.json"
    caminho.write_text(vaga.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
    registrar_evento_auditoria(
        "vaga_criada",
        vaga.id,
        {"titulo": vaga.titulo, "area": vaga.area, "quantidade_posicoes": vaga.quantidade_posicoes},
    )
    return vaga, caminho
