"""Geradores de dados sintéticos para testes e demonstração."""

__all__ = ["executar_geracao", "gerar_curriculos"]


def __getattr__(name: str):
    if name in __all__:
        from generators import curriculos
        return getattr(curriculos, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
