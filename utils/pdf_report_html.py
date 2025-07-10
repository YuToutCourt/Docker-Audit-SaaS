from weasyprint import HTML
from io import BytesIO
import os

def status_class(status):
    if status is False or status == 'success':
        return 'status-ok', 'OK'
    if status is True:
        return 'status-ko', 'KO'
    if status == 'skipped':
        return 'status-skipped', 'skipped'
    if status == 'info':
        return 'status-info', 'info'
    return '', str(status)

def generate_html_report(agent_name, report_date, report_data, logo_url=None, css_path=None):
    # Page de couverture
    html = '<div class="cover">'
    if logo_url:
        html += f'<img src="{logo_url}" class="cover-logo"/>'
    html += f'<div class="cover-title">Rapport DockerAudit</div>'
    html += f'<div class="cover-agent">Agent : {agent_name}</div>'
    html += f'<div class="cover-date">Date du rapport : {report_date}</div>'
    html += '<div class="cover-intro">Ce rapport présente l\'état de sécurité de l\'hôte et des conteneurs Docker audités.</div>'
    html += '</div><div style="page-break-after: always;"></div>'
    # Vulnérabilités globales (host)
    html += '<h2>Vulnérabilités globales (Host)</h2>'
    html += '<table><tr><th>Vérification</th><th>Statut</th></tr>'
    for key, val in report_data['host'].items():
        status = val.get('status') if isinstance(val, dict) else val
        cls, txt = status_class(status)
        html += f'<tr><td>{key.replace("_", " ")}</td><td class="{cls}">{txt}</td></tr>'
    html += '</table>'
    # Un tableau par conteneur
    for cid, cdata in report_data['containers'].items():
        cname = cdata.get('container_name', cid)
        image = cdata.get('image', '')
        html += f'<h3>Conteneur : {cname} ({image})</h3>'
        html += '<table><tr><th>Vérification</th><th>Statut</th></tr>'
        for k, v in cdata.items():
            if k in ('container_name', 'image', 'running'):
                continue
            status = v.get('status') if isinstance(v, dict) and 'status' in v else (v if isinstance(v, bool) else None)
            cls, txt = status_class(status)
            html += f'<tr><td>{k.replace("_", " ")}</td><td class="{cls}">{txt}</td></tr>'
        running = cdata.get('running', None)
        if running is not None:
            cls, txt = status_class(running)
            txt = 'Oui' if running else 'Non'
            html += f'<tr><td>Conteneur en cours d\'exécution</td><td class="{cls}">{txt}</td></tr>'
        html += '</table>'
    # Légende visuelle
    html += '<div class="legend">'
    html += '<span class="status-ok"></span> = pas de vulnérabilité &nbsp; <br>'
    html += '<span class="status-ko"></span> = vulnérabilité détectée &nbsp; <br>'
    html += '<span class="status-skipped"></span> = vérification non applicable &nbsp; <br>'
    html += '<span class="status-info"></span> = information'
    html += '</div>'
    # CSS : NE PAS METTRE DE CSS EN DUR ICI, toujours charger depuis css_path !
    css = ''
    if css_path and os.path.exists(css_path):
        with open(css_path) as f:
            css = f.read()
    html = f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{html}</body></html>'
    return html

def html_to_pdf(html):
    pdf_io = BytesIO()
    HTML(string=html).write_pdf(pdf_io)
    pdf_io.seek(0)
    return pdf_io

# Exemple d'utilisation :
# from utils.pdf_report_html import generate_html_report, html_to_pdf
# html = generate_html_report(agent_name, report_date, report_data, logo_url="file:///chemin/absolu/logo.png", css_path="static/style/report.css")
# pdf_buffer = html_to_pdf(html)
# with open("rapport.pdf", "wb") as f:
#     f.write(pdf_buffer.read())

