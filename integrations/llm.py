"""Adaptador para a API da OpenAI usando Responses API e saída estruturada."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from config.settings import (
    IA_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_NUM_CTX,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from models.analise import ParecerCandidato
from prompts.parecer_recrutamento import INSTRUCOES, montar_prompt


class ConfiguracaoLLMError(RuntimeError):
    """Indica configuração ausente ou uma resposta inválida do provedor de IA."""


class ClienteLLM:
    """Cliente pequeno e facilmente substituível por outro provedor no futuro."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL

    def gerar_parecer(self, contexto: dict) -> ParecerCandidato:
        if not self.api_key:
            raise ConfiguracaoLLMError(
                "OPENAI_API_KEY não configurada. Crie um arquivo .env com OPENAI_API_KEY=..."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ConfiguracaoLLMError("Instale as dependências com: pip install -r requirements.txt") from exc

        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model=self.model,
            instructions=INSTRUCOES,
            input=montar_prompt(contexto),
            store=False,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "parecer_candidato",
                    "strict": True,
                    "schema": ParecerCandidato.model_json_schema(),
                }
            },
        )
        try:
            return ParecerCandidato.model_validate(json.loads(response.output_text))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ConfiguracaoLLMError("A OpenAI não retornou um parecer no formato esperado.") from exc


class ClienteOllama:
    """Cliente para um Ollama em execução local, sem chave de API."""

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or OLLAMA_MODEL
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")

    def gerar_parecer(self, contexto: dict) -> ParecerCandidato:
        schema = ParecerCandidato.model_json_schema()
        prompt = (
            f"{montar_prompt(contexto)}\n\n"
            "Responda estritamente no schema JSON abaixo, sem texto adicional:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": INSTRUCOES},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": schema,
            # Limita o contexto para manter o uso de RAM compatível com execução local.
            "options": {"temperature": 0, "num_ctx": OLLAMA_NUM_CTX},
        }
        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=180) as response:
                resposta = json.loads(response.read().decode("utf-8"))
            conteudo = resposta["message"]["content"]
            return ParecerCandidato.model_validate_json(conteudo)
        except URLError as exc:
            raise ConfiguracaoLLMError(
                "Não foi possível conectar ao Ollama. Instale-o, inicie-o e confirme "
                f"{self.base_url} antes de gerar pareceres."
            ) from exc
        except (KeyError, json.JSONDecodeError, ValueError) as exc:
            raise ConfiguracaoLLMError("O Ollama não retornou um parecer no formato esperado.") from exc


def criar_cliente_llm(
    provider: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> ClienteLLM | ClienteOllama:
    """Seleciona o provedor configurado, mantendo o restante da aplicação independente."""
    selecionado = (provider or IA_PROVIDER).lower()
    if selecionado == "openai":
        return ClienteLLM(model=model)
    if selecionado == "ollama":
        return ClienteOllama(model=model, base_url=base_url)
    raise ConfiguracaoLLMError(
        f"IA_PROVIDER inválido: {selecionado}. Use 'openai' ou 'ollama'."
    )
