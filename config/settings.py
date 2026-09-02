"""Configurações centralizadas da aplicação."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Permite executar ferramentas locais antes da instalação completa.
    def load_dotenv() -> bool:
        return False


load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "rh_inteligente.db"
CANDIDATOS_DIR = DATA_DIR / "candidatos"
VAGAS_DIR = DATA_DIR / "vagas"
RESULTADOS_DIR = DATA_DIR / "resultados"
CURRICULOS_ENTRADA_DIR = PROJECT_ROOT / "curriculos"
CURRICULOS_PROCESSADOS_DIR = DATA_DIR / "curriculos_processados"

# IA: mantenha a chave exclusivamente no arquivo .env (que é ignorado pelo Git).
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

# Provedores aceitos: openai (API com custo) ou ollama (modelo executado localmente).
# O padrão prioriza execução local e não requer chave de API.
IA_PROVIDER = os.getenv("IA_PROVIDER", "ollama").strip().lower()
# Modelo compacto para funcionar em computadores sem GPU dedicada.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
