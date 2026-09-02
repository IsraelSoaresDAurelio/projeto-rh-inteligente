"""Pools de dados para geração sintética de currículos."""

NOMES = [
    "Ana Silva", "Bruno Costa", "Carla Mendes", "Diego Alves", "Elena Rocha",
    "Felipe Nunes", "Gabriela Lima", "Henrique Souza", "Isabela Ferreira", "João Pedro",
    "Karina Dias", "Lucas Martins", "Mariana Teixeira", "Nicolas Barbosa", "Olivia Campos",
    "Paulo Henrique", "Raquel Pires", "Samuel Gomes", "Tatiana Ribeiro", "Vinicius Cardoso",
    "Amanda Castro", "Bernardo Lopes", "Camila Freitas", "Daniel Monteiro", "Elisa Moura",
    "Fabio Rezende", "Giovana Prado", "Hugo Azevedo", "Ingrid Cavalcanti", "Julio Cesar",
    "Larissa Duarte", "Marcelo Farias", "Natália Borges", "Otavio Peixoto", "Patricia Melo",
    "Rafael Torres", "Sabrina Vieira", "Thiago Ramos", "Ursula Nascimento", "Victor Araujo",
    "Wesley Cunha", "Yasmin Correia", "Adriano Pinto", "Bianca Santana", "Caio Moreira",
    "Debora Machado", "Eduardo Batista", "Flavia Coelho", "Guilherme Paiva", "Helena Queiroz",
]

SOBRENOMES = [
    "Oliveira", "Santos", "Pereira", "Carvalho", "Rodrigues", "Almeida", "Nascimento",
    "Lima", "Araujo", "Fernandes", "Gomes", "Ribeiro", "Martins", "Barbosa", "Rocha",
]

CIDADES = [
    ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Belo Horizonte", "MG"),
    ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Brasília", "DF"), ("Salvador", "BA"),
    ("Recife", "PE"), ("Fortaleza", "CE"), ("Campinas", "SP"), ("Florianópolis", "SC"),
    ("Goiânia", "GO"), ("Manaus", "AM"), ("Vitória", "ES"), ("Natal", "RN"),
]

EMPRESAS = [
    "TechNova", "InovaCorp", "DataPrime", "CloudSystems", "AgileWorks",
    "GlobalTech", "NextLevel", "SmartSolutions", "BlueOcean", "VertexGroup",
    "Alpha Consulting", "Beta Digital", "Gamma Labs", "Delta Engenharia", "Omega RH",
    "Prime Analytics", "SyncHub", "CoreBusiness", "Nexus IT", "Pulse Software",
]

INSTITUICOES = [
    "USP", "UNICAMP", "UFMG", "PUC-SP", "UFPR", "UFRJ", "UNESP", "UFSC",
    "FGV", "Insper", "FIAP", "Senac", "Senai", "Estácio", "Anhanguera",
]

AREA_CONFIG = {
    "tech": {
        "cargos": {
            "junior": ["Desenvolvedor Junior", "Analista de Sistemas Junior", "Suporte Tecnico Pleno"],
            "pleno": ["Desenvolvedor Pleno", "Engenheiro de Software", "DevOps Engineer"],
            "senior": ["Desenvolvedor Senior", "Tech Lead", "Arquiteto de Software"],
        },
        "habilidades_base": [
            "Python", "Java", "JavaScript", "Git", "SQL", "Docker", "REST API",
            "HTML/CSS", "React", "Node.js", "AWS", "Linux", "Scrum", "TypeScript",
        ],
        "cursos": ["Ciência da Computação", "Análise e Desenvolvimento de Sistemas", "Engenharia de Software"],
        "certificacoes": ["AWS Certified Developer", "Scrum Foundation", "Oracle Java SE"],
    },
    "engenharia": {
        "cargos": {
            "junior": ["Engenheiro Junior", "Assistente de Engenharia", "Estagiario de Projetos"],
            "pleno": ["Engenheiro de Projetos", "Engenheiro de Processos", "Engenheiro de Qualidade"],
            "senior": ["Engenheiro Senior", "Coordenador de Engenharia", "Gerente de Projetos"],
        },
        "habilidades_base": [
            "AutoCAD", "SolidWorks", "Gestão de Projetos", "Lean Manufacturing",
            "Six Sigma", "NR-12", "Manutenção Industrial", "P&ID", "SAP PM",
            "Controle de Qualidade", "Orçamento de Obras", "Normas ABNT",
        ],
        "cursos": ["Engenharia Mecânica", "Engenharia Civil", "Engenharia de Produção", "Engenharia Elétrica"],
        "certificacoes": ["PMP", "Green Belt Six Sigma", "CREA Regularizado"],
    },
    "rh": {
        "cargos": {
            "junior": ["Assistente de RH", "Analista de RH Junior", "Auxiliar de Departamento Pessoal"],
            "pleno": ["Analista de RH Pleno", "Business Partner Jr", "Analista de Recrutamento"],
            "senior": ["Coordenador de RH", "Gerente de RH", "HR Business Partner"],
        },
        "habilidades_base": [
            "Recrutamento e Seleção", "Departamento Pessoal", "CLT", "eSocial",
            "Treinamento e Desenvolvimento", "Cargos e Salários", "Employer Branding",
            "Entrevista por Competências", "Onboarding", "Gestão de Desempenho",
        ],
        "cursos": ["Psicologia", "Administração de Empresas", "Gestão de RH", "Ciências Contábeis"],
        "certificacoes": ["SHRM-CP", "Certificação GPTW", "People Analytics"],
    },
    "administracao": {
        "cargos": {
            "junior": ["Assistente Administrativo", "Analista Administrativo Junior", "Auxiliar Financeiro"],
            "pleno": ["Analista Administrativo Pleno", "Controller Junior", "Analista Financeiro"],
            "senior": ["Gerente Administrativo", "Controller", "Coordenador Financeiro"],
        },
        "habilidades_base": [
            "Excel Avançado", "Power BI", "Contas a Pagar/Receber", "Fluxo de Caixa",
            "Orçamento", "SAP", "Protheus", "Gestão de Contratos", "Compras",
            "Atendimento ao Cliente", "Organização de Processos",
        ],
        "cursos": ["Administração de Empresas", "Ciências Contábeis", "Gestão Financeira", "Processos Gerenciais"],
        "certificacoes": ["CRC", "Certificação Excel Expert", "Gestão Financeira FGV"],
    },
    "dados": {
        "cargos": {
            "junior": ["Analista de Dados Junior", "Estagiario de BI", "Analista de BI Junior"],
            "pleno": ["Cientista de Dados Pleno", "Analista de BI Pleno", "Engenheiro de Dados Junior"],
            "senior": ["Cientista de Dados Senior", "Engenheiro de Dados", "Head de Analytics"],
        },
        "habilidades_base": [
            "Python", "SQL", "Power BI", "Tableau", "Pandas", "Machine Learning",
            "ETL", "Apache Spark", "dbt", "Statistics", "Data Warehousing",
            "Google BigQuery", "Airflow", "Visualização de Dados",
        ],
        "cursos": ["Ciência de Dados", "Estatística", "Engenharia da Computação", "Análise de Sistemas"],
        "certificacoes": ["Google Data Analytics", "Databricks Associate", "Microsoft PL-300"],
    },
}

NIVEL_ANOS = {"junior": (0, 2), "pleno": (3, 6), "senior": (7, 15)}
NIVEL_QTD_EXP = {"junior": (1, 2), "pleno": (2, 4), "senior": (4, 6)}
NIVEL_QTD_HAB = {"junior": (5, 8), "pleno": (7, 11), "senior": (10, 14)}

RESUMOS = {
    "tech": {
        "junior": "Profissional em início de carreira com sólida base técnica e vontade de aprender.",
        "pleno": "Desenvolvedor com experiência em entrega de soluções e trabalho em equipe ágil.",
        "senior": "Profissional experiente em arquitetura, liderança técnica e mentoria de times.",
    },
    "engenharia": {
        "junior": "Engenheiro recém-formado com foco em projetos e melhoria contínua.",
        "pleno": "Engenheiro com histórico em gestão de projetos e otimização de processos.",
        "senior": "Engenheiro sênior com expertise em liderança de projetos complexos e equipes.",
    },
    "rh": {
        "junior": "Profissional de RH com foco em recrutamento, admissão e rotinas de DP.",
        "pleno": "Analista de RH com experiência em T&D, recrutamento e gestão de talentos.",
        "senior": "Líder de RH com visão estratégica de people management e cultura organizacional.",
    },
    "administracao": {
        "junior": "Profissional administrativo organizado, com foco em rotinas e controles.",
        "pleno": "Analista administrativo/financeiro com experiência em indicadores e processos.",
        "senior": "Gestor administrativo com histórico em controladoria e eficiência operacional.",
    },
    "dados": {
        "junior": "Analista de dados iniciante com foco em SQL, dashboards e análises descritivas.",
        "pleno": "Profissional de dados com experiência em modelagem, BI e pipelines analíticos.",
        "senior": "Especialista sênior em analytics, ML e estratégia orientada a dados.",
    },
}

IDIOMAS_OPCOES = [
    ["Português (nativo)"],
    ["Português (nativo)", "Inglês (intermediário)"],
    ["Português (nativo)", "Inglês (avançado)"],
    ["Português (nativo)", "Inglês (intermediário)", "Espanhol (básico)"],
    ["Português (nativo)", "Inglês (fluente)", "Espanhol (intermediário)"],
]
