from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "Manual_RH_Inteligente.pdf"
NAVY, BLUE, MIST, INK, MUTED, LINE = (colors.HexColor(x) for x in ("#102A43", "#147D92", "#EDF6F7", "#243B53", "#627D98", "#D9E2EC"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ManualTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=32, leading=38, textColor=colors.white, spaceAfter=14))
styles.add(ParagraphStyle(name="Sub", parent=styles["BodyText"], fontName="Helvetica", fontSize=13, leading=19, textColor=colors.HexColor("#D9F1F0")))
styles.add(ParagraphStyle(name="H1Manual", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=NAVY, spaceAfter=12))
styles.add(ParagraphStyle(name="H2Manual", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyManual", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=15, textColor=INK, spaceAfter=8))
styles.add(ParagraphStyle(name="SmallManual", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=MUTED))
styles.add(ParagraphStyle(name="CodeManual", parent=styles["BodyText"], fontName="Courier", fontSize=8.4, leading=13, textColor=INK, backColor=colors.HexColor("#F6F8FA"), borderColor=LINE, borderWidth=0.5, borderPadding=9, spaceBefore=6, spaceAfter=10))
styles.add(ParagraphStyle(name="NoteManual", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=15, textColor=NAVY, backColor=MIST, borderColor=colors.HexColor("#B9E2E0"), borderWidth=0.5, borderPadding=10, spaceBefore=7, spaceAfter=11))


def p(text, style="BodyManual"):
    return Paragraph(text, styles[style])


def step(number, title, body):
    return Table([[p(f"<b>{number}</b>", "SmallManual"), p(f"<b>{title}</b><br/>{body}", "SmallManual")]], colWidths=[1.0 * cm, 13.4 * cm], style=TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), MIST), ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(1.8 * cm, 1.35 * cm, A4[0] - 1.8 * cm, 1.35 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.8 * cm, 0.85 * cm, "Manual | RH Inteligente")
    canvas.drawRightString(A4[0] - 1.8 * cm, 0.85 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.circle(A4[0] - 0.8 * cm, A4[1] - 1.0 * cm, 4.7 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#D9F1F0"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(2.0 * cm, A4[1] - 2.4 * cm, "RH INTELIGENTE")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(2.0 * cm, 2.0 * cm, "Guia de instalacao e operacao | Agosto de 2026")
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=cover), PageTemplate(id="main", frames=[frame], onPage=footer)])
    s = []
    s.extend([Spacer(1, 6.1 * cm), p("Manual", "ManualTitle"), p("Como preparar, executar e demonstrar o RH Inteligente", "Sub"), Spacer(1, 1.2 * cm), p("Este guia explica toda a estrutura do projeto e o caminho completo: dados, ranking, ingestao de curriculos, IA e dashboard.", "Sub"), PageBreak()])
    doc.handle_nextPageTemplate("main")

    s.extend([p("1. Antes de comecar", "H1Manual"), p("O projeto deve ser executado no PowerShell, a partir da pasta raiz abaixo."), p('C:\\Users\\DVipe\\OneDrive\\Area de Trabalho\\Projeto RH', "CodeManual"), p("Voce precisa de Python 3.11 ou superior. Para conferir se ele esta instalado, abra um novo PowerShell e execute:", "BodyManual"), p("python --version", "CodeManual"), p("Se esse comando abrir a Microsoft Store ou der erro, instale o Python 3.11+ e marque a opcao para adiciona-lo ao PATH. Feche e abra o PowerShell novamente antes de continuar.", "NoteManual")])
    s.extend([p("Preparar o ambiente", "H2Manual"), step("1", "Entrar na pasta", 'Execute <font name="Courier">cd "C:\\Users\\DVipe\\OneDrive\\Area de Trabalho\\Projeto RH"</font>.'), step("2", "Criar ambiente virtual", "Execute o comando abaixo apenas uma vez por maquina."), p("python -m venv .venv", "CodeManual"), step("3", "Instalar dependencias", "Instala Streamlit, OpenAI, leitores de PDF/DOCX e ferramentas de teste."), p(".\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt", "CodeManual")])
    s.append(PageBreak())

    s.extend([p("2. Estrutura do projeto", "H1Manual"), p("Cada pasta tem uma responsabilidade definida. Trabalhe sempre a partir da raiz do projeto."), p("Projeto RH/<br/>|- curriculos/ - pasta de entrada para PDFs, DOCX, TXT e JSON recebidos<br/>|- data/ - dados sinteticos, resultados e curriculos extraidos<br/>|- generators/ - criacao de dados ficticios para demonstracao<br/>|- models/ - contratos e validacoes de dados<br/>|- services/ - matching, scoring, ingestao e analise<br/>|- integrations/ - cliente da OpenAI<br/>|- prompts/ - instrucoes do parecer de IA<br/>|- dashboard/ - tela Streamlit para o recrutador<br/>|- tests/ - testes automatizados<br/>|- docs/ - documentacao tecnica", "CodeManual"), p("Arquivos de configuracao", "H2Manual"), p("<b>requirements.txt</b> lista as bibliotecas. <b>.env</b> guarda a chave da OpenAI e nao deve ser compartilhado. <b>.env.example</b> e o modelo seguro para criar seu .env. <b>README.md</b> contem o resumo e roteiro de apresentacao."), p("Pastas com dados reais", "H2Manual"), p("Coloque curriculos recebidos em <b>curriculos/</b>. Os JSONs brutos extraidos sao salvos em <b>data/curriculos_processados/</b>. Esses dois locais sao ignorados pelo Git para evitar publicar dados pessoais.", "NoteManual")])
    s.append(PageBreak())

    s.extend([p("3. Executar o fluxo sem IA", "H1Manual"), p("Este e o caminho ideal para a primeira demonstracao. Ele nao exige chave de API e usa apenas os dados sinteticos que ja existem no projeto."), p("Gerar curriculos e vagas de demonstracao", "H2Manual"), p(".\\.venv\\Scripts\\python.exe -m generators.curriculos<br/>.\\.venv\\Scripts\\python.exe -m generators.gerar_vagas", "CodeManual"), p("Calcular o ranking", "H2Manual"), p(".\\.venv\\Scripts\\python.exe -m services.matching --top 30", "CodeManual"), p("O resultado fica em <b>data/resultados/</b>: um JSON por vaga, CSV consolidado e metadados. Para executar somente uma vaga, use:", "BodyManual"), p(".\\.venv\\Scripts\\python.exe -m services.matching --vaga VAG-0001 --top 30", "CodeManual"), p("Abrir o dashboard", "H2Manual"), p(".\\.venv\\Scripts\\python.exe -m streamlit run dashboard/app.py", "CodeManual"), p("O navegador abre, normalmente, em <b>http://localhost:8501</b>. Escolha uma vaga, consulte o ranking e abra um candidato para ver a composicao do score, competencias e lacunas.", "NoteManual")])
    s.append(PageBreak())

    s.extend([p("4. Receber curriculos em arquivos", "H1Manual"), p("A ingestao converte arquivos recebidos em JSON bruto local, preservando rastreabilidade. Ela nao envia curriculos para IA e ainda nao inclui o candidato automaticamente no ranking."), step("1", "Copiar os arquivos", "Coloque PDF, DOCX, TXT, Markdown ou JSON na pasta curriculos/."), step("2", "Executar a ingestao", "O comando processa todos os arquivos suportados da pasta."), p(".\\.venv\\Scripts\\python.exe -m services.ingestao_curriculos", "CodeManual"), step("3", "Conferir a saida", "Abra data/curriculos_processados/. Cada JSON inclui o texto extraido, hash SHA-256, formato, data e metadados."), p("Importante: PDF digitalizado como imagem nao possui texto para extracao e precisa passar por OCR. Arquivos antigos .doc devem ser convertidos para DOCX ou PDF. Para uso real, a proxima etapa e normalizar e validar as informacoes com revisao humana e regras de LGPD.", "NoteManual")])
    s.append(PageBreak())

    s.extend([p("5. Rodar a IA para gerar pareceres", "H1Manual"), p("A IA e opcional. O ranking continua deterministico e a IA apenas produz um parecer para os melhores candidatos: resumo, pontos fortes, lacunas, perguntas de entrevista, potencial e recomendacao."), p("Configurar a chave", "H2Manual"), p("Copy-Item .env.example .env<br/>notepad .env", "CodeManual"), p("No arquivo .env, substitua o valor de exemplo pela chave do seu projeto OpenAI:", "BodyManual"), p("OPENAI_API_KEY=sua_chave_aqui<br/>OPENAI_MODEL=gpt-5-mini", "CodeManual"), p("Gerar pareceres", "H2Manual"), p(".\\.venv\\Scripts\\python.exe -m services.analise --vaga VAG-0001 --top 10", "CodeManual"), p("O arquivo e salvo como <b>data/resultados/analise_vag-0001.json</b>. Atualize o dashboard aberto para ver os pareceres dos candidatos analisados.", "BodyManual"), p("Privacidade: o contexto da IA exclui e-mail, telefone e localizacao. Nao use dados reais sem base legal, processo de consentimento, controles de acesso e revisao humana. A chave nunca deve ser adicionada ao Git.", "NoteManual")])
    s.append(PageBreak())

    s.extend([p("6. Ordem recomendada e solucao de problemas", "H1Manual"), p("Checklist de demonstracao", "H2Manual"), step("1", "Ambiente", "Criar .venv e instalar as dependencias."), step("2", "Dados", "Gerar curriculos, vagas e ranking."), step("3", "Interface", "Executar Streamlit e abrir localhost:8501."), step("4", "IA opcional", "Configurar .env e gerar pareceres para uma vaga."), step("5", "Curriculos reais", "Usar curriculos/ e rodar a ingestao local."), p("Problemas comuns", "H2Manual")])
    troubleshooting = [[p("<b>Sintoma</b>", "SmallManual"), p("<b>Como resolver</b>", "SmallManual")], [p("python nao e reconhecido", "SmallManual"), p("Instale Python 3.11+ e reinicie o PowerShell. Confirme com python --version.", "SmallManual")], [p("Modulo nao encontrado", "SmallManual"), p("Rode novamente .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt.", "SmallManual")], [p("Dashboard nao abre", "SmallManual"), p("Confirme que o comando Streamlit continua rodando e abra http://localhost:8501.", "SmallManual")], [p("IA retorna erro de chave", "SmallManual"), p("Confira OPENAI_API_KEY no .env e se a conta possui acesso ao modelo configurado.", "SmallManual")], [p("PDF nao extrai texto", "SmallManual"), p("Use OCR antes da ingestao ou envie uma versao do PDF com texto selecionavel.", "SmallManual")]]
    s.append(Table(troubleshooting, colWidths=[4.4 * cm, 10.0 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), MIST), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])))
    s.extend([p("Regra principal", "H2Manual"), p("Use o sistema como apoio a recrutadores. O score e o parecer devem ser interpretados por pessoas; ausencia de evidencia no curriculo nao prova ausencia de competencia.", "NoteManual"), PageBreak(), p("7. Escolher entre IA local e API paga", "H1Manual"), p("O projeto atual usa a API da OpenAI para gerar pareceres. Tambem e possivel adicionar uma IA local para evitar custo por chamada. O ranking e sempre local e deterministico; apenas o parecer de linguagem muda de provedor."), p("Acoes por botao no dashboard", "H2Manual"), step("A", "Processar curriculos e atualizar ranking", "Executa apenas localmente: processa a pasta curriculos/ e recalcula os rankings. Nao chama IA."), step("B", "Gerar pareceres desta vaga", "Chama a IA somente para os 10 primeiros candidatos da vaga selecionada. Esta acao deve ser feita de forma consciente, pois a API de nuvem pode ter custo."), p("Opcao 1 - API OpenAI com custo", "H2Manual"), p("1. Crie o .env com Copy-Item .env.example .env.<br/>2. Informe OPENAI_API_KEY e, se desejado, OPENAI_MODEL.<br/>3. No dashboard, clique em Gerar pareceres desta vaga.", "CodeManual"), p("A cobranca depende do modelo e do total de tokens processados. Antes de uso em escala, consulte a pagina oficial de precos em platform.openai.com/pricing e estabeleca limite de orcamento. A API e mais simples de operar, mas exige conectividade e controles de dados.", "NoteManual"), p("Opcao 2 - IA local com Ollama", "H2Manual"), p("1. Instale o Ollama para Windows pelo site oficial docs.ollama.com/windows.<br/>2. No PowerShell, baixe e teste um modelo: ollama run llama3.2.<br/>3. O Ollama mantem uma API local em http://localhost:11434.<br/>4. Na proxima implementacao, configure IA_PROVIDER=ollama para o projeto usar esse endereco local.", "CodeManual"), p("A IA local nao cobra por chamada depois que o modelo foi baixado, mas usa RAM, CPU ou GPU, espaco em disco e energia. Modelos menores sao mais leves, mas podem produzir pareceres menos consistentes. Para curriculos reais, teste a qualidade e revise sempre as saidas.", "NoteManual"), p("Comparacao rapida", "H2Manual")])
    s.append(Table([[p("<b>Opcao</b>", "SmallManual"), p("<b>Quando usar</b>", "SmallManual"), p("<b>Principal custo</b>", "SmallManual")], [p("OpenAI API", "SmallManual"), p("Prototipo rapido e melhor qualidade gerenciada.", "SmallManual"), p("Uso por tokens.", "SmallManual")], [p("Ollama local", "SmallManual"), p("Privacidade, testes locais e alto volume previsivel.", "SmallManual"), p("Hardware, energia e manutencao.", "SmallManual")]], colWidths=[3.3 * cm, 7.0 * cm, 4.1 * cm], style=TableStyle([("BACKGROUND", (0, 0), (-1, 0), MIST), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])))
    doc.build(s)


if __name__ == "__main__":
    build()
