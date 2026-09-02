"""Dashboard Streamlit para consulta dos rankings e pareceres de recrutamento."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from config.settings import (
    IA_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    RESULTADOS_DIR,
    VAGAS_DIR,
)
from services.ingestao_curriculos import executar_ingestao
from services.database import garantir_banco_atualizado, listar_eventos_recentes, sincronizar_banco
from integrations.llm import criar_cliente_llm
from services.matching import executar_matching
from services.operacoes_dashboard import criar_vaga_pelo_dashboard, salvar_curriculos_enviados

CRITERIOS_SCORE = {
    "tecnologias": "Tecnologias",
    "requisitos": "Requisitos",
    "experiencia": "Experiência",
    "area": "Afinidade de área",
    "formacao": "Formação",
    "idiomas": "Idiomas",
    "desejaveis": "Diferenciais",
}


@st.cache_data
def carregar_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def arquivos_resultado() -> list[Path]:
    return sorted(RESULTADOS_DIR.glob("resultado_vag-*.json"))


def catalogo_vagas(arquivos: list[Path]) -> list[dict[str, Any]]:
    """Índice leve das vagas para busca e seleção no painel."""
    catalogo: list[dict[str, Any]] = []
    for path in arquivos:
        dados = carregar_json(str(path))
        vaga_path = VAGAS_DIR / f"{dados['vaga_id'].lower()}.json"
        dados_vaga = carregar_json(str(vaga_path)) if vaga_path.exists() else {}
        catalogo.append(
            {
                "id": dados["vaga_id"],
                "titulo": dados["vaga_titulo"],
                "area": dados.get("vaga_area", ""),
                "nivel": str(dados.get("vaga_nivel", "")).title(),
                "total": dados.get("total_candidatos", 0),
                "posicoes_disponiveis": int(dados_vaga.get("quantidade_posicoes", 1)),
                "path": path,
            }
        )
    return catalogo


def filtrar_vagas(catalogo: list[dict[str, Any]], busca: str) -> list[dict[str, Any]]:
    termo = busca.strip().lower()
    if not termo:
        return catalogo
    return [
        vaga
        for vaga in catalogo
        if termo in " ".join([vaga["id"], vaga["titulo"], vaga["area"], vaga["nivel"]]).lower()
    ]


def selecionar_secao(status_banco: dict[str, int]) -> str:
    """Exibe a navegação principal voltada à gestão do processo seletivo."""
    with st.sidebar:
        st.title("RH Inteligente")
        st.caption("Acompanhamento de recrutamento")
        st.badge("Banco SQLite conectado", icon=":material/database:", color="green")
        st.caption(f"{status_banco['candidatos']} perfis · {status_banco['vagas']} vagas")
        secao = st.radio(
            "Menu de acompanhamento",
            ["Visão executiva", "Acompanhamento de vagas", "Criar vagas", "Cadastrar candidatos"],
            key="secao_dashboard",
        )
        st.caption("Dados sensíveis permanecem no ambiente local.")
        return secao


def selecionar_vaga(catalogo: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Busca por título, área ou ID e escolhe a vaga no painel lateral."""
    with st.sidebar:
        st.title("Vagas")
        st.caption(f"{len(catalogo)} vaga(s) com ranking disponível")
        busca = st.text_input(
            "Buscar",
            placeholder="Título, área ou ID",
            help="Filtra a lista abaixo por título, área, nível ou código da vaga.",
        )
        filtradas = filtrar_vagas(catalogo, busca)
        if not filtradas:
            st.warning("Nenhuma vaga corresponde à busca.")
            return None

        ids = [vaga["id"] for vaga in filtradas]
        por_id = {vaga["id"]: vaga for vaga in filtradas}

        if "_ultima_vaga_notificada" not in st.session_state:
            st.session_state["_ultima_vaga_notificada"] = ids[0]

        vaga_id = st.selectbox(
            "Selecionar vaga",
            ids,
            format_func=lambda vid: f"{vid} · {por_id[vid]['titulo']}",
        )

        if st.session_state["_ultima_vaga_notificada"] != vaga_id:
            st.session_state["_ultima_vaga_notificada"] = vaga_id
            st.toast(
                f"Filtro aplicado para vaga: {por_id[vaga_id]['titulo']}",
                icon=":material/filter_alt:",
            )

        escolhida = por_id[vaga_id]
        st.markdown(f"**{escolhida['titulo']}**")
        st.caption(f"{escolhida['id']} · {escolhida['area']} · {escolhida['nivel']}")
        st.badge(f"{escolhida['total']} candidatos", icon=":material/group:", color="blue")
        return escolhida


def consolidar_visao_executiva(catalogo: list[dict[str, Any]]) -> pd.DataFrame:
    """Consolida indicadores por vaga sem expor dados pessoais de candidatos."""
    linhas = []
    for vaga in catalogo:
        resultado = carregar_json(str(vaga["path"]))
        ranking = resultado.get("ranking", [])
        melhor = ranking[0] if ranking else {}
        melhor_score = melhor.get("score_total")
        score = float(melhor_score or 0)
        if score >= 88:
            prontidao = "Pronto para decisão"
        elif score >= 70:
            prontidao = "Acompanhar"
        else:
            prontidao = "Revisar estratégia"
        linhas.append(
            {
                "Vaga": vaga["titulo"],
                "Área": vaga["area"],
                "Nível": vaga["nivel"],
                "Posições disponíveis": vaga["posicoes_disponiveis"],
                "Candidatos": len(ranking),
                "Score do líder": melhor_score,
                "Prontidão": prontidao,
            }
        )
    return pd.DataFrame(linhas)


def ir_para_acompanhamento_vagas() -> None:
    """Atualiza a navegação antes da próxima renderização do dashboard."""
    st.session_state["secao_dashboard"] = "Acompanhamento de vagas"


def renderizar_visao_executiva(catalogo: list[dict[str, Any]], status_banco: dict[str, int]) -> None:
    """Tela inicial para gestão: panorama e prioridades do recrutamento."""
    resumo = consolidar_visao_executiva(catalogo)
    total_perfis = status_banco["candidatos"]
    total_posicoes = int(resumo["Posições disponíveis"].sum()) if not resumo.empty else 0
    media_candidatos = resumo["Candidatos"].mean() if not resumo.empty else 0
    media_score_lideres = resumo["Score do líder"].mean() if not resumo.empty else 0
    prontas_decisao = (
        int((resumo["Prontidão"] == "Pronto para decisão").sum()) if not resumo.empty else 0
    )
    top_processos = resumo.nlargest(5, "Score do líder") if not resumo.empty else resumo

    with st.container(border=True):
        destaque, contexto = st.columns([4, 1], vertical_alignment="center")
        with destaque:
            st.title("Painel executivo", text_alignment="left")
            st.write("Uma leitura rápida do portfólio para orientar prioridades de recrutamento.")
            st.caption("Ranking comparável, critérios explícitos e decisão final sempre humana.")
        with contexto:
            st.badge("Base sincronizada", icon=":material/database:", color="green")
            st.caption(f"{status_banco['vagas']} processos ativos")
            st.button(
                "Ver vagas",
                icon=":material/arrow_forward:",
                width="stretch",
                on_click=ir_para_acompanhamento_vagas,
            )

    st.space("small")

    with st.container(horizontal=True):
        st.metric("Processos ativos", len(catalogo), border=True)
        st.metric("Posições disponíveis", total_posicoes, border=True)
        st.metric("Talentos na base", total_perfis, border=True)
        st.metric("Cobertura média", f"{media_candidatos:.0f} perfis/vaga", border=True)
        st.metric(
            "Aderência média dos líderes",
            f"{media_score_lideres:.1f}" if not resumo.empty else "—",
            border=True,
        )

    st.space("small")
    prioridades, distribuicao = st.columns([3, 2], gap="medium")
    with prioridades:
        with st.container(border=True):
            st.subheader("Prioridades para decisão")
            st.caption("Vagas com a maior aderência já disponível no ranking.")
            st.dataframe(
                top_processos[
                    ["Vaga", "Área", "Posições disponíveis", "Candidatos", "Score do líder", "Prontidão"]
                ],
                hide_index=True,
                width="stretch",
                height=260,
                column_config={
                    "Vaga": st.column_config.TextColumn(pinned=True, width="large"),
                    "Candidatos": st.column_config.NumberColumn(format="%d", width="small"),
                    "Posições disponíveis": st.column_config.NumberColumn(format="%d", width="small"),
                    "Score do líder": st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=100,
                        format="%.1f",
                    ),
                },
            )
    with distribuicao:
        with st.container(border=True):
            st.subheader("Leitura do portfólio")
            st.metric("Prontas para decisão", prontas_decisao, border=True)
            st.caption("Processos cujo perfil líder atingiu aderência de 88 pontos ou mais.")
            distribuicao_prontidao = (
                resumo.groupby("Prontidão", as_index=False).size().rename(columns={"size": "Vagas"})
            )
            st.bar_chart(
                distribuicao_prontidao,
                x="Prontidão",
                y="Vagas",
                horizontal=True,
                height=180,
                color="primary",
            )

    st.space("small")
    with st.container(border=True):
        st.subheader("Radar do portfólio")
        st.caption("Acompanhe volume, aderência e situação de cada processo seletivo.")
        st.dataframe(
            resumo[
                [
                    "Vaga",
                    "Área",
                    "Nível",
                    "Posições disponíveis",
                    "Candidatos",
                    "Score do líder",
                    "Prontidão",
                ]
            ],
            hide_index=True,
            width="stretch",
            height=380,
            column_config={
                "Vaga": st.column_config.TextColumn(pinned=True, width="large"),
                "Candidatos": st.column_config.NumberColumn(format="%d", width="small"),
                "Posições disponíveis": st.column_config.NumberColumn(format="%d", width="small"),
                "Score do líder": st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=100,
                    format="%.1f",
                ),
            },
        )


def carregar_pareceres(vaga_id: str) -> dict[str, Any]:
    path = RESULTADOS_DIR / f"analise_{vaga_id.lower()}.json"
    return carregar_json(str(path)).get("analises", {}) if path.exists() else {}


@st.cache_data
def carregar_perfis_candidatos() -> dict[str, dict[str, Any]]:
    """Carrega os perfis para a aba Top 10 sem expor dados de contato."""
    from services.loader import carregar_candidatos

    campos_publicos = {
        "id",
        "nome",
        "nivel",
        "area",
        "cargo_desejado",
        "resumo",
        "anos_experiencia",
        "formacao",
        "experiencias",
        "habilidades",
        "certificacoes",
        "idiomas",
    }
    return {
        candidato.id: {
            chave: valor
            for chave, valor in candidato.model_dump(mode="json").items()
            if chave in campos_publicos
        }
        for candidato in carregar_candidatos()
    }


def tabela_ranking(ranking: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Posição": item["posicao"],
                "Candidato": item["nome"],
                "Score": item["score_total"],
                "Nível": item["nivel"].title(),
                "Área": item["area"].title(),
                "Experiência (anos)": item["anos_experiencia"],
                "Principais lacunas": ", ".join(item["skills_faltantes"]) or "—",
            }
            for item in ranking
        ]
    )


def badges_lista(itens: list[str], cor: str) -> str:
    if not itens:
        return "Nenhum item listado."
    partes = []
    for item in itens:
        rotulo = str(item).replace("[", "(").replace("]", ")")
        partes.append(f":{cor}-badge[{rotulo}]")
    return " ".join(partes)


def renderizar_parecer(parecer: dict[str, Any]) -> None:
    st.subheader("Direcionamento para o recrutador")
    st.caption("Leitura gerada por IA para apoiar a entrevista. A decisão continua sob revisão humana.")
    st.write(parecer["resumo"])
    colunas = st.columns(2)
    with colunas[0]:
        with st.container(border=True):
            st.markdown("**Pontos fortes**")
            for item in parecer["pontos_fortes"]:
                st.markdown(f"- {item}")
            st.markdown("**Pontos a investigar na entrevista**")
            for item in parecer["lacunas"]:
                st.markdown(f"- {item}")
    with colunas[1]:
        with st.container(border=True):
            st.markdown("**Roteiro de entrevista**")
            for pergunta in parecer["perguntas_entrevista"]:
                st.markdown(f"- {pergunta}")
            st.markdown("**Potencial de desenvolvimento**")
            st.write(parecer["potencial_desenvolvimento"])
    recomendacao = parecer["recomendacao"].replace("_", " ")
    st.badge(f"Recomendação: {recomendacao}", icon=":material/recommend:", color="green")


def executar_fluxo_local() -> None:
    """Processa os arquivos recebidos e atualiza rankings sem enviar dados à IA."""
    with st.spinner("Processando currículos e atualizando o ranking..."):
        gerados, avisos = executar_ingestao()
        resumo = executar_matching(top=30)
        sincronizar_banco()
    carregar_json.clear()
    carregar_perfis_candidatos.clear()
    st.success(
        f"Fluxo concluído: {len(gerados)} currículo(s) extraído(s) e "
        f"{resumo['vagas_processadas']} vaga(s) ranqueada(s)."
    )
    for aviso in avisos:
        st.warning(aviso)


def executar_pareceres(
    vaga_id: str,
    provider: str,
    model: str,
    top: int,
    base_url: str | None = None,
) -> None:
    """Gera pareceres apenas após uma ação explícita do usuário."""
    from services.analise import executar_analises

    with st.spinner(f"Gerando {top} parecer(es) de IA. Isso pode levar alguns minutos no Ollama local..."):
        paths = executar_analises(
            vaga_id=vaga_id,
            top=top,
            provider=provider,
            model=model,
            base_url=base_url,
        )
    carregar_json.clear()
    st.success(
        f"Parecer(es) gerado(s) para os {top} primeiros candidatos da vaga. "
        "Atualize a seleção para visualizá-los."
    )


def renderizar_composicao_score(candidato: dict[str, Any]) -> None:
    """Exibe a aderência com métrica e barras nativas."""
    with st.container(border=True):
        cabecalho, total = st.columns([3, 1], vertical_alignment="center")
        with cabecalho:
            st.subheader("Composição do score")
            st.caption("Critérios objetivos utilizados no ranking")
        with total:
            st.metric("Score total", f"{candidato['score_total']:.0f}", border=True)

        for chave, valor in candidato["breakdown"].items():
            percentual = max(0, min(100, float(valor)))
            st.progress(percentual / 100, text=f"{CRITERIOS_SCORE[chave]}  ·  {percentual:.0f}%")


def separar_itens(texto: str) -> list[str]:
    """Converte campos de formulário separados por linha ou vírgula em listas limpas."""
    return [item.strip() for item in texto.replace("\n", ",").split(",") if item.strip()]


def renderizar_historico_operacional() -> None:
    """Exibe ações recentes sem mostrar o conteúdo de dados pessoais."""
    st.subheader("Rastreabilidade recente")
    eventos = listar_eventos_recentes()
    if eventos:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Quando": evento["criado_em"].replace("T", " "),
                        "Ação": evento["tipo"].replace("_", " ").capitalize(),
                        "Referência": evento["referencia"],
                    }
                    for evento in eventos
                ]
            ),
            hide_index=True,
            width="stretch",
            height=240,
        )
    else:
        st.caption("Nenhuma ação registrada ainda.")


def renderizar_cadastro_candidatos() -> None:
    """Centraliza o recebimento local de currículos fora do painel executivo."""
    st.title("Cadastrar candidatos")
    st.write("Receba currículos e processe-os localmente para compor a base de talentos.")
    with st.container(border=True):
        st.subheader("Receber currículos")
        st.caption("Os arquivos são processados no ambiente local. PDFs precisam conter texto selecionável.")
        with st.form("enviar_curriculos", clear_on_submit=True):
            arquivos = st.file_uploader(
                "Currículos recebidos",
                type=["pdf", "docx", "txt", "md", "json"],
                accept_multiple_files=True,
                max_upload_size=15,
            )
            enviar = st.form_submit_button(
                "Enviar e processar currículos", icon=":material/upload_file:", width="stretch"
            )
        if enviar:
            if not arquivos:
                st.warning("Selecione ao menos um currículo para continuar.")
            else:
                salvos, avisos_upload = salvar_curriculos_enviados(arquivos)
                gerados, avisos_ingestao = executar_ingestao()
                sincronizar_banco()
                carregar_json.clear()
                carregar_perfis_candidatos.clear()
                for aviso in [*avisos_upload, *avisos_ingestao]:
                    st.warning(aviso)
                if salvos:
                    st.success(f"{len(salvos)} currículo(s) recebido(s) e {len(gerados)} arquivo(s) extraído(s).")
                st.caption("Nenhum currículo é enviado à IA nesta etapa; revise os perfis antes de usá-los no ranking.")

    with st.container(border=True):
        renderizar_historico_operacional()


def _preencher_formulario_vaga(rascunho: dict[str, Any]) -> None:
    """Preenche o formulário manual com um rascunho que permanece editável."""
    campos_lista = ["responsabilidades", "requisitos_obrigatorios", "desejaveis", "tecnologias", "idiomas"]
    for campo, valor in rascunho.items():
        chave = f"vaga_{campo}"
        st.session_state[chave] = ", ".join(valor) if campo in campos_lista else valor


def renderizar_criacao_vagas() -> None:
    """Separa criação de vagas do painel, com apoio opcional e revisável de IA."""
    st.title("Criar vagas")
    st.write("Crie uma vaga manualmente ou gere um rascunho com IA para revisar antes de publicar.")
    modo = st.segmented_control(
        "Como começar", ["Assistida por IA", "Manual"], default="Assistida por IA", selection_mode="single"
    )

    if modo == "Assistida por IA":
        with st.container(border=True):
            st.subheader("Gerar rascunho com IA")
            st.caption("A IA propõe o conteúdo; a publicação só acontece depois da sua revisão no formulário abaixo.")
            provider_opcoes = {"Ollama (local)": "ollama", "OpenAI": "openai"}
            provider_label = st.selectbox("Provedor", list(provider_opcoes), key="vaga_provider")
            provider = provider_opcoes[provider_label]
            modelo = st.text_input(
                "Modelo", value=OLLAMA_MODEL if provider == "ollama" else OPENAI_MODEL, key=f"vaga_modelo_{provider}"
            )
            servidor = None
            if provider == "ollama":
                servidor = st.text_input("Servidor Ollama", value=OLLAMA_BASE_URL, key="vaga_servidor_ollama")
            with st.form("gerar_rascunho_vaga", border=False):
                necessidade = st.text_area(
                    "Descreva a necessidade", placeholder="Ex.: Pessoa para analisar dados agrícolas e criar painéis para operações."
                )
                nivel_ia = st.segmented_control("Nível", ["junior", "pleno", "senior"], default="pleno")
                gerar = st.form_submit_button("Gerar rascunho para revisão", icon=":material/auto_awesome:")
            if gerar:
                if not necessidade.strip():
                    st.warning("Descreva a necessidade da vaga para gerar o rascunho.")
                else:
                    try:
                        rascunho = criar_cliente_llm(provider, modelo, servidor).gerar_rascunho_vaga(necessidade, nivel_ia)
                        _preencher_formulario_vaga(rascunho.model_dump())
                        st.session_state["vaga_nivel"] = nivel_ia
                        st.success("Rascunho gerado. Revise e ajuste os campos antes de criar a vaga.")
                    except Exception as exc:
                        st.error(f"Não foi possível gerar o rascunho: {exc}")

    with st.container(border=True):
        st.subheader("Revisar e criar vaga")
        st.caption("Todos os campos abaixo são editáveis. O ranking será atualizado após a criação.")
        with st.form("criar_vaga", clear_on_submit=False):
            titulo = st.text_input("Título da vaga", placeholder="Ex.: Analista de dados", key="vaga_titulo")
            descricao = st.text_area("Descrição", placeholder="Objetivo e escopo da oportunidade", key="vaga_descricao")
            primeira_linha, segunda_linha = st.columns(2, gap="medium")
            with primeira_linha:
                area = st.text_input("Área", placeholder="Ex.: Dados", key="vaga_area")
                nivel = st.selectbox("Nível", ["junior", "pleno", "senior"], format_func=str.title, key="vaga_nivel")
                modalidade = st.selectbox(
                    "Modalidade", ["remoto", "hibrido", "presencial"], format_func=str.title, key="vaga_modalidade"
                )
                localizacao = st.text_input("Localização", placeholder="Ex.: São Paulo, SP", key="vaga_localizacao")
            with segunda_linha:
                quantidade_posicoes = st.number_input("Posições disponíveis", min_value=1, value=1, step=1, key="vaga_quantidade_posicoes")
                anos_experiencia = st.number_input("Experiência mínima (anos)", min_value=0, value=0, step=1, key="vaga_anos_minimos_experiencia")
                formacao_minima = st.text_input("Formação mínima", placeholder="Ex.: Graduação em áreas correlatas", key="vaga_formacao_minima")
                idiomas = st.text_input("Idiomas", placeholder="Ex.: Português fluente, Inglês intermediário", key="vaga_idiomas")
            responsabilidades = st.text_area("Responsabilidades", placeholder="Uma responsabilidade por linha ou separada por vírgulas", key="vaga_responsabilidades")
            requisitos = st.text_area("Requisitos obrigatórios", placeholder="Um requisito por linha ou separado por vírgulas", key="vaga_requisitos_obrigatorios")
            tecnologias = st.text_area("Tecnologias", placeholder="Ex.: Python, SQL, Power BI", key="vaga_tecnologias")
            desejaveis = st.text_area("Diferenciais desejáveis", placeholder="Opcional: um item por linha ou separado por vírgulas", key="vaga_desejaveis")
            criar = st.form_submit_button(
                "Criar vaga e atualizar ranking",
                type="primary",
                icon=":material/playlist_add_check:",
                width="stretch",
            )
        if criar:
            listas_obrigatorias = {
                "Responsabilidades": separar_itens(responsabilidades),
                "Requisitos obrigatórios": separar_itens(requisitos),
                "Tecnologias": separar_itens(tecnologias),
            }
            campos_obrigatorios = [titulo, descricao, area, localizacao, formacao_minima, idiomas]
            if not all(campo.strip() for campo in campos_obrigatorios) or not all(listas_obrigatorias.values()):
                st.error("Preencha todos os campos obrigatórios e informe ao menos um item em cada lista requerida.")
            else:
                vaga, _ = criar_vaga_pelo_dashboard(
                    {
                        "titulo": titulo.strip(),
                        "area": area.strip(),
                        "nivel": nivel,
                        "descricao": descricao.strip(),
                        "responsabilidades": listas_obrigatorias["Responsabilidades"],
                        "requisitos_obrigatorios": listas_obrigatorias["Requisitos obrigatórios"],
                        "desejaveis": separar_itens(desejaveis),
                        "tecnologias": listas_obrigatorias["Tecnologias"],
                        "formacao_minima": formacao_minima.strip(),
                        "anos_minimos_experiencia": int(anos_experiencia),
                        "idiomas": separar_itens(idiomas),
                        "modalidade": modalidade,
                        "localizacao": localizacao.strip(),
                        "quantidade_posicoes": int(quantidade_posicoes),
                    }
                )
                resumo = executar_matching(top=30)
                sincronizar_banco()
                carregar_json.clear()
                carregar_perfis_candidatos.clear()
                st.success(
                    f"{vaga.id} criada e ranking atualizado para {resumo['vagas_processadas']} vaga(s)."
                )
                st.session_state["secao_dashboard"] = "Acompanhamento de vagas"
                st.rerun()


def renderizar_acoes(vaga_id: str) -> None:
    acoes, ia = st.columns(2, gap="medium")
    with acoes:
        with st.container(border=True):
            st.markdown("**Atualizar base**")
            st.caption("Lê a pasta `curriculos/` e atualiza os rankings sem chamadas de IA.")
            if st.button(
                "Processar currículos",
                type="primary",
                icon=":material/sync:",
                width="stretch",
            ):
                executar_fluxo_local()
    with ia:
        with st.container(border=True):
            st.markdown("**Gerar pareceres**")
            st.caption("Cria pareceres para o top 10 usando Ollama local ou OpenAI.")
            opcoes_provider = {"Ollama (local)": "ollama", "OpenAI": "openai"}
            indice_padrao = 0 if IA_PROVIDER == "ollama" else 1
            provider_label = st.selectbox(
                "Provedor de IA",
                list(opcoes_provider),
                index=indice_padrao,
                key="provider_ia",
            )
            provider = opcoes_provider[provider_label]
            model = st.text_input(
                "Modelo",
                value=OLLAMA_MODEL if provider == "ollama" else OPENAI_MODEL,
                key=f"modelo_{provider}",
                help="No Ollama, use o nome de um modelo que já tenha sido baixado localmente.",
            )
            base_url = None
            if provider == "ollama":
                base_url = st.text_input(
                    "Servidor Ollama",
                    value=OLLAMA_BASE_URL,
                    key="servidor_ollama",
                )
            quantidade_pareceres = st.selectbox(
                "Quantidade de pareceres",
                [1, 3, 5, 10],
                index=0,
                format_func=lambda quantidade: f"Top {quantidade}",
                help="Para uma demonstração local, comece com Top 1. Cada parecer é gerado separadamente.",
            )
            if st.button(
                "Gerar pareceres",
                icon=":material/psychology:",
                width="stretch",
            ):
                try:
                    executar_pareceres(vaga_id, provider, model, quantidade_pareceres, base_url)
                except Exception as exc:
                    st.error(f"Não foi possível gerar os pareceres: {exc}")


def renderizar_visao_vaga(resultado: dict[str, Any], vaga: dict[str, Any], ranking: list[dict[str, Any]]) -> None:
    st.header(resultado["vaga_titulo"])
    total_na_vaga = len(ranking)
    rotulo_candidatos = "candidato" if total_na_vaga == 1 else "candidatos"
    with st.container(horizontal=True):
        st.badge(resultado["vaga_area"], icon=":material/work:", color="blue")
        st.badge(resultado["vaga_nivel"].title(), icon=":material/signal_cellular_alt:", color="violet")
        st.badge(
            f"{total_na_vaga} {rotulo_candidatos} para esta vaga",
            icon=":material/groups:",
            color="gray",
        )

    with st.container(horizontal=True):
        st.metric(
            "Melhor score",
            f"{ranking[0]['score_total']:.1f}" if ranking else "—",
            border=True,
        )
        st.metric("Candidatos exibidos", len(ranking), border=True)
        st.metric(
            "Experiência mínima",
            f"{vaga.get('anos_minimos_experiencia', '—')} anos",
            border=True,
        )

    with st.expander("Requisitos e contexto da vaga", expanded=True):
        st.write(vaga.get("descricao", "Descrição não disponível."))
        col_req, col_tec = st.columns(2)
        with col_req:
            st.markdown("**Obrigatórios**")
            st.markdown(badges_lista(vaga.get("requisitos_obrigatorios", []), "orange"))
        with col_tec:
            st.markdown("**Tecnologias**")
            st.markdown(badges_lista(vaga.get("tecnologias", []), "blue"))


def renderizar_ranking(ranking: list[dict[str, Any]]) -> None:
    st.subheader("Ranking de candidatos")
    st.caption("A posição é definida pelos mesmos critérios para todos os perfis.")
    st.dataframe(
        tabela_ranking(ranking),
        hide_index=True,
        width="stretch",
        height=420,
        column_config={
            "Posição": st.column_config.NumberColumn(format="%d", width="small"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
            "Experiência (anos)": st.column_config.NumberColumn(format="%d"),
        },
    )


def renderizar_candidato(resultado: dict[str, Any], ranking: list[dict[str, Any]]) -> None:
    if not ranking:
        st.info("Nenhum candidato no ranking desta vaga.")
        return

    por_opcao = {f"#{item['posicao']} · {item['nome']} ({item['candidato_id']})": item for item in ranking}
    escolha = st.selectbox("Analisar candidato", list(por_opcao))
    candidato = por_opcao[escolha]
    parecer = carregar_pareceres(resultado["vaga_id"]).get(candidato["candidato_id"])

    if not parecer:
        return

    st.subheader(candidato["nome"])
    with st.container(horizontal=True):
        st.badge(f"Score {candidato['score_total']:.1f}", icon=":material/analytics:", color="green")
        st.badge(candidato["nivel"].title(), color="violet")
        st.badge(candidato["area"].title(), color="blue")
        st.badge(f"{candidato['anos_experiencia']} anos de experiência", color="gray")

    colunas = st.columns(2, gap="medium")
    with colunas[0]:
        with st.container(border=True):
            st.markdown("**Competências atendidas**")
            st.markdown(badges_lista(candidato["skills_atendidas"], "green"))
            st.markdown("**Requisitos atendidos**")
            st.markdown(badges_lista(candidato["requisitos_atendidos"], "blue"))
    with colunas[1]:
        with st.container(border=True):
            st.markdown("**Competências a validar**")
            st.markdown(badges_lista(candidato["skills_faltantes"], "orange"))
            st.markdown("**Requisitos pendentes**")
            st.markdown(badges_lista(candidato["requisitos_pendentes"], "red"))

    renderizar_composicao_score(candidato)
    renderizar_parecer(parecer)


def renderizar_faixa_do_ranking(
    ranking: list[dict[str, Any]],
    titulo: str,
    descricao: str,
    mensagem_vazia: str,
) -> None:
    """Exibe uma lista operacional de candidatos de uma faixa do ranking."""
    st.subheader(titulo)
    st.caption(descricao)
    if not ranking:
        st.info(mensagem_vazia)
        return

    st.dataframe(
        tabela_ranking(ranking),
        hide_index=True,
        width="stretch",
        height=340,
        column_config={
            "Posição": st.column_config.NumberColumn(format="%d", width="small"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f"),
            "Experiência (anos)": st.column_config.NumberColumn(format="%d"),
        },
    )


def renderizar_top_10(ranking: list[dict[str, Any]]) -> None:
    """Mostra um resumo comparável dos dez perfis mais bem posicionados."""
    st.subheader("Top 10 candidatos")
    st.caption("Os perfis abaixo são exibidos sem dados de contato e seguem a ordem do ranking.")
    perfis = carregar_perfis_candidatos()

    for candidato_ranking in ranking[:10]:
        perfil = perfis.get(candidato_ranking["candidato_id"])
        with st.container(border=True):
            cabecalho, score = st.columns([5, 1], vertical_alignment="center")
            with cabecalho:
                st.markdown(f"**#{candidato_ranking['posicao']} · {candidato_ranking['nome']}**")
                st.caption(
                    f"{candidato_ranking['cargo_desejado']} · "
                    f"{candidato_ranking['nivel'].title()} · "
                    f"{candidato_ranking['anos_experiencia']} anos de experiência"
                )
            with score:
                st.metric("Score", f"{candidato_ranking['score_total']:.1f}")

            if not perfil:
                st.info("A descrição deste perfil não está disponível na base de currículos.")
                continue

            st.write(perfil["resumo"])
            st.markdown("**Competências**")
            st.markdown(badges_lista(perfil.get("habilidades", []), "blue"))

            with st.expander("Ver formação, idiomas e experiências"):
                formacoes = perfil.get("formacao", [])
                if formacoes:
                    st.markdown("**Formação**")
                    for formacao in formacoes:
                        ano = f" · {formacao['ano_conclusao']}" if formacao.get("ano_conclusao") else ""
                        st.markdown(
                            f"- {formacao['curso']} · {formacao['instituicao']} "
                            f"({formacao['nivel']}{ano})"
                        )
                if perfil.get("idiomas"):
                    st.markdown("**Idiomas**")
                    st.markdown(badges_lista(perfil["idiomas"], "violet"))
                if perfil.get("certificacoes"):
                    st.markdown("**Certificações**")
                    st.markdown(badges_lista(perfil["certificacoes"], "green"))
                if perfil.get("experiencias"):
                    st.markdown("**Experiências profissionais**")
                    for experiencia in perfil["experiencias"]:
                        periodo = f"{experiencia['inicio']} a {experiencia.get('fim') or 'atual'}"
                        st.markdown(
                            f"- **{experiencia['cargo']} · {experiencia['empresa']}** ({periodo})  \n"
                            f"  {experiencia['descricao']}"
                        )


def main() -> None:
    st.set_page_config(
        page_title="RH Inteligente",
        page_icon=":material/groups:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    status_banco = garantir_banco_atualizado()
    secao = selecionar_secao(status_banco)
    if secao == "Criar vagas":
        renderizar_criacao_vagas()
        return
    if secao == "Cadastrar candidatos":
        renderizar_cadastro_candidatos()
        return

    arquivos = arquivos_resultado()
    if not arquivos:
        st.info("Nenhum ranking encontrado ainda. Envie currículos e crie uma vaga acima, ou gere um ranking pelo terminal.")
        st.code("python -m services.matching --top 30", language="powershell")
        return

    catalogo = catalogo_vagas(arquivos)
    if secao == "Visão executiva":
        renderizar_visao_executiva(catalogo, status_banco)
        return

    escolhida = selecionar_vaga(catalogo)
    if escolhida is None:
        return

    resultado = carregar_json(str(escolhida["path"]))
    vaga_path = VAGAS_DIR / f"{resultado['vaga_id'].lower()}.json"
    vaga = carregar_json(str(vaga_path)) if vaga_path.exists() else {}
    ranking = resultado["ranking"]

    renderizar_acoes(resultado["vaga_id"])

    visao, ranking_tab, top_10_tab, analise, talentos, nao_avancaram = st.tabs(
        [
            "Visão da vaga",
            "Ranking",
            "Top 10 candidatos",
            "Candidato",
            "Banco de talentos",
            "Não avançaram",
        ]
    )
    with visao:
        renderizar_visao_vaga(resultado, vaga, ranking)
    with ranking_tab:
        renderizar_ranking(ranking)
    with top_10_tab:
        renderizar_top_10(ranking)
    with analise:
        renderizar_candidato(resultado, ranking)
    with talentos:
        renderizar_faixa_do_ranking(
            [item for item in ranking if 11 <= item["posicao"] <= 15],
            "Banco de talentos",
            "Perfis entre as posições 11 e 15 para reaproveitamento em futuras oportunidades.",
            "Não há candidatos nesta faixa para esta vaga.",
        )
    with nao_avancaram:
        renderizar_faixa_do_ranking(
            [item for item in ranking if item["posicao"] >= 16],
            "Não avançaram nesta vaga",
            "Perfis não priorizados para este processo específico. Revise antes de qualquer comunicação ao candidato.",
            "Não há candidatos nesta faixa para esta vaga.",
        )


if __name__ == "__main__":
    main()
