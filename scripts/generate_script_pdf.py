"""Generador del PDF del Guión Técnico del Video (3 Minutos) con interpretación de gráficas."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

ROOT = Path.cwd()
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = DOCS_DIR / "GUION_VIDEO_PRESENTACION_UNILLANOS.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(54, 32, "Universidad de los Llanos · Proyecto CRISP-DM · Análisis de Comentarios")
        self.drawRightString(612 - 54, 32, f"Página {self._pageNumber} de {page_count}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 44, 612 - 54, 44)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        "MetaText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#4A5568")
    )
    block_title_style = ParagraphStyle(
        "BlockTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=10,
        spaceAfter=6
    )
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    script_style = ParagraphStyle(
        "ScriptStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A202C")
    )
    interpret_style = ParagraphStyle(
        "InterpretStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#742A2A")
    )

    story = []

    # Encabezado
    story.append(Paragraph("Guión Técnico y de Locución para Presentación de Proyecto", title_style))
    story.append(Paragraph("Análisis Descriptivo de Comentarios Institucionales de la Universidad de los Llanos", subtitle_style))
    story.append(Paragraph("<b>Duración estimada:</b> Máximo 3 minutos (180 s) &nbsp;|&nbsp; <b>Autores:</b> Juan Camilo Londoño Velásquez y Juan David Burgos Atuesta", meta_style))
    story.append(Paragraph("<b>Metodología:</b> CRISP-DM &nbsp;|&nbsp; <b>Corpus analizado:</b> 15.885 comentarios (Facebook, Instagram, YouTube)", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1A365D"), spaceAfter=12))

    # Bloques del guión
    blocks = [
        {
            "num": "BLOQUE 1",
            "time": "0:00 – 0:30 (30 seg)",
            "title": "Introducción, Alcance y Métricas Generales",
            "screen": "Abrir la aplicación en la pestaña <b>Resumen</b>. Mostrar la barra lateral de filtros (Facebook, Instagram, YouTube) y las 4 tarjetas de métricas superiores (15.885 comentarios analizados).",
            "voice": '"Hola a todos. En este proyecto desarrollamos un marco de análisis descriptivo bajo el estándar CRISP-DM para auditar y comprender la conversación digital en las cuentas institucionales de la Universidad de los Llanos en Facebook, Instagram y YouTube. Recopilamos 16.471 registros que, tras una estricta auditoría de calidad y remoción de filas sin texto, consolidaron un corpus de 15.885 comentarios analizables. La aplicación que observan permite explorar tres dimensiones articuladas: las temáticas institucionales, la polaridad de sentimiento y las emociones expresadas por la comunidad."',
            "interpretation": "<b>Lectura clave de la gráfica de plataformas:</b> Facebook concentra el 72,6% del volumen (11.529 comentarios), mientras Instagram aporta el 26,0% y YouTube el 1,4%. Esto refleja que los conteos no deben compararse como tasas de éxito o alcance relativo, sino como el nivel de actividad capturado en cada canal."
        },
        {
            "num": "BLOQUE 2",
            "time": "0:30 – 1:15 (45 seg)",
            "title": "Taxonomía Temática y Desarticulación del Residual",
            "screen": "Pasar a la pestaña <b>Temas</b>. Resaltar la gráfica horizontal con porcentajes por tema y la gráfica de pastel de macro-categorías (Temas específicos: 40,2%, Otros residual: 34,6%, Sin contenido: 25,2%). Hacer hover sobre <i>Protesta y movilización</i> y <i>Felicitaciones</i>.",
            "voice": '"Estructuramos una taxonomía de reglas léxicas compiladas con límites de palabra (\\b) y orden de precedencia fija, congelada formalmente mediante hash SHA-256 antes de la evaluación. A diferencia de enfoques clásicos donde el residual absorbe dos tercios del corpus, nuestra estrategia aisló un 25,2% de mensajes sin contenido proposicional (solo emojis o saludos) y elevó la cobertura de temas específicos al 40,2%. Sobresale la incorporación de Protesta y movilización en primer orden con 603 comentarios, corrigiendo 467 falsos positivos que antes caían erróneamente en temas académicos."',
            "interpretation": "<b>Interpretación analítica de las gráficas:</b><br/>"
                              "• <i>Instagram vs. Facebook:</i> En Instagram, el 41,4% de los comentarios es 'Sin contenido suficiente' (comunidad altamente visual que reacciona con emojis o menciones limpias). En contraste, Facebook concentra el 98,3% de toda la protesta estudiantil (#hambredeeducacion), operando como el ágora de debate político.<br/>"
                              "• <i>Residual genuino:</i> El 34,6% en 'Otros' representa un residual sustantivo real: preguntas atípicas y reflexiones que no caben en un catálogo cerrado."
        },
        {
            "num": "BLOQUE 3",
            "time": "1:15 – 1:55 (40 seg)",
            "title": "Sentimiento por Tema y Advertencia Metodológica",
            "screen": "Pasar a <b>Sentimiento por tema</b>. Seleccionar en el menú <i>Protesta y movilización</i> (mostrar la dona con 22,7% negativo y 75% neutral) y luego <i>Felicitaciones y aprecio</i> (mostrar 82,5% positivo). Bajar al gráfico de barras apiladas al 100% que compara todas las áreas temáticas.",
            "voice": '"Procesamos el afecto con modelos RoBERTuito preentrenados en español. Al cruzar temática con sentimiento surgen hallazgos cruciales: mientras Protesta exhibe un 22,7% negativo y 75% neutro por consignas informativas, Felicitaciones alcanza un 82,5% de positividad. Sin embargo, aplicamos un principio de honestidad científica: la categoría de felicitaciones se define por palabras de elogio que el modelo asocia de inmediato con polaridad positiva. Por tanto, parte sustancial de esa correlación es por diseño de construcción de la regla y no un descubrimiento empírico independiente."',
            "interpretation": "<b>Interpretación de la barra apilada 100%:</b> Permite diagnosticar la 'temperatura afectiva' de cada área. <i>Admisiones e inscripciones</i> presenta una alta tasa de fricción negativa (25,8%), revelando inquietudes y reclamos sobre fechas y cupos. En cambio, <i>Oferta académica</i> muestra un balance constructivo (38,6% positivo frente a 25,9% negativo), donde las dudas curriculares conviven con el aprecio hacia programas y grados."
        },
        {
            "num": "BLOQUE 4",
            "time": "1:55 – 2:35 (40 seg)",
            "title": "Validación Humana y Visualizaciones Avanzadas",
            "screen": "Pasar a la pestaña <b>Visualizaciones avanzadas</b>. Mostrar primero el <b>Cuadrante de Impacto (Scatter Plot)</b> apuntando a las burbujas de Protesta, Admisiones e Infraestructura. Bajar enseguida al <b>Diagrama de Sankey</b> y pasar el cursor sobre los flujos entre plataformas y temas.",
            "voice": '"Para validar las reglas, ambos autores evaluamos a ciegas una muestra estratificada independiente de 198 comentarios. Obtuvimos un acuerdo inter-anotador sustancial de kappa = 0,623 y una coincidencia de categoría exacta del 56,2% frente a las reglas. En esta sección avanzada, el Cuadrante de Impacto cruza el volumen frente a la negatividad: la línea horizontal marca el promedio del corpus (14,6%). Temas como Admisiones e Infraestructura se sitúan en el cuadrante superior de puntos de dolor focalizados. Abajo, el Diagrama de Sankey mapea visualmente cómo el tráfico fluye desde cada red hacia los tópicos y la polaridad final."',
            "interpretation": "<b>Interpretación del Cuadrante y Sankey:</b><br/>"
                              "• <i>Cuadrante:</i> Separa dos tipos de problemas: <i>Protesta</i> es un evento de alto volumen y alta visibilidad; mientras que <i>Infraestructura</i> y <i>Admisiones</i> son temas de menor volumen pero con tasas de quejas que duplican la media institucional (23%–26% negativo), señalando cuellos de botella operativos en sedes y matrículas.<br/>"
                              "• <i>Sankey:</i> Demuestra que la negatividad institucional se origina mayoritariamente en Facebook hacia trámites y admisiones, mientras Instagram drena hacia positividad en felicitaciones."
        },
        {
            "num": "BLOQUE 5",
            "time": "2:35 – 3:00 (25 seg)",
            "title": "Perfil Emocional, Privacidad y Conclusión",
            "screen": "Mostrar brevemente el <b>Radar Emocional</b> por plataforma en la misma pestaña avanzada. Finalizar en la pestaña <b>Método y límites</b> mostrando el texto de privacidad y el enlace a GitHub.",
            "voice": '"Finalmente, el gráfico de Radar evidencia que la huella emocional de Instagram se expande fuertemente hacia la alegría (32%), mientras Facebook abarca mayor tensión con picos en enojo y tristeza. Respecto a la ética, la aplicación opera exclusivamente con datos agregados y supresión de celdas menores a 10 comentarios, garantizando que ningún texto privado ni usuario sea expuesto. Este proyecto aporta una herramienta analítica auditable, reproducible y transparente para la comunidad académica. ¡Muchas gracias!"',
            "interpretation": "<b>Interpretación del Radar de Emociones:</b> Dos tercios del corpus (66,8%) caen en la categoría 'Otros', lo que demuestra que los comentarios universitarios son primordialmente informativos, transaccionales y sin desborde emocional. Instagram amplifica la alegría y el reconocimiento estético, mientras Facebook canaliza las demandas ciudadanas y estudiantiles."
        }
    ]

    for b in blocks:
        block_content = []
        # Header del bloque
        hdr_text = f"<b>{b['num']} &nbsp;|&nbsp; {b['time']} &nbsp;—&nbsp; {b['title']}</b>"
        block_content.append(Paragraph(hdr_text, block_title_style))

        # Tabla con 3 filas: Pantalla, Voz, Interpretación
        table_data = [
            [
                Paragraph("<b>Visual en pantalla</b><br/><i>(Acción en la app)</i>", label_style),
                Paragraph(b["screen"], body_style)
            ],
            [
                Paragraph("<b>Guión de voz en off</b><br/><i>(Locución exacta)</i>", label_style),
                Paragraph(b["voice"], script_style)
            ],
            [
                Paragraph("<b>Claves de interpretación</b><br/><i>(Qué significan los datos)</i>", label_style),
                Paragraph(b["interpretation"], interpret_style)
            ]
        ]

        t = Table(table_data, colWidths=[120, 384])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7FAFC")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#EDF2F7")),
            ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#FFFFFF")),
            ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#FFF5F5")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        block_content.append(t)
        block_content.append(Spacer(1, 10))

        story.append(KeepTogether(block_content))

    # Caja final de recomendaciones
    recom_data = [
        [
            Paragraph("<b>Recomendaciones clave para la grabación del video:</b><br/>"
                      "1. <b>Ritmo de locución:</b> Mantener una velocidad moderada (~130 palabras por minuto). El texto de voz suma exactamente 410 palabras (unos 2 minutos y 45 segundos de habla natural).<br/>"
                      "2. <b>Zoom de pantalla:</b> Grabar la ventana de Streamlit a un 90% de escala para que las gráficas interactivas de Plotly se aprecien íntegras sin desplazamiento brusco.<br/>"
                      "3. <b>Interacción suave:</b> Desplazar el cursor pausadamente sobre las barras y burbujas clave para activar las etiquetas flotantes (tooltips) justo cuando se mencionen en el audio.",
                      body_style)
        ]
    ]
    t_recom = Table(recom_data, colWidths=[504])
    t_recom.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EBF8FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#3182CE")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(Spacer(1, 4))
    story.append(t_recom)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
