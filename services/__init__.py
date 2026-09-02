"""Serviços de negócio: matching, scoring, orquestração."""

__all__ = ["executar_matching", "pontuar"]


def __getattr__(name: str):
    if name == "executar_matching":
        from services.matching import executar_matching
        return executar_matching
    if name == "pontuar":
        from services.scoring import pontuar
        return pontuar
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
