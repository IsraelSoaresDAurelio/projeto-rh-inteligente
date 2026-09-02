"""Testes unitários da orquestração de análises, sem chamar a API externa."""

from integrations.llm import ClienteLLM, ClienteOllama, criar_cliente_llm
from models.analise import ParecerCandidato
from services.analise import analisar_resultado, construir_contexto
from tests.test_matching import _candidato, _vaga
from services.matching import comparar_vaga


class LLMFalso(ClienteLLM):
    def gerar_parecer(self, contexto: dict) -> ParecerCandidato:
        return ParecerCandidato(
            resumo="Perfil com aderência comprovada.",
            pontos_fortes=["Python"],
            lacunas=["Validar experiência prática."],
            perguntas_entrevista=[
                "Conte sobre um projeto em Python.",
                "Como você usou SQL para investigar um problema de dados?",
                "Descreva uma análise feita com Pandas que mudou uma decisão.",
                "Quais critérios você usa para validar a qualidade de um conjunto de dados?",
                "Como comunica resultados de análise para pessoas não técnicas?",
            ],
            potencial_desenvolvimento="Pode evoluir com mentoria.",
            recomendacao="avancar",
        )


def test_contexto_nao_expoe_contatos_do_candidato():
    candidato = _candidato()
    match = comparar_vaga(_vaga(), [candidato]).ranking[0]
    contexto = construir_contexto(_vaga(), candidato, match)
    assert "email" not in contexto["candidato"]
    assert "telefone" not in contexto["candidato"]
    assert contexto["matching_auditavel"]["score_total"] == match.score_total


def test_analisar_resultado_usa_top_e_retorna_pareceres():
    candidato = _candidato()
    vaga = _vaga()
    resultado = comparar_vaga(vaga, [candidato])
    analise = analisar_resultado(resultado, vaga, [candidato], LLMFalso(), top=1)
    assert analise.candidatos_analisados == 1
    assert analise.analises[candidato.id].recomendacao == "avancar"


def test_factory_seleciona_ollama_sem_chave_de_api():
    cliente = criar_cliente_llm(
        "ollama",
        model="llama3.2:3b",
        base_url="http://localhost:11434/",
    )
    assert isinstance(cliente, ClienteOllama)
    assert cliente.model == "llama3.2:3b"
    assert cliente.base_url == "http://localhost:11434"
