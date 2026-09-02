"""Persistência local em SQLite para candidatos, vagas e rankings."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from config.settings import CANDIDATOS_DIR, DATABASE_PATH, RESULTADOS_DIR, VAGAS_DIR


def _conectar() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco() -> None:
    """Cria as tabelas locais na primeira execução."""
    with _conectar() as conexao:
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS candidatos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                area TEXT,
                nivel TEXT,
                cargo_desejado TEXT,
                anos_experiencia INTEGER,
                dados_json TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vagas (
                id TEXT PRIMARY KEY,
                titulo TEXT NOT NULL,
                area TEXT,
                nivel TEXT,
                dados_json TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rankings (
                vaga_id TEXT NOT NULL,
                candidato_id TEXT NOT NULL,
                posicao INTEGER NOT NULL,
                score_total REAL NOT NULL,
                dados_json TEXT NOT NULL,
                atualizado_em TEXT NOT NULL,
                PRIMARY KEY (vaga_id, candidato_id),
                FOREIGN KEY (vaga_id) REFERENCES vagas(id),
                FOREIGN KEY (candidato_id) REFERENCES candidatos(id)
            );

            CREATE INDEX IF NOT EXISTS idx_rankings_vaga_posicao
            ON rankings(vaga_id, posicao);

            CREATE TABLE IF NOT EXISTS eventos_auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                referencia TEXT NOT NULL,
                detalhes_json TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );
            """
        )


def _carregar_registros(pasta: Path, padrao: str) -> list[dict]:
    registros = []
    for path in sorted(pasta.glob(padrao)):
        registros.append(json.loads(path.read_text(encoding="utf-8")))
    return registros


def sincronizar_banco() -> dict[str, int]:
    """Espelha os JSONs do fluxo local no SQLite de forma transacional."""
    inicializar_banco()
    candidatos = _carregar_registros(CANDIDATOS_DIR, "cand-*.json")
    vagas = _carregar_registros(VAGAS_DIR, "vag-*.json")
    resultados = _carregar_registros(RESULTADOS_DIR, "resultado_vag-*.json")
    atualizado_em = datetime.now().isoformat(timespec="seconds")

    with _conectar() as conexao:
        conexao.execute("DELETE FROM rankings")
        conexao.execute("DELETE FROM candidatos")
        conexao.execute("DELETE FROM vagas")

        conexao.executemany(
            """
            INSERT INTO candidatos (
                id, nome, area, nivel, cargo_desejado, anos_experiencia, dados_json, atualizado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    candidato["id"],
                    candidato["nome"],
                    candidato.get("area"),
                    candidato.get("nivel"),
                    candidato.get("cargo_desejado"),
                    candidato.get("anos_experiencia"),
                    json.dumps(candidato, ensure_ascii=False),
                    atualizado_em,
                )
                for candidato in candidatos
            ],
        )
        conexao.executemany(
            """
            INSERT INTO vagas (id, titulo, area, nivel, dados_json, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    vaga["id"],
                    vaga["titulo"],
                    vaga.get("area"),
                    vaga.get("nivel"),
                    json.dumps(vaga, ensure_ascii=False),
                    atualizado_em,
                )
                for vaga in vagas
            ],
        )

        rankings = [
            (resultado["vaga_id"], item, atualizado_em)
            for resultado in resultados
            for item in resultado.get("ranking", [])
        ]
        conexao.executemany(
            """
            INSERT INTO rankings (vaga_id, candidato_id, posicao, score_total, dados_json, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    vaga_id,
                    item["candidato_id"],
                    item["posicao"],
                    item["score_total"],
                    json.dumps(item, ensure_ascii=False),
                    momento,
                )
                for vaga_id, item, momento in rankings
            ],
        )

    return {"candidatos": len(candidatos), "vagas": len(vagas), "rankings": len(rankings)}


def garantir_banco_atualizado() -> dict[str, int]:
    """Atualiza o banco somente quando os arquivos de origem forem mais recentes."""
    fontes = [
        *CANDIDATOS_DIR.glob("cand-*.json"),
        *VAGAS_DIR.glob("vag-*.json"),
        *RESULTADOS_DIR.glob("resultado_vag-*.json"),
    ]
    if not DATABASE_PATH.exists() or any(path.stat().st_mtime > DATABASE_PATH.stat().st_mtime for path in fontes):
        return sincronizar_banco()

    with _conectar() as conexao:
        return {
            "candidatos": conexao.execute("SELECT COUNT(*) FROM candidatos").fetchone()[0],
            "vagas": conexao.execute("SELECT COUNT(*) FROM vagas").fetchone()[0],
            "rankings": conexao.execute("SELECT COUNT(*) FROM rankings").fetchone()[0],
        }


def registrar_evento_auditoria(tipo: str, referencia: str, detalhes: dict | None = None) -> None:
    """Registra ações operacionais sem gravar conteúdo sensível no histórico."""
    inicializar_banco()
    with _conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO eventos_auditoria (tipo, referencia, detalhes_json, criado_em)
            VALUES (?, ?, ?, ?)
            """,
            (
                tipo,
                referencia,
                json.dumps(detalhes or {}, ensure_ascii=False),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def listar_eventos_recentes(limite: int = 8) -> list[dict]:
    """Retorna o histórico operacional mais recente para o dashboard."""
    inicializar_banco()
    with _conectar() as conexao:
        registros = conexao.execute(
            """
            SELECT tipo, referencia, detalhes_json, criado_em
            FROM eventos_auditoria
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()
    return [
        {
            "tipo": registro["tipo"],
            "referencia": registro["referencia"],
            "detalhes": json.loads(registro["detalhes_json"]),
            "criado_em": registro["criado_em"],
        }
        for registro in registros
    ]


if __name__ == "__main__":
    resumo = sincronizar_banco()
    print(
        "Banco SQLite sincronizado: "
        f"{resumo['candidatos']} candidatos, {resumo['vagas']} vagas e {resumo['rankings']} posições de ranking."
    )
