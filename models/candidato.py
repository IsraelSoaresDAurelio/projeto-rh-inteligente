"""Modelos de domínio para candidatos."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class NivelExperiencia(str, Enum):
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"


class AreaAtuacao(str, Enum):
    TECH = "tech"
    ENGENHARIA = "engenharia"
    RH = "rh"
    ADMINISTRACAO = "administracao"
    DADOS = "dados"


class Formacao(BaseModel):
    instituicao: str
    curso: str
    nivel: str
    ano_conclusao: Optional[int] = None
    status: str = "concluido"


class Experiencia(BaseModel):
    empresa: str
    cargo: str
    inicio: str
    fim: Optional[str] = None
    descricao: str


class Candidato(BaseModel):
    id: str
    nome: str
    email: EmailStr
    telefone: str
    cidade: str
    estado: str
    nivel: NivelExperiencia
    area: AreaAtuacao
    cargo_desejado: str
    resumo: str
    anos_experiencia: int
    formacao: list[Formacao]
    experiencias: list[Experiencia]
    habilidades: list[str]
    certificacoes: list[str] = Field(default_factory=list)
    idiomas: list[str] = Field(default_factory=list)
