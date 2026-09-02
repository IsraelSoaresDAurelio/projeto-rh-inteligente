"""Pontuação determinística de aderência candidato × vaga."""

import re
import unicodedata

from models.candidato import AreaAtuacao, Candidato, NivelExperiencia
from models.resultado import ScoreBreakdown
from models.vaga import Vaga

PESOS = {
    "tecnologias": 0.30,
    "requisitos": 0.20,
    "experiencia": 0.20,
    "area": 0.15,
    "formacao": 0.05,
    "idiomas": 0.05,
    "desejaveis": 0.05,
}

NIVEL_ORDEM = {
    NivelExperiencia.JUNIOR: 0,
    NivelExperiencia.PLENO: 1,
    NivelExperiencia.SENIOR: 2,
}

AREA_VAGA: dict[str, set[AreaAtuacao]] = {
    "inteligencia artificial": {AreaAtuacao.DADOS, AreaAtuacao.TECH},
    "ciencia de dados": {AreaAtuacao.DADOS},
    "engenharia de dados": {AreaAtuacao.DADOS, AreaAtuacao.TECH},
    "desenvolvimento python": {AreaAtuacao.TECH},
    "rh": {AreaAtuacao.RH},
    "compliance": {AreaAtuacao.ADMINISTRACAO, AreaAtuacao.RH},
    "power bi": {AreaAtuacao.DADOS, AreaAtuacao.ADMINISTRACAO},
    "automacao": {AreaAtuacao.TECH, AreaAtuacao.ENGENHARIA, AreaAtuacao.DADOS},
    "cloud": {AreaAtuacao.TECH},
    "analise de dados": {AreaAtuacao.DADOS, AreaAtuacao.ADMINISTRACAO},
}

ALIASES: dict[str, set[str]] = {
    "python": {"python", "pandas", "fastapi", "django", "flask"},
    "sql": {"sql", "postgresql", "mysql", "bigquery"},
    "power bi": {"power bi", "dax", "power query", "pl-300"},
    "excel": {"excel", "excel avancado"},
    "aws": {"aws", "amazon", "sagemaker", "cloudwatch"},
    "docker": {"docker", "containers", "kubernetes"},
    "kubernetes": {"kubernetes", "k8s", "docker"},
    "terraform": {"terraform", "iac", "cloudformation"},
    "machine learning": {"machine learning", "ml", "pytorch", "scikit-learn", "xgboost"},
    "pytorch": {"pytorch", "machine learning", "ml"},
    "scikit-learn": {"scikit-learn", "sklearn", "machine learning"},
    "mlflow": {"mlflow", "mlops"},
    "airflow": {"airflow", "etl", "pipelines"},
    "spark": {"spark", "apache spark"},
    "dbt": {"dbt", "etl"},
    "kafka": {"kafka", "streaming"},
    "pandas": {"pandas", "python"},
    "git": {"git", "github"},
    "rest api": {"rest api", "apis rest", "api", "fastapi"},
    "apis rest": {"apis rest", "rest api", "api"},
    "linkedin recruiter": {"linkedin recruiter", "linkedin", "recrutamento"},
    "gupy": {"gupy", "ats"},
    "recrutamento": {"recrutamento", "selecao", "entrevista"},
    "esocial": {"esocial", "clt", "departamento pessoal"},
    "clt": {"clt", "esocial"},
    "lgpd": {"lgpd", "compliance", "privacidade"},
    "power automate": {"power automate", "rpa", "automacao"},
    "rpa": {"rpa", "power automate", "uipath", "automacao"},
    "prometheus": {"prometheus", "observabilidade"},
}


def _norm(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    ascii_txt = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_txt).strip()


def _tokens(texto: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9+]+", _norm(texto)) if len(t) >= 2}


def _expand(termo: str) -> set[str]:
    chave = _norm(termo)
    extras = ALIASES.get(chave, set())
    return {_norm(chave), *{_norm(a) for a in extras}, *_tokens(termo)}


def _corpus_candidato(candidato: Candidato) -> str:
    partes = [
        candidato.resumo,
        candidato.cargo_desejado,
        " ".join(candidato.habilidades),
        " ".join(candidato.certificacoes),
        " ".join(f.curso for f in candidato.formacao),
        " ".join(f"{e.cargo} {e.descricao}" for e in candidato.experiencias),
    ]
    return _norm(" ".join(partes))


def _contem(termo: str, corpus: str) -> bool:
    alvos = _expand(termo)
    corpus_tokens = set(corpus.split())
    for alvo in alvos:
        if " " in alvo:
            if alvo in corpus:
                return True
        elif alvo in corpus_tokens or f" {alvo} " in f" {corpus} ":
            return True
    return False


def _cobertura(itens: list[str], corpus: str) -> tuple[float, list[str], list[str]]:
    if not itens:
        return 1.0, [], []
    atendidos: list[str] = []
    pendentes: list[str] = []
    for item in itens:
        if _contem(item, corpus):
            atendidos.append(item)
        else:
            pendentes.append(item)
    return len(atendidos) / len(itens), atendidos, pendentes


def _score_experiencia(candidato: Candidato, vaga: Vaga) -> float:
    minimo = vaga.anos_minimos_experiencia
    if minimo <= 0:
        anos_score = 1.0
    elif candidato.anos_experiencia >= minimo:
        anos_score = 1.0
    else:
        anos_score = candidato.anos_experiencia / minimo

    delta = NIVEL_ORDEM[candidato.nivel] - NIVEL_ORDEM[vaga.nivel]
    if delta == 0:
        nivel_score = 1.0
    elif delta == 1:
        nivel_score = 0.85
    elif delta == -1:
        nivel_score = 0.55
    elif delta == 2:
        nivel_score = 0.70
    else:
        nivel_score = 0.25

    return round(0.6 * anos_score + 0.4 * nivel_score, 4)


def _score_area(candidato: Candidato, vaga: Vaga) -> float:
    areas_alvo = AREA_VAGA.get(_norm(vaga.area), set())
    if candidato.area in areas_alvo:
        return 1.0
    if areas_alvo and candidato.area in {AreaAtuacao.DADOS, AreaAtuacao.TECH} and (
        AreaAtuacao.DADOS in areas_alvo or AreaAtuacao.TECH in areas_alvo
    ):
        return 0.55
    return 0.15


def _score_formacao(candidato: Candidato, vaga: Vaga) -> float:
    texto_vaga = _norm(vaga.formacao_minima)
    cursos = _norm(" ".join(f.curso for f in candidato.formacao))
    if not texto_vaga:
        return 1.0
    palavras = [p for p in texto_vaga.split() if len(p) > 3]
    if not palavras:
        return 0.5
    hits = sum(1 for p in set(palavras) if p in cursos)
    return min(1.0, 0.35 + hits / max(len(set(palavras)), 1))


def _nivel_idioma(texto: str) -> int:
    n = _norm(texto)
    if any(x in n for x in ("nativo", "fluente", "avancado")):
        return 3
    if "intermediario" in n:
        return 2
    if "basico" in n:
        return 1
    return 2


def _score_idiomas(candidato: Candidato, vaga: Vaga) -> float:
    if not vaga.idiomas:
        return 1.0
    cand = [_norm(i) for i in candidato.idiomas]
    pontos = 0.0
    for req in vaga.idiomas:
        req_n = _norm(req)
        lingua = "ingles" if "ingles" in req_n else "espanhol" if "espanhol" in req_n else "portugues"
        match = next((c for c in cand if lingua in c), None)
        if match is None:
            if lingua == "portugues":
                pontos += 1.0
            continue
        if _nivel_idioma(match) >= _nivel_idioma(req):
            pontos += 1.0
        else:
            pontos += 0.55
    return pontos / len(vaga.idiomas)


def pontuar(candidato: Candidato, vaga: Vaga) -> tuple[float, ScoreBreakdown, dict]:
    corpus = _corpus_candidato(candidato)

    tec_score, tec_ok, tec_falta = _cobertura(vaga.tecnologias, corpus)
    req_score, req_ok, req_falta = _cobertura(vaga.requisitos_obrigatorios, corpus)
    des_score, _, _ = _cobertura(vaga.desejaveis, corpus)

    breakdown = ScoreBreakdown(
        tecnologias=round(tec_score * 100, 2),
        requisitos=round(req_score * 100, 2),
        experiencia=round(_score_experiencia(candidato, vaga) * 100, 2),
        area=round(_score_area(candidato, vaga) * 100, 2),
        formacao=round(_score_formacao(candidato, vaga) * 100, 2),
        idiomas=round(_score_idiomas(candidato, vaga) * 100, 2),
        desejaveis=round(des_score * 100, 2),
    )

    total = (
        breakdown.tecnologias * PESOS["tecnologias"]
        + breakdown.requisitos * PESOS["requisitos"]
        + breakdown.experiencia * PESOS["experiencia"]
        + breakdown.area * PESOS["area"]
        + breakdown.formacao * PESOS["formacao"]
        + breakdown.idiomas * PESOS["idiomas"]
        + breakdown.desejaveis * PESOS["desejaveis"]
    )

    evidencias = {
        "skills_atendidas": tec_ok,
        "skills_faltantes": tec_falta,
        "requisitos_atendidos": req_ok,
        "requisitos_pendentes": req_falta,
    }
    return round(total, 2), breakdown, evidencias
