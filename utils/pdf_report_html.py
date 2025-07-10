from weasyprint import HTML
from io import BytesIO
import os
from icecream import ic

# Mapping des vérifications pour des noms plus lisibles
VERIFICATION_MAPPING = {
    # Host checks
    'daemon_json_check': 'Configuration daemon.json',
    'docker_socket_check': 'Accès socket Docker',
    'docker_versions_check': 'Versions Docker',
    'rootless_check': 'Mode rootless',
    
    # Container checks
    'docker_container_capabilities_check': 'Capacités du conteneur',
    'docker_container_registry_check': 'Registre d\'images',
    'docker_container_sensitives_check': 'Données sensibles',
}

def status_class(status):
    if status is False:
        return 'status-ko', '❌ VULNÉRABLE'
    if status is True:
        return 'status-ok', '✅ SÉCURISÉ'
    if status is None:
        return 'status-skipped', '⚠️ NON VÉRIFIABLE'
    if status == 'success':
        return 'status-ok', '✅ SÉCURISÉ'
    if status == 'skipped':
        return 'status-skipped', '⏭️ IGNORÉ'
    if status == 'info':
        return 'status-info', 'ℹ️ INFO'
    return 'status-unknown', str(status)

def format_verification_value(val):
    """Formate une valeur de vérification pour l'affichage"""
    if isinstance(val, dict):
        # Si c'est un dictionnaire avec un status
        if 'status' in val:
            status = val.get('status')
            cls, txt = status_class(status)
            
            # Extraire les détails
            details = []
            for key, value in val.items():
                if key != 'status':
                    if key == 'capabilities':
                        if value is None:
                            details.append("Aucune capacité spéciale")
                        elif isinstance(value, list) and value:
                            details.append(f"Capacités: {', '.join(value)}")
                        else:
                            details.append("Aucune capacité spéciale")
                    elif key == 'sensitive_data':
                        if isinstance(value, list) and value:
                            details.append(', '.join(value))
                        else:
                            details.append("Aucune donnée sensible détectée")
                    elif key == 'registry_type':
                        details.append(f"Type: {value}")
                    elif key == 'uses_private_registry':
                        details.append("Registre privé" if value else "Registre public")
                    elif key == 'local_version':
                        details.append(f"Version locale: {value}")
                    elif key == 'remote_version':
                        details.append(f"Version distante: {value}")
                    elif key == 'message':
                        details.append(f"Message: {value}")
                    else:
                        details.append(f"{key}: {value}")
            
            detail_text = '; '.join(details) if details else ''
            return cls, txt, detail_text
        else:
            # Dictionnaire sans status, afficher toutes les valeurs
            details = []
            for key, value in val.items():
                if isinstance(value, list):
                    details.append(f"{key}: {', '.join(value)}")
                else:
                    details.append(f"{key}: {value}")
            return 'status-info', 'ℹ️ INFO', '; '.join(details)
    elif isinstance(val, list):
        return 'status-info', 'ℹ️ INFO', ', '.join(str(item) for item in val)
    elif isinstance(val, str):
        # Essayer de parser le JSON string
        try:
            import json
            parsed = json.loads(val)
            return format_verification_value(parsed)
        except:
            return 'status-info', 'ℹ️ INFO', val
    else:
        cls, txt = status_class(val)
        return cls, txt, ''

def get_verification_name(key):
    """Retourne le nom lisible d'une vérification"""
    return VERIFICATION_MAPPING.get(key, key.replace('_', ' ').title())

def count_vuln_and_secure(report_data):
    vuln = 0
    secure = 0
    def count_in_dict(d):
        nonlocal vuln, secure
        for v in d.values():
            if isinstance(v, dict) and 'status' in v:
                if v['status'] is False:
                    vuln += 1
                elif v['status'] is True:
                    secure += 1
            elif isinstance(v, dict):
                count_in_dict(v)
            elif isinstance(v, str):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, dict) and 'status' in parsed:
                        if parsed['status'] is False:
                            vuln += 1
                        elif parsed['status'] is True:
                            secure += 1
                except:
                    pass
    count_in_dict(report_data.get('host', {}))
    for cdata in report_data.get('containers', {}).values():
        count_in_dict(cdata)
    return vuln, secure

def generate_html_report(agent_name, report_date, report_data, logo_url=None, css_path=None):
    ic(report_data)
    vuln, secure = count_vuln_and_secure(report_data)
    # Page de couverture
    html = '<div class="cover">'
    if logo_url:
        html += f'<img src="{logo_url}" class="cover-logo"/>'
    html += f'<div class="cover-title">Rapport DockerAudit</div>'
    html += f'<div class="cover-agent">Agent : {agent_name}</div>'
    html += f'<div class="cover-date">Date du rapport : {report_date}</div>'
    html += '<div class="cover-intro">Ce rapport présente l\'état de sécurité de l\'hôte et des conteneurs Docker audités.</div>'
    # Tableau de synthèse sur la première page
    html += '<div class="section" style="margin-top:2em;">'
    html += '<h2 style="font-size:1.3em;">Résumé des vérifications</h2>'
    html += '<table class="security-table" style="max-width:400px;margin-bottom:2em;">'
    html += '<thead><tr><th>Type</th><th>Nombre</th></tr></thead>'
    html += f'<tr><td class="status-ko">Vulnérabilités</td><td style="text-align:center;font-weight:bold;">{vuln}</td></tr>'
    html += f'<tr><td class="status-ok">Sécurisées</td><td style="text-align:center;font-weight:bold;">{secure}</td></tr>'
    html += '</table>'
    html += '</div>'
    html += '</div><div style="page-break-after: always;"></div>'

    # Vulnérabilités globales (host)
    html += '<div class="section">'
    html += '<h2>🔍 Vulnérabilités globales (Host)</h2>'
    html += '<table class="security-table">'
    html += '<thead><tr><th>Vérification</th><th>Statut</th><th>Détail</th></tr></thead>'
    html += '<tbody>'
    for key, val in report_data['host'].items():
        verification_name = get_verification_name(key)
        cls, status_txt, detail_txt = format_verification_value(val)
        html += f'<tr><td class="verification-name">{verification_name}</td><td class="{cls}">{status_txt}</td><td class="detail">{detail_txt}</td></tr>'
    html += '</tbody></table>'
    html += '</div>'
    
    # Un tableau par conteneur
    for cid, cdata in report_data['containers'].items():
        cname = cdata.get('container_name', cid)
        image = cdata.get('image', '')
        html += f'<div class="section">'
        html += f'<h3>🐳 Conteneur : {cname}</h3>'
        html += f'<div class="container-info">Image : {image}</div>'
        html += '<table class="security-table">'
        html += '<thead><tr><th>Vérification</th><th>Statut</th><th>Détail</th></tr></thead>'
        html += '<tbody>'
        for k, v in cdata.items():
            if k in ('container_name', 'image', 'running'):
                continue
            verification_name = get_verification_name(k)
            cls, status_txt, detail_txt = format_verification_value(v)
            html += f'<tr><td class="verification-name">{verification_name}</td><td class="{cls}">{status_txt}</td><td class="detail">{detail_txt}</td></tr>'
        
        # État du conteneur
        running = cdata.get('running', None)
        if running is not None:
            cls, txt = status_class(running)
            status_txt = txt
            detail_txt = 'En cours d\'exécution' if running else 'Arrêté'
            html += f'<tr><td class="verification-name">État du conteneur</td><td class="{cls}">{status_txt}</td><td class="detail">{detail_txt}</td></tr>'
        html += '</tbody></table>'
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

