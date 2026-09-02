"""Modelos de domínio: Candidato, Vaga, Resultado."""

from models.candidato import (
    AreaAtuacao,
    Candidato,
    Experiencia,
    Formacao,
    NivelExperiencia,
)
from models.resultado import MatchCandidato, ResultadoVaga, ScoreBreakdown
from models.vaga import ModalidadeTrabalho, Vaga

__all__ = [
    "AreaAtuacao",
    "Candidato",
    "Experiencia",
    "Formacao",
    "MatchCandidato",
    "ModalidadeTrabalho",
    "NivelExperiencia",
    "ResultadoVaga",
    "ScoreBreakdown",
    "Vaga",
]
