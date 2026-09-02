from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "documentacao_rh_inteligente.pdf"
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#147D92")
TEAL = colors.HexColor("#0F9D8A")
MIST = colors.HexColor("#EDF6F7")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
LINE = colors.HexColor("#D9E2EC")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=30, leading=35, textColor=colors.white, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["BodyText"], fontName="Helvetica", fontSize=13, leading=19, textColor=colors.HexColor("#D9F1F0"), spaceAfter=18))
styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=NAVY, spaceAfter=12))
styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=15, textColor=INK, spaceAfter=8))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=15, textColor=NAVY, backColor=MIST, borderColor=colors.HexColor("#B9E2E0"), borderWidth=0.5, borderPadding=11, spaceBefore=8, spaceAfter=12))
styles.add(ParagraphStyle(name="CodeCustom", parent=styles["BodyText"], fontName="Courier", fontSize=8.5, leading=13, textColor=INK, backColor=colors.HexColor("#F6F8FA"), borderColor=LINE, borderWidth=0.5, borderPadding=9, spaceBefore=6, spaceAfter=10))


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def bullet(text):
    return p(f"<b>-</b> {text}")


def standard_table(rows, widths, header=True):
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), MIST))
    return Table(rows, colWidths=widths, style=TableStyle(commands))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(1.8 * cm, 1.35 * cm, A4[0] - 1.8 * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.8 * cm, 0.85 * cm, "RH Inteligente | Documentacao do MVP")
    canvas.drawRightString(A4[0] - 1.8 * cm, 0.85 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.circle(A4[0] - 1.3 * cm, A4[1] - 1.8 * cm, 4.7 * cm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.circle(A4[0] - 0.5 * cm, A4[1] - 3.0 * cm, 2.7 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#D9F1F0"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(2.0 * cm, A4[1] - 2.4 * cm, "DOCUMENTACAO DO APLICATIVO")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(2.0 * cm, 2.0 * cm, "MVP para apresentacao | Agosto de 2026")
    canvas.restoreState()


def build_pdf():
    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover), PageTemplate(id="main", frames=[frame], onPage=footer)])
    story = []

    story.extend([Spacer(1, 5.8 * cm), p("RH Inteligente", "CoverTitle"), p("Agente de apoio ao recrutamento e selecao", "CoverSub"), Spacer(1, 0.5 * cm), p("Um MVP que transforma curriculos e requisitos de vagas em rankings auditaveis e pareceres de apoio a entrevista.", "CoverSub"), Spacer(1, 1.0 * cm)])
    story.append(Table([[p("<b>Proposta</b><br/>Apoiar o time de RH com criterios claros e evidencias rastreaveis.", "Small"), p("<b>Escopo</b><br/>Dados sinteticos, matching, IA opcional e dashboard.", "Small")]], colWidths=[7.2 * cm, 7.2 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBE8E8")), ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12)])))
    story.append(PageBreak())
    doc.handle_nextPageTemplate("main")

    story.extend([p("1. Visao geral", "H1"), p("O RH Inteligente e um MVP para demonstrar como uma equipe de recrutamento pode organizar uma triagem inicial de forma consistente. Ele compara os dados de candidatos e vagas, apresenta o ranking com a composicao da nota e gera um parecer opcional para orientar a entrevista."), p("O produto foi pensado como apoio a decisao. Nenhuma pessoa deve ser contratada, excluida ou avaliada somente com base no resultado da aplicacao.", "Callout"), p("Objetivos", "H2"), bullet("Reduzir o esforco operacional de leitura e comparacao de curriculos."), bullet("Tornar os criterios de aderencia visiveis e reproduziveis."), bullet("Apontar evidencias, lacunas e perguntas de validacao."), bullet("Oferecer uma demonstracao visual para times de RH e liderancas."), p("Entregas do MVP", "H2")])
    story.append(standard_table([[p("<b>Modulo</b>", "Small"), p("<b>Entrega</b>", "Small")], [p("Dados", "Small"), p("300 curriculos sinteticos e 10 vagas ficticias.", "Small")], [p("Matching", "Small"), p("Ranking por score e detalhamento de evidencias.", "Small")], [p("IA opcional", "Small"), p("Resumo, lacunas, perguntas e recomendacao para entrevista.", "Small")], [p("Dashboard", "Small"), p("Consulta de vagas, ranking e pareceres em Streamlit.", "Small")]], [3.2 * cm, 11.2 * cm]))
    story.append(PageBreak())

    story.extend([p("2. Como a solucao funciona", "H1"), p("O fluxo separa o calculo auditavel da interpretacao por IA. Assim, mesmo sem chave de API, a demonstracao do ranking continua funcional.")])
    story.append(standard_table([[p("<b>1. Entrada</b><br/>Curriculos e vagas em JSON/CSV.", "Small"), p("<b>2. Scoring</b><br/>Criterios e pesos explicitos.", "Small")], [p("<b>3. Ranking</b><br/>Posicao, score e lacunas.", "Small"), p("<b>4. IA opcional</b><br/>Parecer para apoiar a entrevista.", "Small")], [p("<b>5. Dashboard</b><br/>Visualizacao para a pessoa recrutadora.", "Small"), p("<b>6. Revisao humana</b><br/>Decisao final e responsabilidade do RH.", "Small")]], [7.2 * cm, 7.2 * cm], header=False))
    story.append(p("Composicao do score", "H2"))
    story.append(standard_table([[p("<b>Criterio</b>", "Small"), p("<b>Peso</b>", "Small"), p("<b>O que e observado</b>", "Small")], [p("Tecnologias", "Small"), p("30%", "Small"), p("Habilidades e termos equivalentes evidenciados no perfil.", "Small")], [p("Requisitos", "Small"), p("20%", "Small"), p("Cobertura dos requisitos obrigatorios da vaga.", "Small")], [p("Experiencia", "Small"), p("20%", "Small"), p("Anos de experiencia e nivel de senioridade.", "Small")], [p("Area", "Small"), p("15%", "Small"), p("Proximidade entre area do candidato e area da vaga.", "Small")], [p("Formacao, idiomas e desejaveis", "Small"), p("15%", "Small"), p("Criterios complementares de aderencia.", "Small")]], [5.0 * cm, 2.0 * cm, 7.4 * cm]))
    story.append(PageBreak())

    story.extend([p("3. Interface e demonstracao", "H1"), p("O dashboard em Streamlit e a interface de apresentacao do MVP. Ele consome os rankings ja processados, portanto pode ser demonstrado sem custo de chamada a IA."), p("O que mostrar", "H2"), bullet("Selecao de uma vaga na barra lateral e leitura dos requisitos."), bullet("Ranking com posicao, score, nivel, area, experiencia e lacunas principais."), bullet("Detalhamento de um candidato: competencias atendidas, requisitos pendentes e grafico da composicao do score."), bullet("Parecer de IA, quando gerado: pontos fortes, lacunas, perguntas e potencial de desenvolvimento."), p("Roteiro sugerido - 5 minutos", "H2")])
    story.append(standard_table([[p("<b>Minuto 1</b>", "Small"), p("Apresente o problema da triagem e a proposta de apoio ao RH.", "Small")], [p("<b>Minutos 2-3</b>", "Small"), p("Selecione uma vaga e explore o ranking com os criterios transparentes.", "Small")], [p("<b>Minuto 4</b>", "Small"), p("Abra um candidato e explique as evidencias e lacunas.", "Small")], [p("<b>Minuto 5</b>", "Small"), p("Mostre o parecer e reforce a revisao humana e as proximas evolucoes.", "Small")]], [3.0 * cm, 11.4 * cm], header=False))
    story.extend([p("Execucao", "H2"), p("python -m venv .venv<br/>.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt<br/>.\\.venv\\Scripts\\python.exe -m services.matching --top 30<br/>.\\.venv\\Scripts\\python.exe -m streamlit run dashboard/app.py", "CodeCustom"), PageBreak()])

    story.extend([p("4. IA, privacidade e proximos passos", "H1"), p("A integracao com a OpenAI recebe apenas dados relevantes ao parecer. O contexto exclui e-mail, telefone e localizacao. O modelo deve se limitar as evidencias fornecidas e nao pode alterar o score deterministico."), p("Principios do MVP", "H2"), bullet("Dados de demonstracao: os curriculos e vagas do repositorio sao sinteticos."), bullet("Minimizacao: contatos e localizacao nao seguem para a camada de IA."), bullet("Explicabilidade: o ranking tem composicao de score, habilidades atendidas e lacunas."), bullet("Supervisao: a recomendacao de IA serve para orientar a conversa, nunca para decidir sozinha."), p("Limites e evolucoes necessarias", "H2"), bullet("Validar criterios e pesos com recrutadores e gestao de pessoas."), bullet("Avaliar vieses, conformidade com LGPD e controles de seguranca antes de dados reais."), bullet("Adicionar upload de curriculos, criacao de vagas, filtros e comparacao lado a lado."), bullet("Incluir autenticacao, perfis de acesso, trilha de auditoria e integracao com ATS."), p("Mensagem final", "H2"), p("O RH Inteligente demonstra uma base funcional para uma triagem mais organizada e explicavel. O valor do produto esta em combinar automacao de baixo risco com julgamento humano, preservando transparencia em cada recomendacao.", "Callout"), PageBreak(), p("5. Opcoes de IA e automacao", "H1"), p("O dashboard agora possui dois controles: Processar curriculos e atualizar ranking executa somente operacoes locais; Gerar pareceres desta vaga usa a IA de forma explicita. A separacao evita custo inesperado e torna o fluxo mais seguro."), p("API de nuvem com custo", "H2"), bullet("Usa a API da OpenAI para gerar pareceres estruturados; requer OPENAI_API_KEY no arquivo .env."), bullet("A cobranca e por uso, conforme modelo e volume de entrada e saida. Consulte a tabela atual em platform.openai.com/pricing antes de definir um orcamento."), bullet("Vantagens: configuracao simples, modelos gerenciados e boa qualidade. Pontos de atencao: custo variavel, conectividade e governanca de dados."), p("IA local sem custo por chamada", "H2"), bullet("E possivel usar um runtime local como Ollama no Windows. O modelo e baixado e responde pela API local em http://localhost:11434."), bullet("Depois do download, nao ha custo de API por chamada; permanecem os custos de maquina, energia, espaco em disco e manutencao."), bullet("Vantagens: maior controle e possibilidade de operar sem internet. Pontos de atencao: qualidade e velocidade dependem do modelo e do hardware."), p("Proxima evolucao recomendada", "H2"), p("Criar um adaptador LocalLLM ao lado de ClienteLLM, com uma variavel IA_PROVIDER=ollama ou openai. Assim, o mesmo parecer pode ser gerado localmente ou por API paga, sem alterar o motor de ranking.", "Callout"), p("Referencias: docs.ollama.com/windows | platform.openai.com/pricing", "Small")])
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
