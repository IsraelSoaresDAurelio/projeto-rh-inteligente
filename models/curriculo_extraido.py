"""Contrato do currículo extraído antes de qualquer normalização para o matching."""

from datetime import datetime

from pydantic import BaseModel, Field


class CurriculoExtraido(BaseModel):
    id: str
    arquivo_origem: str
    formato: str
    hash_sha256: str
    extraido_em: datetime
    texto: str = Field(min_length=1)
    metadados: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
