"""Modelo estruturado para rascunhos de vagas gerados com assistência de IA."""

from pydantic import BaseModel, Field


class RascunhoVaga(BaseModel):
    """Conteúdo revisável por uma pessoa antes de criar uma vaga."""

    titulo: str
    area: str
    descricao: str
    responsabilidades: list[str] = Field(min_length=1)
    requisitos_obrigatorios: list[str] = Field(min_length=1)
    desejaveis: list[str] = Field(default_factory=list)
    tecnologias: list[str] = Field(min_length=1)
    formacao_minima: str
    anos_minimos_experiencia: int = Field(ge=0)
    idiomas: list[str] = Field(min_length=1)
