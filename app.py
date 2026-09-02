"""
Ponto de entrada da aplicação — Agente Inteligente de Apoio ao Recrutamento e Seleção.
"""

from pathlib import Path

from config.settings import RESULTADOS_DIR
from services.matching import executar_matching


def main() -> None:
    """Executa o motor de comparação (Etapa 4)."""
    project_root = Path(__file__).parent
    print("Agente Inteligente de Apoio ao Recrutamento e Seleção")
    print(f"Diretório raiz: {project_root}")
    resumo = executar_matching(top=30)
    print(f"Matching concluído: {resumo['vagas_processadas']} vagas × {resumo['candidatos']} candidatos.")
    print(f"Resultados em: {RESULTADOS_DIR}")


if __name__ == "__main__":
    main()
