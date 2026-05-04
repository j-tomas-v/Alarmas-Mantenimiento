"""Script para generar la Guía de Usuario en PDF."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable,
)

# Colors
RED = HexColor("#E74C3C")
ORANGE = HexColor("#F39C12")
GREEN = HexColor("#27AE60")
GRAY = HexColor("#95A5A6")
DARK = HexColor("#2C3E50")
BLUE = HexColor("#3498DB")
LIGHT_BG = HexColor("#F5F6FA")
LIGHT_RED = HexColor("#FADBD8")
LIGHT_ORANGE = HexColor("#FEF5E7")
LIGHT_GREEN = HexColor("#E8F8F5")
LIGHT_GRAY = HexColor("#F2F3F4")
LIGHT_BLUE = HexColor("#EBF5FB")
WHITE = white

OUTPUT_PATH = "docs/guia_usuario.pdf"


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        alignment=TA_CENTER,
        textColor=DARK,
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Helvetica",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=GRAY,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=DARK,
        spaceBefore=20,
        spaceAfter=10,
        borderWidth=0,
        borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        name="SubSection",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=BLUE,
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        textColor=black,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BulletItem",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        leftIndent=20,
        bulletIndent=8,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="ImportantNote",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=RED,
        spaceBefore=8,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="FAQ_Question",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=DARK,
        spaceBefore=10,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="FAQ_Answer",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        leftIndent=15,
        textColor=black,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=GRAY,
    ))
    return styles


def add_header_line(story):
    story.append(HRFlowable(
        width="100%", thickness=2, color=BLUE,
        spaceBefore=2, spaceAfter=10,
    ))


def colored_box_table(text, bg_color, text_color=black):
    """Create a small colored box with text inside."""
    style = ParagraphStyle("box", fontName="Helvetica", fontSize=9,
                           textColor=text_color, alignment=TA_CENTER)
    t = Table([[Paragraph(text, style)]], colWidths=[4 * cm], rowHeights=[0.7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("BOX", (0, 0), (-1, -1), 0.5, bg_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def build_pdf():
    styles = build_styles()

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        title="Guia de Usuario - Sistema de Alarmas de Mantenimiento ATT",
        author="Equipo de Control de Calidad",
    )

    story = []

    # ========== COVER PAGE ==========
    story.append(Spacer(1, 4 * cm))

    # Title box
    cover_data = [[Paragraph(
        "Sistema de Alarmas de<br/>Mantenimiento ATT", styles["CoverTitle"])]]
    cover_table = Table(cover_data, colWidths=[15 * cm])
    cover_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 1 * cm))

    story.append(HRFlowable(width="60%", thickness=3, color=BLUE, spaceBefore=0, spaceAfter=15))

    story.append(Paragraph("Guia de Usuario", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Equipo de Control de Calidad", styles["CoverSubtitle"]))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("Mayo 2026", ParagraphStyle(
        "date", fontName="Helvetica", fontSize=12, alignment=TA_CENTER, textColor=GRAY)))
    story.append(Spacer(1, 1 * cm))

    # Version info
    version_style = ParagraphStyle("ver", fontName="Helvetica", fontSize=9,
                                   alignment=TA_CENTER, textColor=GRAY)
    story.append(Paragraph("Version 1.2", version_style))

    story.append(PageBreak())

    # ========== TABLE OF CONTENTS ==========
    story.append(Paragraph("Contenido", styles["SectionTitle"]))
    add_header_line(story)

    toc_items = [
        ("1.", "Introduccion"),
        ("2.", "Pantalla Principal - Dashboard"),
        ("3.", "Alertas y Asignacion de Personal"),
        ("4.", "Vehiculos - Registro de Kilometraje"),
        ("5.", "Configuracion"),
        ("6.", "Significado de Colores y Dias Restantes"),
        ("7.", "Emails Automaticos"),
        ("8.", "Cerrar Ordenes y Auto-Creacion"),
        ("9.", "Dashboard Web (Pantalla de Planta)"),
        ("10.", "Preguntas Frecuentes"),
    ]
    for num, title in toc_items:
        story.append(Paragraph(
            f"<b>{num}</b>&nbsp;&nbsp;&nbsp;{title}", styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 1. INTRODUCCION ==========
    story.append(Paragraph("1. Introduccion", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "El <b>Sistema de Alarmas de Mantenimiento ATT</b> es una aplicacion de escritorio "
        "desarrollada para el equipo de Control de Calidad. Su objetivo es facilitar el "
        "seguimiento de las ordenes de mantenimiento preventivo y correctivo de las maquinas, "
        "equipos y vehiculos de la empresa.",
        styles["BodyText2"]))

    story.append(Paragraph("El sistema permite:", styles["BodyText2"]))

    benefits = [
        "Visualizar el estado de todas las ordenes de mantenimiento en un dashboard centralizado.",
        "Identificar rapidamente mantenimientos vencidos o proximos a vencer mediante un sistema de colores.",
        "Generar y enviar alertas por email a los responsables cuando un mantenimiento esta vencido o proximo.",
        "Registrar el kilometraje de los vehiculos de la empresa (Renault Master, Camion Iveco, Toyota Hiace).",
        "Solicitar automaticamente informacion de kilometraje a los conductores por email.",
        "Configurar frecuencias de mantenimiento por cada actividad del PAMPO.",
    ]
    for b in benefits:
        story.append(Paragraph(f"\u2022  {b}", styles["BulletItem"]))

    story.append(Spacer(1, 0.5 * cm))

    # Important note box
    note_data = [[Paragraph(
        "<b>NOTA:</b> El sistema puede actualizar el personal asignado (PM1/PM2/PM3) directamente "
        "en la base de datos Access desde la vista de Alertas. Los datos de kilometraje, "
        "configuracion y directorio de personal se guardan en archivos locales separados.",
        ParagraphStyle("note", fontName="Helvetica", fontSize=9, leading=13, textColor=DARK))]]
    note_table = Table(note_data, colWidths=[14 * cm])
    note_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 1, BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(note_table)

    story.append(PageBreak())

    # ========== 2. DASHBOARD ==========
    story.append(Paragraph("2. Pantalla Principal - Dashboard", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "El Dashboard es la pantalla principal del sistema. Al abrir la aplicacion, esta es la "
        "primera vista que aparece. Muestra un resumen del estado de todos los mantenimientos "
        "y permite navegar y filtrar las ordenes.",
        styles["BodyText2"]))

    # 2.1 Summary Cards
    story.append(Paragraph("2.1 Tarjetas de Resumen", styles["SubSection"]))
    story.append(Paragraph(
        "En la parte superior del dashboard se muestran 4 tarjetas con informacion resumida:",
        styles["BodyText2"]))

    cards_data = [
        ["Tarjeta", "Color", "Descripcion"],
        ["Pendientes", "Rojo", "Cantidad total de ordenes que aun no fueron completadas"],
        ["Vencidos", "Rojo", "Ordenes cuya fecha limite ya paso y no se realizaron"],
        ["Proximos", "Naranja", "Ordenes que vencen en los proximos 7 dias"],
        ["Completados (mes)", "Verde", "Ordenes completadas durante el mes actual"],
    ]
    cards_table = Table(cards_data, colWidths=[3.5 * cm, 2.5 * cm, 8.5 * cm])
    cards_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (1, 1), (1, 1), LIGHT_RED),
        ("BACKGROUND", (1, 2), (1, 2), LIGHT_RED),
        ("BACKGROUND", (1, 3), (1, 3), LIGHT_ORANGE),
        ("BACKGROUND", (1, 4), (1, 4), LIGHT_GREEN),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 0.5 * cm))

    # 2.2 Table
    story.append(Paragraph("2.2 Tabla de Ordenes", styles["SubSection"]))
    story.append(Paragraph(
        "Debajo de las tarjetas se muestra una tabla con todas las ordenes de mantenimiento. "
        "Cada fila esta coloreada segun su estado de urgencia:",
        styles["BodyText2"]))

    color_rows = [
        ["Color de fondo", "Estado", "Significado"],
        ["Rojo claro", "Vencido", "La fecha limite ya paso. Requiere atencion inmediata."],
        ["Naranja claro", "Proximo", "Vence en los proximos 7 dias. Planificar su realizacion."],
        ["Verde claro", "Programado", "Dentro del plazo. No requiere accion urgente."],
        ["Gris claro", "Completado", "Ya fue realizado. Solo informativo."],
    ]
    color_table = Table(color_rows, colWidths=[3 * cm, 2.5 * cm, 9 * cm])
    color_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT_RED),
        ("BACKGROUND", (0, 2), (0, 2), LIGHT_ORANGE),
        ("BACKGROUND", (0, 3), (0, 3), LIGHT_GREEN),
        ("BACKGROUND", (0, 4), (0, 4), LIGHT_GRAY),
    ]))
    story.append(color_table)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "Las columnas de la tabla son: <b>N. de OM</b>, <b>Dias restantes</b>, Maquina, Actividad, "
        "Tipo, Fecha de creacion, Fecha limite, Estado y Personal asignado. "
        "La columna <b>Dias restantes</b> esta ubicada en la segunda posicion (justo despues de "
        "N. de OM) porque es el dato operativo mas importante: indica cuanto falta para que "
        "venza la proxima orden de cada equipo.",
        styles["BodyText2"]))

    story.append(Paragraph(
        "<b>Detalle de una orden:</b> Haga <b>doble click</b> sobre cualquier fila para abrir "
        "una ventana emergente con toda la informacion de esa orden de mantenimiento. "
        "Desde alli tambien puede <b>finalizar</b> una orden con el boton verde 'Finalizar Orden'.",
        styles["BodyText2"]))

    # 2.3 Filters
    story.append(Paragraph("2.3 Filtros", styles["SubSection"]))
    story.append(Paragraph(
        "Entre las tarjetas y la tabla hay un panel de filtros que permite reducir la "
        "lista de ordenes mostradas:",
        styles["BodyText2"]))

    filters = [
        "<b>Maquina:</b> Filtrar por una maquina o equipo especifico (ej: Barnizadora, Troqueladora YIGUO).",
        "<b>Tipo:</b> Filtrar entre mantenimientos Preventivos o Correctivos.",
        "<b>Estado:</b> Filtrar por Pendientes (default), Vencido, Proximo, Programado, Completado o Todos.",
        "<b>Solo ultimo por PAMPO:</b> Checkbox que muestra unicamente la orden mas reciente de "
        "cada procedimiento. Util para ver el estado actual de cada equipo de un vistazo.",
    ]
    for f in filters:
        story.append(Paragraph(f"\u2022  {f}", styles["BulletItem"]))

    story.append(Paragraph(
        'Presione el boton <b>"Actualizar"</b> para refrescar los datos desde la base de datos Access.',
        styles["BodyText2"]))

    story.append(Paragraph("2.4 Boton 'Abrir Dashboard Web'", styles["SubSection"]))
    story.append(Paragraph(
        'En la esquina superior derecha del Dashboard hay un boton azul <b>"&#127760; Abrir Dashboard Web"</b>. '
        'Al presionarlo, el sistema arranca un servidor web local (si no estaba activo) y abre el '
        'navegador con una vista optimizada para mostrar en una pantalla de planta. Ver la seccion 9 '
        'para mas detalles sobre como usar y configurar este dashboard.',
        styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 3. ALERTAS ==========
    story.append(Paragraph("3. Alertas y Asignacion de Personal", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "La seccion de Alertas permite evaluar el estado actual de todos los mantenimientos "
        "y generar notificaciones que pueden enviarse por email a los responsables. "
        "Tambien permite asignar personal directamente desde la lista de alertas.",
        styles["BodyText2"]))

    story.append(Paragraph("3.1 Tipos de Alerta", styles["SubSection"]))

    alert_types = [
        ["Tipo de Alerta", "Descripcion"],
        ["Mantenimiento vencido", "Se genera cuando una orden supero su fecha limite y no fue completada."],
        ["Mantenimiento proximo", "Se genera cuando una orden vence dentro de los proximos 7 dias."],
        ["Solicitud de kilometraje",
         "Se genera cuando un vehiculo no tiene registros de km recientes."],
    ]
    at_table = Table(alert_types, colWidths=[4.5 * cm, 10 * cm])
    at_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(at_table)

    story.append(Paragraph("3.2 Acciones", styles["SubSection"]))

    actions = [
        '<b>"Evaluar alertas":</b> Analiza todas las ordenes pendientes y genera la lista de alertas actual. '
        'La tabla incluye una columna <b>Personal</b> mostrando quien esta asignado a cada orden.',
        '<b>"Asignar personal":</b> Seleccione una alerta y presione este boton para abrir un dialogo '
        'donde puede asignar PM1, PM2 y PM3 a la orden. Los cambios se guardan directamente en Access.',
        '<b>"Enviar seleccionada":</b> Seleccione una alerta de la lista y presione este boton para enviar '
        'un email de notificacion a los destinatarios correspondientes.',
        '<b>"Enviar todas pendientes":</b> Envia emails para todas las alertas que no hayan sido enviadas '
        'recientemente.',
    ]
    for a in actions:
        story.append(Paragraph(f"\u2022  {a}", styles["BulletItem"]))

    story.append(Paragraph("3.3 Asignar Personal a una Orden", styles["SubSection"]))
    story.append(Paragraph(
        "Al presionar <b>'Asignar personal'</b> con una alerta seleccionada, se abre un dialogo con "
        "tres campos (PM1, PM2, PM3). Los desplegables se autocompletan con los nombres registrados "
        "en el Directorio de Personal (ver seccion 5.2). Al guardar, el sistema actualiza los campos "
        "en la base de datos Access y refresca la tabla de alertas.",
        styles["BodyText2"]))

    story.append(Paragraph("3.4 Sistema de Cooldown", styles["SubSection"]))
    story.append(Paragraph(
        "Para evitar saturar las casillas de email, el sistema tiene un periodo de <b>cooldown</b> "
        "(por defecto 7 dias). Si una alerta ya fue enviada dentro de ese periodo, no se reenviara "
        "hasta que transcurra el tiempo configurado. Esto se aplica tanto al envio manual como al automatico.",
        styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 4. VEHICULOS ==========
    story.append(Paragraph("4. Vehiculos - Registro de Kilometraje", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "Esta seccion permite registrar el kilometraje de los vehiculos de la empresa. "
        "Es fundamental para el seguimiento del mantenimiento vehicular.",
        styles["BodyText2"]))

    story.append(Paragraph("4.1 Registrar Nuevo Kilometraje", styles["SubSection"]))
    story.append(Paragraph("Complete los siguientes campos:", styles["BodyText2"]))

    fields = [
        "<b>Vehiculo:</b> Seleccione el vehiculo de la lista (Renault Master, Camion Iveco, Toyota Hiace).",
        "<b>Kilometraje:</b> Ingrese la lectura actual del odometro. Debe ser mayor o igual al ultimo registro.",
        "<b>Fecha:</b> Fecha de la lectura en formato DD/MM/AAAA (por defecto es la fecha actual).",
        "<b>Registrado por:</b> Nombre de la persona que realiza el registro.",
        "<b>Notas:</b> Campo opcional para observaciones.",
    ]
    for f in fields:
        story.append(Paragraph(f"\u2022  {f}", styles["BulletItem"]))

    story.append(Paragraph(
        'Presione <b>"Guardar registro"</b> para almacenar los datos. El sistema validara que el '
        'kilometraje sea correcto antes de guardar.',
        styles["BodyText2"]))

    story.append(Paragraph("4.2 Historial de Registros", styles["SubSection"]))
    story.append(Paragraph(
        "Debajo del formulario se muestra el historial de todos los registros de kilometraje. "
        "Puede filtrar por vehiculo usando el selector disponible.",
        styles["BodyText2"]))

    # Important note
    note2_data = [[Paragraph(
        "<b>IMPORTANTE:</b> Si no se registra el kilometraje de un vehiculo dentro del periodo "
        "configurado, el sistema enviara automaticamente un email a los conductores solicitando "
        "la actualizacion de datos.",
        ParagraphStyle("note2", fontName="Helvetica", fontSize=9, leading=13, textColor=DARK))]]
    note2_table = Table(note2_data, colWidths=[14 * cm])
    note2_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_ORANGE),
        ("BOX", (0, 0), (-1, -1), 1, ORANGE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(note2_table)

    story.append(PageBreak())

    # ========== 5. CONFIGURACION ==========
    story.append(Paragraph("5. Configuracion", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "La seccion Configuracion permite ajustar todos los parametros del sistema sin necesidad "
        "de editar archivos manualmente.",
        styles["BodyText2"]))

    story.append(Paragraph("5.1 Servidor SMTP", styles["SubSection"]))
    story.append(Paragraph(
        "Configure la cuenta de email desde la que se enviaran las alertas. "
        "Use el boton <b>'Probar conexion'</b> para verificar que los datos sean correctos "
        "antes de guardar. El sistema soporta SSL (puerto 465) y STARTTLS (puerto 587).",
        styles["BodyText2"]))

    story.append(Paragraph("5.2 Directorio de Personal", styles["SubSection"]))
    story.append(Paragraph(
        "Permite registrar el nombre y el email de cada integrante del equipo de mantenimiento. "
        "Estos datos se usan para:",
        styles["BodyText2"]))

    pd_uses = [
        "Autocompletar los desplegables al asignar personal a una orden desde la vista de Alertas.",
        "Agregar automaticamente los emails del personal asignado (PM1/PM2/PM3) como destinatarios "
        "al enviar una alerta de esa orden.",
    ]
    for u in pd_uses:
        story.append(Paragraph(f"\u2022  {u}", styles["BulletItem"]))

    story.append(Paragraph(
        "Para agregar una persona: complete los campos <b>Nombre</b> y <b>Email</b> y presione "
        "<b>'Agregar / Actualizar'</b>. Para eliminar: seleccione la fila y presione "
        "<b>'Eliminar seleccionado'</b>.",
        styles["BodyText2"]))

    story.append(Paragraph("5.3 Destinatarios de Email", styles["SubSection"]))
    story.append(Paragraph(
        "Permite configurar las listas de destinatarios para cada tipo de alerta. "
        "Los grupos disponibles son: Equipo mantenimiento, Gerencia y Conductores. "
        "Se pueden ingresar multiples emails separados por coma.",
        styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 6. COLORES Y DIAS RESTANTES ==========
    story.append(Paragraph("6. Significado de Colores y Dias Restantes", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph("6.1 Colores de Estado", styles["SubSection"]))
    story.append(Paragraph(
        "El sistema utiliza un codigo de colores consistente en toda la aplicacion para "
        "indicar el estado de urgencia de cada orden:",
        styles["BodyText2"]))

    estado_data = [
        ["Color", "Estado", "Significado", "Accion requerida"],
        ["ROJO", "Vencido",
         "La fecha limite ya paso",
         "Accion INMEDIATA. Coordinar realizacion urgente."],
        ["NARANJA", "Proximo",
         "Vence en los proximos 7 dias",
         "Planificar realizacion esta semana."],
        ["VERDE", "Programado",
         "Dentro del plazo establecido",
         "No urgente. Planificar segun calendario."],
        ["GRIS", "Completado",
         "Mantenimiento ya realizado",
         "Ninguna. Solo informativo."],
    ]
    est_table = Table(estado_data, colWidths=[2.2 * cm, 2.2 * cm, 4.5 * cm, 5.5 * cm])
    est_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (0, 1), LIGHT_RED),
        ("BACKGROUND", (0, 2), (0, 2), LIGHT_ORANGE),
        ("BACKGROUND", (0, 3), (0, 3), LIGHT_GREEN),
        ("BACKGROUND", (0, 4), (0, 4), LIGHT_GRAY),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
    ]))
    story.append(est_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("6.2 Dias Restantes", styles["SubSection"]))
    story.append(Paragraph(
        "La columna <b>Dias restantes</b> es el indicador operativo principal del sistema. "
        "Muestra cuantos dias faltan para que venza la proxima orden de cada equipo. Su formato es:",
        styles["BodyText2"]))

    dias_data = [
        ["Texto en celda", "Significado", "Color"],
        ["7 dias", "Faltan 7 dias para el vencimiento", "Verde (programado) o Naranja (proximo)"],
        ["HOY", "Vence hoy mismo", "Naranja"],
        ["VENCIDA (-3)", "Vencida hace 3 dias", "Rojo"],
        ["—", "Orden ya finalizada (no aplica)", "Gris"],
    ]
    dias_table = Table(dias_data, colWidths=[3.5 * cm, 5.5 * cm, 5.5 * cm])
    dias_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (2, 3), (2, 3), LIGHT_RED),
        ("BACKGROUND", (2, 2), (2, 2), LIGHT_ORANGE),
        ("BACKGROUND", (2, 4), (2, 4), LIGHT_GRAY),
    ]))
    story.append(dias_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "<b>Tip:</b> En el dashboard web (pantalla de planta), los dias restantes se muestran "
        "con fuente grande y color por urgencia para que sean legibles a la distancia.",
        styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 7. EMAILS AUTOMATICOS ==========
    story.append(Paragraph("7. Emails Automaticos", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "El sistema puede enviar emails automaticamente de forma periodica durante el horario "
        "laboral (por defecto entre las 7:00 y las 18:00 hs). La frecuencia de verificacion "
        "es configurable (por defecto cada 4 horas).",
        styles["BodyText2"]))

    story.append(Paragraph("7.1 Tipos de Email", styles["SubSection"]))

    email_types = [
        "<b>Alerta de mantenimiento vencido:</b> Email con fondo rojo informando que un "
        "mantenimiento supero su fecha limite. Incluye datos de la orden, maquina, actividad "
        "y dias de atraso.",
        "<b>Alerta de mantenimiento proximo:</b> Email con fondo naranja avisando que un "
        "mantenimiento vence en los proximos dias. Permite planificar con anticipacion.",
        "<b>Solicitud de kilometraje:</b> Email con fondo azul dirigido a los conductores "
        "solicitando que informen el kilometraje actual de su vehiculo.",
    ]
    for e in email_types:
        story.append(Paragraph(f"\u2022  {e}", styles["BulletItem"]))

    story.append(Paragraph("7.2 Destinatarios de las Alertas", styles["SubSection"]))
    story.append(Paragraph(
        "Cuando el sistema envia una alerta sobre una orden de mantenimiento, los destinatarios son:",
        styles["BodyText2"]))
    dest_items = [
        "El grupo <b>Equipo mantenimiento</b> configurado en la seccion Configuracion.",
        "Los emails del personal asignado (PM1/PM2/PM3) si tienen email registrado en el "
        "Directorio de Personal.",
    ]
    for d in dest_items:
        story.append(Paragraph(f"\u2022  {d}", styles["BulletItem"]))
    story.append(Paragraph(
        "Las alertas de kilometraje se envian solo al grupo <b>Conductores</b>.",
        styles["BodyText2"]))

    story.append(Paragraph("7.3 Al Recibir un Email", styles["SubSection"]))

    responses = [
        ["Tipo de Email", "Accion requerida"],
        ["Mantenimiento vencido",
         "Coordinar con el equipo de mantenimiento para realizar la tarea "
         "a la brevedad. Informar a Control de Calidad cuando se complete."],
        ["Mantenimiento proximo",
         "Planificar la realizacion del mantenimiento dentro del plazo. "
         "Verificar disponibilidad de personal y materiales."],
        ["Solicitud de kilometraje",
         "Informar el kilometraje actual del vehiculo al equipo de Control "
         "de Calidad. Puede hacerlo en persona o respondiendo el email."],
    ]
    resp_table = Table(responses, colWidths=[4.5 * cm, 10 * cm])
    resp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(resp_table)

    story.append(PageBreak())

    # ========== 8. CERRAR ORDENES ==========
    story.append(Paragraph("8. Cerrar Ordenes y Auto-Creacion", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "Cuando un mantenimiento se realiza, hay que registrarlo en el sistema. "
        "El sistema tiene una funcionalidad para finalizar ordenes y, ademas, "
        "<b>automaticamente genera la siguiente orden programada</b> en base a la "
        "frecuencia del PAMPO correspondiente.",
        styles["BodyText2"]))

    story.append(Paragraph("8.1 Como cerrar una orden", styles["SubSection"]))

    close_steps = [
        "En el Dashboard, haga <b>doble click</b> sobre la fila de la orden a cerrar.",
        "Se abre el popup de detalle. Presione el boton verde <b>'Finalizar Orden'</b>.",
        "Confirme la accion en el dialogo.",
        "El sistema marca la orden como completada en Access "
        "(<b>¿Finalizado? = Si</b>, <b>Fecha realizacion = hoy</b>) y refresca la tabla.",
    ]
    for s in close_steps:
        story.append(Paragraph(f"•  {s}", styles["BulletItem"]))

    story.append(Paragraph("8.2 Auto-creacion de la siguiente OM", styles["SubSection"]))
    story.append(Paragraph(
        "Si la orden cerrada era la <b>ultima registrada</b> para ese ID PAMPO, el sistema crea "
        "automaticamente la siguiente orden con:",
        styles["BodyText2"]))

    auto_items = [
        "<b>Fecha de creacion:</b> hoy",
        "<b>Realizar el dia:</b> hoy + frecuencia configurada (de pampo_frequencies.json)",
        "<b>Tipo (Preventivo/Correctivo):</b> mismo que la orden cerrada",
        "<b>ID PAMPO:</b> mismo que la orden cerrada",
        "<b>Resto de campos:</b> vacios o por defecto",
    ]
    for a in auto_items:
        story.append(Paragraph(f"•  {a}", styles["BulletItem"]))

    story.append(Paragraph("8.3 Asignacion de personal a la nueva OM", styles["SubSection"]))
    story.append(Paragraph(
        "Si la orden cerrada tenia <b>personal asignado</b> (PM1/PM2/PM3), el sistema abre un "
        "popup con esos nombres precargados, para que el usuario los confirme o edite para la "
        "nueva orden:",
        styles["BodyText2"]))

    pers_items = [
        "<b>'Guardar':</b> asigna el personal mostrado a la nueva OM.",
        "<b>'Omitir':</b> la nueva OM queda sin personal.",
    ]
    for p in pers_items:
        story.append(Paragraph(f"•  {p}", styles["BulletItem"]))

    story.append(Paragraph(
        "Si la orden cerrada <b>no tenia personal asignado</b>, la nueva OM se crea sin personal "
        "y no aparece ningun dialogo (no se pregunta).",
        styles["BodyText2"]))

    story.append(PageBreak())

    # ========== 9. DASHBOARD WEB ==========
    story.append(Paragraph("9. Dashboard Web (Pantalla de Planta)", styles["SectionTitle"]))
    add_header_line(story)

    story.append(Paragraph(
        "Ademas del dashboard de la app de escritorio, el sistema incluye un <b>dashboard web</b> "
        "pensado para mostrarse permanentemente en una pantalla de planta (TV o monitor industrial). "
        "El dashboard web se actualiza automaticamente cada 60 segundos sin intervencion del usuario.",
        styles["BodyText2"]))

    story.append(Paragraph("9.1 Como abrir el dashboard web", styles["SubSection"]))
    open_steps = [
        "En la app de escritorio, ir al Dashboard principal.",
        "Hacer click en el boton azul <b>'&#127760; Abrir Dashboard Web'</b> (esquina superior derecha).",
        "El sistema arranca un servidor web local (si no estaba activo) y abre el navegador "
        "automaticamente con el dashboard.",
    ]
    for s in open_steps:
        story.append(Paragraph(f"•  {s}", styles["BulletItem"]))

    story.append(Paragraph("9.2 Vistas disponibles", styles["SubSection"]))
    view_items = [
        "<b>Por defecto:</b> muestra solo la <b>ultima orden de cada PAMPO</b>. Vista de "
        "'estado actual de cada equipo'.",
        "<b>'Ver todas las ordenes':</b> link en la esquina superior derecha del navegador. "
        "Muestra todas las ordenes pendientes.",
        "<b>Auto-refresh:</b> el dashboard se recarga solo cada 60 segundos. No hay que tocar nada.",
    ]
    for v in view_items:
        story.append(Paragraph(f"•  {v}", styles["BulletItem"]))

    story.append(Paragraph("9.3 Conectar la pantalla de planta por HDMI", styles["SubSection"]))
    story.append(Paragraph(
        "Caso tipico: conectar la PC de Control de Calidad a una TV/monitor de planta usando un "
        "cable HDMI, y mostrar el dashboard web en esa pantalla.",
        styles["BodyText2"]))

    hdmi_data = [
        ["Paso", "Accion"],
        ["1", "Conectar el cable HDMI entre la PC y la pantalla de planta."],
        ["2", "En Windows, presionar Win + P y seleccionar 'Extender' (no 'Duplicar')."],
        ["3", "Abrir el dashboard web desde la app (boton 'Abrir Dashboard Web')."],
        ["4", "Arrastrar la ventana del navegador hacia la pantalla de planta."],
        ["5", "Presionar F11 en el navegador para entrar en modo pantalla completa."],
        ["6", "(Opcional) Ajustar resolucion y escala desde Configuracion de Windows para que "
              "sea legible a distancia."],
    ]
    hdmi_table = Table(hdmi_data, colWidths=[1.5 * cm, 13 * cm])
    hdmi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(hdmi_table)
    story.append(Spacer(1, 0.4 * cm))

    # Important note
    note_hdmi_data = [[Paragraph(
        "<b>IMPORTANTE:</b> El dashboard se actualiza solo cada 60 segundos. No hay que refrescar "
        "manualmente. Si la pantalla muestra un error de conexion ('localhost rechazo la conexion'), "
        "volver a la PC y presionar el boton 'Abrir Dashboard Web' para arrancar el servidor.",
        ParagraphStyle("note_hdmi", fontName="Helvetica", fontSize=9, leading=13, textColor=DARK))]]
    note_hdmi_table = Table(note_hdmi_data, colWidths=[14 * cm])
    note_hdmi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("BOX", (0, 0), (-1, -1), 1, BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(note_hdmi_table)

    story.append(Paragraph("9.4 Tips operativos", styles["SubSection"]))
    tips = [
        "Dejar la PC y el navegador siempre abiertos durante el horario laboral.",
        "Para que el servidor arranque automaticamente al prender la PC, pedir al administrador "
        "del sistema que active <b>auto_start</b> en la configuracion del sistema.",
        "Si la pantalla externa se queda en negro tras un rato de inactividad, deshabilitar la "
        "suspension del monitor en Configuracion de Windows -> Sistema -> Energia.",
        "Tambien se puede acceder al dashboard desde otra PC en la misma red ingresando "
        "<b>http://&lt;ip-de-la-pc-server&gt;:5000</b> en el navegador.",
    ]
    for t in tips:
        story.append(Paragraph(f"•  {t}", styles["BulletItem"]))

    story.append(PageBreak())

    # ========== 10. FAQ ==========
    story.append(Paragraph("10. Preguntas Frecuentes", styles["SectionTitle"]))
    add_header_line(story)

    faqs = [
        ("Cada cuanto se actualizan los datos?",
         "Los datos se actualizan desde la base de datos Access cada vez que se abre el "
         "Dashboard o se presiona el boton 'Actualizar'. Ademas, el sistema verifica "
         "automaticamente cada cierta cantidad de horas (configurable)."),

        ("Puedo modificar la base de datos desde el sistema?",
         "Si, parcialmente. Desde la vista de Alertas se puede asignar personal (PM1/PM2/PM3) "
         "a cualquier orden. El resto de los campos debe seguir editandose directamente en Access."),

        ("Que hago si aparece un error de conexion?",
         "Verifique que: (1) La base de datos Access no este abierta en modo exclusivo por "
         "otro usuario. (2) La ruta al archivo .accdb sea correcta en la seccion Configuracion. "
         "(3) El driver ODBC de Microsoft Access este instalado en la computadora. Si el problema "
         "persiste, contacte al administrador del sistema."),

        ("Quien configura las frecuencias de mantenimiento?",
         "El equipo de Control de Calidad puede configurar las frecuencias (cada cuantos dias "
         "debe realizarse cada actividad) desde la seccion 'Configuracion' del sistema. "
         "Cada actividad del PAMPO tiene su frecuencia individual."),

        ("Por que recibo emails repetidos?",
         "El sistema tiene un periodo de cooldown de 7 dias. Si recibe un email sobre el "
         "mismo mantenimiento, significa que pasaron mas de 7 dias y la tarea sigue pendiente."),

        ("Como se si un mantenimiento esta vencido?",
         "En el Dashboard, las filas en color rojo indican mantenimientos vencidos. La columna "
         "'Dias rest.' muestra un numero negativo indicando cuantos dias de atraso tiene."),

        ("Como cierro una orden de mantenimiento?",
         "Hacer doble click sobre la fila de la orden en el Dashboard, y en el popup que aparece "
         "presionar el boton verde 'Finalizar Orden'. El sistema marca la orden como completada "
         "en Access y refresca la tabla."),

        ("Que pasa cuando cierro la ultima orden de un equipo?",
         "El sistema crea automaticamente la siguiente orden programada para ese equipo, con la "
         "frecuencia configurada en pampo_frequencies.json. Si la orden cerrada tenia personal "
         "asignado, aparece un popup para confirmar el personal de la nueva orden."),

        ("Como veo el dashboard en una pantalla grande de la planta?",
         "Conectar la PC a la pantalla por HDMI, presionar Win+P y seleccionar 'Extender'. "
         "Despues, en la app, hacer click en el boton azul 'Abrir Dashboard Web', arrastrar la "
         "ventana del navegador a la pantalla externa, y presionar F11 para pantalla completa. "
         "Ver la seccion 9 de esta guia para el procedimiento completo."),

        ("La pantalla de planta dice 'localhost rechazo la conexion', que hago?",
         "Significa que el servidor web no esta corriendo. Volver a la PC y presionar el boton "
         "azul 'Abrir Dashboard Web' en el Dashboard de la app. El servidor arranca y se abre "
         "automaticamente. Si pasa seguido, pedir al administrador que active 'auto_start' en "
         "la configuracion."),

        ("Puedo usar el sistema en varias computadoras?",
         "Si, siempre que todas apunten a la misma base de datos Access y tengan el driver "
         "ODBC instalado. Los datos de kilometraje, alertas y directorio de personal son "
         "locales a cada computadora."),

        ("Como agrego el email de un tecnico para que reciba las alertas?",
         "Ir a Configuracion seccion 'Directorio de Personal'. Ingresar el nombre exactamente "
         "como aparece en PM1/PM2/PM3 de Access y su email. Al enviar una alerta de una orden "
         "con ese tecnico asignado, recibira el email automaticamente."),

        ("Por que el tecnico asignado no recibe el email?",
         "Verificar que: (1) El nombre en el Directorio de Personal coincida exactamente con "
         "el nombre guardado en PM1/PM2/PM3 en Access (respetando mayusculas y espacios). "
         "(2) El email del tecnico sea correcto. (3) El servidor SMTP este correctamente "
         "configurado (probar con 'Probar conexion' en Configuracion)."),
    ]

    for q, a in faqs:
        story.append(Paragraph(f"  {q}", styles["FAQ_Question"]))
        story.append(Paragraph(a, styles["FAQ_Answer"]))

    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GRAY, spaceBefore=0, spaceAfter=10))
    story.append(Paragraph(
        "Sistema de Alarmas de Mantenimiento ATT - Guia de Usuario v1.2 - Mayo 2026<br/>"
        "Equipo de Control de Calidad",
        styles["Footer"]))

    # Build
    doc.build(story)
    print(f"PDF generado exitosamente: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
