# Documentação de Arquitetura

> Evolui a cada etapa. O MVP avança em módulos pequenos e executáveis.

## Visão Geral

O sistema segue uma arquitetura em camadas com separação clara entre domínio, aplicação e infraestrutura. A IA não substitui o scoring determinístico: o motor de comparação (Etapa 4) produz notas auditáveis; o LLM (Etapas 5 e 6) interpreta semanticamente o match, explica o ranking, aponta lacunas, sugere perguntas de entrevista e comenta potencial de desenvolvimento.

## Decisões de Design (MVP)

- **Persistência local** — arquivos JSON/CSV em `data/` para simplicidade
- **Scoring primeiro, LLM depois** — ranking reproduzível mesmo sem API; a IA enriquece o parecer
- **LLM via API** — OpenAI como provedor inicial, abstraído em `integrations/`; a saída é JSON estruturado validado por Pydantic
- **Privacidade mínima** — o contexto enviado para a IA exclui e-mail, telefone e localização do candidato
- **Dashboard Streamlit** — prototipagem rápida da interface
- **Pydantic** — validação de dados em todas as fronteiras

## Roadmap de referência

1. Arquitetura → 2. Currículos → 3. Vagas → 4. Motor de comparação → 5. Integração LLM ✅ → 6. Análise inteligente ✅ → 7. Dashboard → 8. Testes e refinamento

## Próximos Documentos

- `docs/PROMPTS.md` — Etapa 5
- `docs/ANALISE.md` — Etapa 6
- `docs/DASHBOARD.md` — Etapa 7
