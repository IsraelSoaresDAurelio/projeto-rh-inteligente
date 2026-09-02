"""Modelos de domínio para resultados de matching."""

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    tecnologias: float
    requisitos: float
    experiencia: float
    area: float
    formacao: float
    idiomas: float
    desejaveis: float


class MatchCandidato(BaseModel):
    posicao: int
    candidato_id: str
    nome: str
    nivel: str
    area: str
    cargo_desejado: str
    anos_experiencia: int
    score_total: float
    breakdown: ScoreBreakdown
    skills_atendidas: list[str] = Field(default_factory=list)
    skills_faltantes: list[str] = Field(default_factory=list)
    requisitos_atendidos: list[str] = Field(default_factory=list)
    requisitos_pendentes: list[str] = Field(default_factory=list)


class ResultadoVaga(BaseModel):
    vaga_id: str
    vaga_titulo: str
    vaga_area: str
    vaga_nivel: str
    total_candidatos: int
    ranking: list[MatchCandidato]
