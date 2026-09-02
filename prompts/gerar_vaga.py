"""Instruções para criação assistida de rascunhos de vagas."""

from __future__ import annotations


INSTRUCOES_GERAR_VAGA = """
Você apoia uma pessoa de RH a redigir uma vaga no Brasil.
Crie somente um rascunho claro, inclusivo, objetivo e revisável. Não invente
certificações obrigatórias, requisitos legais ou critérios discriminatórios.
Use linguagem neutra sobre idade, gênero, raça, religião, deficiência e origem.
Os requisitos devem ser proporcionais ao nível informado. Responda apenas no
formato estruturado solicitado.
""".strip()


def montar_prompt_gerar_vaga(descricao: str, nivel: str) -> str:
    return (
        "Crie um rascunho de vaga a partir desta necessidade de contratação.\n\n"
        f"Nível desejado: {nivel.title()}\n"
        f"Necessidade informada: {descricao.strip()}\n\n"
        "Inclua responsabilidades, requisitos, tecnologias, formação, experiência e idiomas. "
        "Considere o texto como ponto de partida; a pessoa recrutadora fará a revisão final."
    )
