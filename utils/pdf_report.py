import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from icecream import ic

def draw_cover_page(c, agent_name, report_date, logo_path, width, height):
    bleu = colors.HexColor("#2496ed")
    violet = colors.HexColor("#764ba2")
    # Logo centré
    logo_w, logo_h = 80, 80

    # Titre centré
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(bleu)
    c.drawCentredString(width/2, height-30, "Rapport DockerAudit")

    try:
        c.drawImage(ImageReader(logo_path), (width-logo_w)/2 - 10, height-2*cm-logo_h, width=logo_w, height=logo_h, mask='auto')
    except Exception:
        pass


    # Agent et date centrés
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-5*cm - 10, f"Agent : {agent_name}")
    c.setFont("Helvetica", 15)
    c.setFillColor(violet)
    c.drawCentredString(width/2, height-6*cm - 10, f"Date du rapport : {report_date}")
    # Encadré d'intro
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 15)
    intro = "Ce rapport présente l'état de sécurité de l'hôte et des conteneurs Docker audités."
    c.drawCentredString(width/2, height-8.5*cm, intro)
    c.showPage()

def color_for_status(status):
    if status == 'success' or status is False:
        return colors.green, colors.black
    if status == 'skipped':
        return colors.orange, colors.black
    if status is True:
        return colors.red, colors.white
    if status == 'info':
        return colors.blue, colors.white
    return colors.lightgrey, colors.black

def draw_vuln_table(c, report_data, width, height):
    bleu = colors.HexColor("#2496ed")
    violet = colors.HexColor("#764ba2")
    line_height = 32
    font_size = 12
    header_font_size = 14
    col1, col2 = 2*cm, 11*cm
    col_widths = [9*cm, 6*cm]
    y = height-2.5*cm
    # Titre centré
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(bleu)
    c.drawCentredString(width/2, y, "Synthèse des vulnérabilités détectées")
    y -= 1.2*cm
    # En-tête tableau
    c.setFont("Helvetica-Bold", header_font_size)
    c.setFillColor(bleu)
    c.rect(col1, y-line_height+6, col_widths[0], line_height, fill=1, stroke=0)
    c.rect(col2, y-line_height+6, col_widths[1], line_height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.drawCentredString(col1+col_widths[0]/2, y-line_height/2+header_font_size/2+2, "Vérification")
    c.drawCentredString(col2+col_widths[1]/2, y-line_height/2+header_font_size/2+2, "Statut")
    y -= line_height
    c.setFont("Helvetica", font_size)
    c.setFillColor(colors.black)
    # Host/global
    if 'host' in report_data:
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(bleu)
        c.drawString(col1, y-line_height/2+font_size/2+2, "Vulnérabilités globales (Host)")
        y -= line_height
        c.setFont("Helvetica", font_size)
        for key, val in report_data['host'].items():
            status = val.get('status') if isinstance(val, dict) else val
            label = key.replace('_', ' ')
            # Case Vérification
            c.setFillColor(colors.whitesmoke)
            c.rect(col1, y-line_height+6, col_widths[0], line_height, fill=1, stroke=0)
            c.setFillColor(colors.black)
            label_trunc = label[:40] + ("..." if len(label) > 40 else "")
            c.drawString(col1+8, y-line_height/2+font_size/2+2, label_trunc)
            # Case Statut
            fill, txtcol = color_for_status(status)
            c.setFillColor(fill)
            c.rect(col2, y-line_height+6, col_widths[1], line_height, fill=1, stroke=0)
            c.setFillColor(txtcol)
            txt = "OK" if status is False or status == 'success' else ("KO" if status is True else str(status))
            txt_trunc = txt[:15] + ("..." if len(txt) > 15 else "")
            c.drawCentredString(col2+col_widths[1]/2, y-line_height/2+font_size/2+2, txt_trunc)
            y -= line_height
            if y < 3*cm:
                c.showPage()
                y = height-2.5*cm
    y -= 10
    # Containers
    if 'containers' in report_data:
        for cid, cdata in report_data['containers'].items():
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(violet)
            cname = cdata.get('container_name', cid)
            image = cdata.get('image', '')
            c.drawString(col1, y, f"Conteneur : {cname} ({image})")
            y -= line_height
            c.setFont("Helvetica", font_size)
            for k, v in cdata.items():
                if k in ('container_name', 'image', 'running'):
                    continue
                status = v.get('status') if isinstance(v, dict) and 'status' in v else (v if isinstance(v, bool) else None)
                label = k.replace('_', ' ')
                # Case Vérification
                c.setFillColor(colors.whitesmoke)
                c.rect(col1, y-line_height+6, col_widths[0], line_height, fill=1, stroke=0)
                c.setFillColor(colors.black)
                label_trunc = label[:40] + ("..." if len(label) > 40 else "")
                c.drawString(col1+8, y-line_height/2+font_size/2+2, label_trunc)
                # Case Statut
                fill, txtcol = color_for_status(status)
                c.setFillColor(fill)
                c.rect(col2, y-line_height+6, col_widths[1], line_height, fill=1, stroke=0)
                c.setFillColor(txtcol)
                txt = "OK" if status is False or status == 'success' else ("KO" if status is True else str(status))
                txt_trunc = txt[:15] + ("..." if len(txt) > 15 else "")
                c.drawCentredString(col2+col_widths[1]/2, y-line_height/2+font_size/2+2, txt_trunc)
                y -= line_height
                if y < 3*cm:
                    c.showPage()
                    y = height-2.5*cm
            # Running status
            running = cdata.get('running', None)
            if running is not None:
                c.setFillColor(colors.whitesmoke)
                c.rect(col1, y-line_height+6, col_widths[0], line_height, fill=1, stroke=0)
                c.setFillColor(colors.black)
                c.drawString(col1+8, y-line_height/2+font_size/2+2, "Conteneur en cours d'exécution")
                fill, txtcol = color_for_status(not not running)
                c.setFillColor(fill)
                c.rect(col2, y-line_height+6, col_widths[1], line_height, fill=1, stroke=0)
                c.setFillColor(txtcol)
                c.drawCentredString(col2+col_widths[1]/2, y-line_height/2+font_size/2+2, "Oui" if running else "Non")
                y -= line_height
                if y < 3*cm:
                    c.showPage()
                    y = height-2.5*cm
            y -= 10
    # Légende
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    legend = [
        (colors.green, "🟩 : Pas de vulnérabilité détectée"),
        (colors.red, "🟥 : Vulnérabilité détectée (à corriger)"),
        (colors.orange, "🟧 : Vérification non applicable ou à surveiller"),
        (colors.blue, "🟦 : Information, attention requise (ex : données sensibles)")
    ]
    y = 2*cm
    for color, text in legend:
        c.setFillColor(color)
        c.drawString(col1, y, text)
        y += 16

def create_pdf_report(agent_name, report_date, report_data, logo_path="static/images/logo.png"):
    ic(report_data)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    draw_cover_page(c, agent_name, report_date, logo_path, width, height)
    draw_vuln_table(c, report_data, width, height)
    c.save()
    buffer.seek(0)
    return buffer 


