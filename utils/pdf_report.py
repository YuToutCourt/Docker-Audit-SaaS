import json
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

def draw_report_data(c, data, x, y, bleu, indent=0):
    """Affiche joliment le contenu du rapport, récursivement."""
    line_height = 18
    for key, value in data.items():
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(bleu)
        c.drawString(x + indent, y, str(key).replace("_", " ") + " :")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        if isinstance(value, dict):
            y -= line_height
            y = draw_report_data(c, value, x, y, bleu, indent + 20)
        elif isinstance(value, list):
            y -= line_height
            for item in value:
                c.drawString(x + indent + 20, y, f"- {item}")
                y -= line_height
        else:
            # Gérer le retour à la ligne si la valeur est trop longue
            text = str(value)
            while len(text) > 0:
                c.drawString(x + indent + 120, y, text[:60])
                text = text[60:]
                if text:
                    y -= line_height
            y -= line_height
        if y < 60:
            c.showPage()
            y = c._pagesize[1] - 60
    return y

def create_pdf_report(agent_name, report_date, report_data, logo_path="static/images/logo.png"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    bleu = colors.HexColor("#2496ed")
    violet = colors.HexColor("#764ba2")

    # En-tête avec logo
    try:
        c.drawImage(ImageReader(logo_path), 50, height - 90, width=60, height=60, mask='auto')
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(bleu)
    c.drawString(120, height - 60, f"Rapport DockerAudit")
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.black)
    c.drawString(120, height - 80, f"Agent : {agent_name}")

    c.setFont("Helvetica", 12)
    c.setFillColor(violet)
    c.drawString(50, height - 110, f"Date du rapport : {report_date}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, height - 130, "Données du rapport :")

    c.setFont("Helvetica", 12)
    y = height - 160
    y = draw_report_data(c, report_data, 70, y, bleu)

    c.save()
    buffer.seek(0)
    return buffer 


