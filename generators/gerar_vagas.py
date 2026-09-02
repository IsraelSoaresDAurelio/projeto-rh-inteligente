"""Gerador de vagas fictícias para o sistema de recrutamento."""

import json
from pathlib import Path

from config.settings import VAGAS_DIR
from models.candidato import NivelExperiencia
from models.vaga import ModalidadeTrabalho, Vaga

VAGAS_TEMPLATE: list[dict] = [
    {
        "id": "VAG-0001",
        "titulo": "Engenheiro de Machine Learning",
        "area": "Inteligência Artificial",
        "nivel": NivelExperiencia.SENIOR,
        "descricao": (
            "Buscamos profissional para liderar projetos de IA generativa e modelos "
            "preditivos, do protótipo à produção, em parceria com times de produto e dados."
        ),
        "responsabilidades": [
            "Desenvolver e operacionalizar modelos de ML e LLMs",
            "Definir pipelines de treinamento, validação e monitoramento",
            "Colaborar com engenharia de dados na preparação de features",
            "Documentar experimentos e garantir governança dos modelos",
        ],
        "requisitos_obrigatorios": [
            "Experiência com Python e frameworks de ML",
            "Conhecimento em NLP ou visão computacional",
            "Vivência com MLOps e versionamento de modelos",
            "Capacidade analítica e comunicação com stakeholders",
        ],
        "desejaveis": [
            "Experiência com LangChain ou ferramentas de IA generativa",
            "Publicações ou projetos open source em IA",
            "Conhecimento em fine-tuning de LLMs",
        ],
        "tecnologias": ["Python", "PyTorch", "scikit-learn", "MLflow", "Docker", "AWS SageMaker"],
        "formacao_minima": "Graduação em Ciência da Computação, Engenharia ou áreas correlatas",
        "anos_minimos_experiencia": 5,
        "idiomas": ["Português fluente", "Inglês avançado"],
        "modalidade": ModalidadeTrabalho.HIBRIDO,
        "localizacao": "São Paulo, SP",
    },
    {
        "id": "VAG-0002",
        "titulo": "Cientista de Dados",
        "area": "Ciência de Dados",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Oportunidade para atuar na construção de modelos estatísticos e soluções "
            "analíticas que apoiem decisões estratégicas de negócio."
        ),
        "responsabilidades": [
            "Explorar bases de dados e formular hipóteses analíticas",
            "Desenvolver modelos preditivos e algoritmos de classificação",
            "Apresentar insights para áreas de negócio",
            "Validar resultados e medir impacto das soluções",
        ],
        "requisitos_obrigatorios": [
            "Sólida estatística e probabilidade",
            "Experiência com Python e bibliotecas de Data Science",
            "Conhecimento em SQL e manipulação de grandes volumes",
            "Experiência com ciclo completo de projetos analíticos",
        ],
        "desejaveis": [
            "Experiência com séries temporais",
            "Conhecimento em experimentação A/B",
            "MBA ou pós-graduação em Analytics",
        ],
        "tecnologias": ["Python", "Pandas", "SQL", "Jupyter", "Statsmodels", "XGBoost"],
        "formacao_minima": "Graduação em Estatística, Matemática, Computação ou afins",
        "anos_minimos_experiencia": 3,
        "idiomas": ["Português fluente", "Inglês intermediário"],
        "modalidade": ModalidadeTrabalho.REMOTO,
        "localizacao": "Brasil (remoto)",
    },
    {
        "id": "VAG-0003",
        "titulo": "Engenheiro de Dados",
        "area": "Engenharia de Dados",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Profissional responsável por construir e manter pipelines de dados "
            "escaláveis, confiáveis e prontos para consumo analítico."
        ),
        "responsabilidades": [
            "Desenvolver pipelines ETL/ELT em ambientes cloud",
            "Modelar data lakes e data warehouses",
            "Garantir qualidade, observabilidade e performance dos dados",
            "Apoiar times de BI e ciência de dados com dados confiáveis",
        ],
        "requisitos_obrigatorios": [
            "Experiência com SQL avançado",
            "Conhecimento em pipelines de dados batch e streaming",
            "Vivência com cloud e boas práticas de engenharia",
            "Experiência com versionamento e CI/CD",
        ],
        "desejaveis": [
            "Certificação cloud (AWS, GCP ou Azure)",
            "Experiência com dbt ou ferramentas de transformação",
            "Conhecimento em Data Mesh ou arquiteturas modernas",
        ],
        "tecnologias": ["Python", "SQL", "Airflow", "Spark", "dbt", "AWS", "Kafka"],
        "formacao_minima": "Graduação em Engenharia, Computação ou áreas afins",
        "anos_minimos_experiencia": 3,
        "idiomas": ["Português fluente", "Inglês intermediário"],
        "modalidade": ModalidadeTrabalho.HIBRIDO,
        "localizacao": "Curitiba, PR",
    },
    {
        "id": "VAG-0004",
        "titulo": "Desenvolvedor Python",
        "area": "Desenvolvimento Python",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Vaga para desenvolver APIs, integrações e serviços backend em Python, "
            "participando de squads ágeis com foco em qualidade e entrega contínua."
        ),
        "responsabilidades": [
            "Implementar APIs REST e integrações entre sistemas",
            "Escrever testes automatizados e revisar código",
            "Participar de refinamentos técnicos e estimativas",
            "Manter documentação técnica atualizada",
        ],
        "requisitos_obrigatorios": [
            "Experiência sólida com Python",
            "Conhecimento em FastAPI ou Django",
            "Experiência com Git e metodologias ágeis",
            "Familiaridade com bancos relacionais",
        ],
        "desejaveis": [
            "Experiência com Redis ou filas de mensagens",
            "Conhecimento em Docker e Kubernetes",
            "Experiência com sistemas de alta disponibilidade",
        ],
        "tecnologias": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "pytest"],
        "formacao_minima": "Graduação em Computação, Sistemas ou experiência equivalente",
        "anos_minimos_experiencia": 3,
        "idiomas": ["Português fluente"],
        "modalidade": ModalidadeTrabalho.REMOTO,
        "localizacao": "Brasil (remoto)",
    },
    {
        "id": "VAG-0005",
        "titulo": "Analista de Recrutamento e Seleção",
        "area": "RH",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Atuação ponta a ponta em processos seletivos, employer branding e "
            "experiência do candidato para posições de tecnologia e corporativas."
        ),
        "responsabilidades": [
            "Conduzir processos seletivos do briefing à proposta",
            "Realizar entrevistas por competências e triagens",
            "Apoiar gestores na definição de perfis e job descriptions",
            "Acompanhar indicadores de recrutamento e time-to-hire",
        ],
        "requisitos_obrigatorios": [
            "Experiência em recrutamento volume ou hunting",
            "Conhecimento em técnicas de entrevista comportamental",
            "Domínio de ATS e LinkedIn Recruiter",
            "Boa comunicação escrita e verbal",
        ],
        "desejaveis": [
            "Experiência em recrutamento tech",
            "Conhecimento em people analytics",
            "Certificação em RH ou coaching",
        ],
        "tecnologias": ["LinkedIn Recruiter", "Gupy", "Excel", "Power BI"],
        "formacao_minima": "Graduação em Psicologia, Administração ou RH",
        "anos_minimos_experiencia": 2,
        "idiomas": ["Português fluente", "Inglês intermediário"],
        "modalidade": ModalidadeTrabalho.HIBRIDO,
        "localizacao": "Belo Horizonte, MG",
    },
    {
        "id": "VAG-0006",
        "titulo": "Analista de Compliance e Riscos",
        "area": "Compliance",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Responsável por monitorar conformidade regulatória, políticas internas "
            "e controles de risco operacional em ambiente corporativo."
        ),
        "responsabilidades": [
            "Mapear e monitorar riscos de compliance",
            "Elaborar relatórios e planos de ação corretiva",
            "Apoiar auditorias internas e externas",
            "Treinar áreas sobre normas e procedimentos",
        ],
        "requisitos_obrigatorios": [
            "Conhecimento em normas regulatórias e controles internos",
            "Experiência com análise de riscos e indicadores",
            "Capacidade de redigir políticas e procedimentos",
            "Atenção a detalhes e confidencialidade",
        ],
        "desejaveis": [
            "Certificação CRC, CEA ou similar",
            "Experiência em setor financeiro ou saúde",
            "Conhecimento em LGPD",
        ],
        "tecnologias": ["Excel", "Power BI", "SAP GRC", "SharePoint"],
        "formacao_minima": "Graduação em Direito, Administração, Contabilidade ou Economia",
        "anos_minimos_experiencia": 3,
        "idiomas": ["Português fluente", "Inglês intermediário"],
        "modalidade": ModalidadeTrabalho.PRESENCIAL,
        "localizacao": "Rio de Janeiro, RJ",
    },
    {
        "id": "VAG-0007",
        "titulo": "Analista de BI — Power BI",
        "area": "Power BI",
        "nivel": NivelExperiencia.JUNIOR,
        "descricao": (
            "Vaga para apoiar a construção de dashboards corporativos, modelagem "
            "semântica e automação de relatórios gerenciais."
        ),
        "responsabilidades": [
            "Desenvolver dashboards e relatórios no Power BI",
            "Tratar e modelar dados para camadas analíticas",
            "Atender demandas de áreas de negócio",
            "Documentar métricas e definições de KPIs",
        ],
        "requisitos_obrigatorios": [
            "Experiência com Power BI Desktop e Service",
            "Conhecimento em DAX e Power Query",
            "Domínio de SQL básico/intermediário",
            "Organização e foco em usabilidade dos painéis",
        ],
        "desejaveis": [
            "Certificação PL-300",
            "Experiência com SharePoint ou Dataverse",
            "Conhecimento em Python para automações",
        ],
        "tecnologias": ["Power BI", "DAX", "Power Query", "SQL", "Excel"],
        "formacao_minima": "Graduação em Administração, Sistemas, Estatística ou afins",
        "anos_minimos_experiencia": 1,
        "idiomas": ["Português fluente"],
        "modalidade": ModalidadeTrabalho.HIBRIDO,
        "localizacao": "Porto Alegre, RS",
    },
    {
        "id": "VAG-0008",
        "titulo": "Engenheiro de Automação de Processos",
        "area": "Automação",
        "nivel": NivelExperiencia.PLENO,
        "descricao": (
            "Profissional para automatizar fluxos operacionais e integrações entre "
            "sistemas, reduzindo esforço manual e aumentando eficiência."
        ),
        "responsabilidades": [
            "Mapear processos e identificar oportunidades de automação",
            "Desenvolver bots e scripts de integração",
            "Monitorar execuções e tratar exceções",
            "Documentar fluxos automatizados e SLAs",
        ],
        "requisitos_obrigatorios": [
            "Experiência com RPA ou automação de workflows",
            "Conhecimento em Python ou scripts de integração",
            "Capacidade de levantamento de processos (AS-IS / TO-BE)",
            "Experiência com APIs e tratamento de erros",
        ],
        "desejaveis": [
            "Experiência com UiPath, Power Automate ou n8n",
            "Conhecimento em filas e orquestração",
            "Background em BPM",
        ],
        "tecnologias": ["Python", "Power Automate", "APIs REST", "SQL", "Git"],
        "formacao_minima": "Graduação em Engenharia, Computação ou áreas afins",
        "anos_minimos_experiencia": 2,
        "idiomas": ["Português fluente"],
        "modalidade": ModalidadeTrabalho.HIBRIDO,
        "localizacao": "Campinas, SP",
    },
    {
        "id": "VAG-0009",
        "titulo": "Arquiteto Cloud",
        "area": "Cloud",
        "nivel": NivelExperiencia.SENIOR,
        "descricao": (
            "Liderança técnica na definição de arquiteturas cloud seguras, escaláveis "
            "e cost-effective para aplicações críticas do negócio."
        ),
        "responsabilidades": [
            "Desenhar arquiteturas multi-conta e multi-região",
            "Definir padrões de segurança, rede e observabilidade",
            "Apoiar migrações lift-and-shift e cloud native",
            "Mentorar engenheiros e revisar decisões técnicas",
        ],
        "requisitos_obrigatorios": [
            "Experiência com AWS, Azure ou GCP em produção",
            "Conhecimento em IaC (Terraform ou CloudFormation)",
            "Experiência com containers e orquestração",
            "Visão de FinOps e alta disponibilidade",
        ],
        "desejaveis": [
            "Certificações AWS Solutions Architect ou equivalente",
            "Experiência com Kubernetes em escala",
            "Conhecimento em Zero Trust e IAM avançado",
        ],
        "tecnologias": ["AWS", "Terraform", "Kubernetes", "Docker", "Prometheus", "CloudWatch"],
        "formacao_minima": "Graduação em Computação, Engenharia ou experiência equivalente",
        "anos_minimos_experiencia": 7,
        "idiomas": ["Português fluente", "Inglês avançado"],
        "modalidade": ModalidadeTrabalho.REMOTO,
        "localizacao": "Brasil (remoto)",
    },
    {
        "id": "VAG-0010",
        "titulo": "Analista de Dados",
        "area": "Análise de Dados",
        "nivel": NivelExperiencia.JUNIOR,
        "descricao": (
            "Atuar na coleta, limpeza e análise de dados para geração de insights "
            "operacionais e apoio à tomada de decisão."
        ),
        "responsabilidades": [
            "Extrair e consolidar dados de múltiplas fontes",
            "Criar relatórios e análises ad hoc",
            "Apoiar definição de indicadores e rotinas analíticas",
            "Garantir qualidade e consistência das bases utilizadas",
        ],
        "requisitos_obrigatorios": [
            "Conhecimento em SQL",
            "Experiência com Excel avançado",
            "Noções de estatística descritiva",
            "Capacidade de traduzir dados em narrativas simples",
        ],
        "desejaveis": [
            "Experiência com Python (Pandas)",
            "Conhecimento em Power BI ou Tableau",
            "Experiência em rotinas de reporting",
        ],
        "tecnologias": ["SQL", "Excel", "Power BI", "Python", "Google Sheets"],
        "formacao_minima": "Graduação em curso superior ou cursando último ano",
        "anos_minimos_experiencia": 0,
        "idiomas": ["Português fluente"],
        "modalidade": ModalidadeTrabalho.PRESENCIAL,
        "localizacao": "Salvador, BA",
    },
]


def gerar_vagas() -> list[Vaga]:
    """Retorna a lista de vagas fictícias pré-definidas."""
    posicoes_por_vaga = [3, 2, 2, 3, 2, 1, 2, 2, 1, 3]
    return [
        Vaga(**template, quantidade_posicoes=quantidade_posicoes)
        for template, quantidade_posicoes in zip(VAGAS_TEMPLATE, posicoes_por_vaga, strict=True)
    ]


def salvar_json_individual(vagas: list[Vaga], output_dir: Path | None = None) -> Path:
    """Salva cada vaga em um arquivo JSON separado."""
    output_dir = output_dir or VAGAS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    for vaga in vagas:
        arquivo = output_dir / f"{vaga.id.lower()}.json"
        arquivo.write_text(
            vaga.model_dump_json(indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return output_dir


def salvar_json_consolidado(vagas: list[Vaga], output_dir: Path | None = None) -> Path:
    """Salva todas as vagas em um único arquivo JSON."""
    output_dir = output_dir or VAGAS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    consolidado = [json.loads(v.model_dump_json()) for v in vagas]
    path = output_dir / "vagas_consolidado.json"
    path.write_text(json.dumps(consolidado, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def executar_geracao(output_dir: Path | None = None) -> dict:
    """Executa geração completa das vagas fictícias."""
    output_dir = output_dir or VAGAS_DIR
    vagas = gerar_vagas()
    json_dir = salvar_json_individual(vagas, output_dir)
    consolidado_path = salvar_json_consolidado(vagas, output_dir)

    resumo = {
        "total": len(vagas),
        "json_dir": str(json_dir),
        "consolidado_path": str(consolidado_path),
        "areas": [v.area for v in vagas],
        "niveis": {v.nivel.value: sum(1 for x in vagas if x.nivel == v.nivel) for v in vagas},
    }

    metadata_path = output_dir / "metadata.json"
    metadata_path.write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")

    return resumo


if __name__ == "__main__":
    resultado = executar_geracao()
    print(f"Geradas {resultado['total']} vagas fictícias.")
    print(f"JSONs em: {resultado['json_dir']}")
    print(f"Consolidado: {resultado['consolidado_path']}")
    print(f"Áreas: {', '.join(resultado['areas'])}")
