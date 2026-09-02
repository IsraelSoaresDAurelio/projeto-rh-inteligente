"""Contratos para os pareceres produzidos pela camada de IA."""

from difflib import SequenceMatcher

from pydantic import BaseModel, Field, field_validator

LIMIAR_SIMILARIDADE = 0.75


def _similares(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio() >= LIMIAR_SIMILARIDADE


class ParecerCandidato(BaseModel):
    """Parecer conciso, baseado apenas nas evidências fornecidas ao modelo."""

    resumo: str = Field(description="Resumo objetivo, em português, com no máximo 100 palavras.")
    pontos_fortes: list[str] = Field(description="Evidências de aderência à vaga.")
    lacunas: list[str] = Field(description="Requisitos ainda não comprovados pelo currículo.")
    perguntas_entrevista: list[str] = Field(
        min_length=5,
        max_length=5,
        description=(
            "Exatamente 5 perguntas abertas e únicas (sem repetição), cada uma investigando "
            "um aspecto diferente da aderência à vaga."
        ),
    )
    potencial_desenvolvimento: str = Field(description="Sinal de evolução, sem inventar fatos.")
    recomendacao: str = Field(description="Uma de: avancar, entrevistar_com_ressalvas, nao_avancar.")

    @field_validator("pontos_fortes", "lacunas", "perguntas_entrevista")
    @classmethod
    def remover_duplicatas(cls, itens: list[str]) -> list[str]:
        """Modelos menores (ex.: qwen2.5:3b) às vezes repetem itens na mesma lista,
        às vezes só reformulando com outras palavras. Removemos duplicatas exatas E
        quase-idênticas (similaridade >= 75%), mantendo a ordem original."""
        unicos: list[str] = []
        for item in itens:
            if not any(_similares(item, existente) for existente in unicos):
                unicos.append(item)
        return unicos


class AnaliseVaga(BaseModel):
    vaga_id: str
    vaga_titulo: str
    candidatos_analisados: int
    analises: dict[str, ParecerCandidato]
