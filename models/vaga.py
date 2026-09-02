"""Modelos de domínio para vagas."""

from enum import Enum

from pydantic import BaseModel, Field

from models.candidato import NivelExperiencia


class ModalidadeTrabalho(str, Enum):
    REMOTO = "remoto"
    HIBRIDO = "hibrido"
    PRESENCIAL = "presencial"


class Vaga(BaseModel):
    id: str
    titulo: str
    area: str
    nivel: NivelExperiencia
    descricao: str
    responsabilidades: list[str]
    requisitos_obrigatorios: list[str]
    desejaveis: list[str] = Field(default_factory=list)
    tecnologias: list[str]
    formacao_minima: str
    anos_minimos_experiencia: int
    idiomas: list[str]
    modalidade: ModalidadeTrabalho
    localizacao: str
    quantidade_posicoes: int = Field(
        default=1,
        ge=1,
        description="Quantidade de posições disponíveis neste processo seletivo.",
    )
