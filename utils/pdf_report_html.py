from weasyprint import HTML
from io import BytesIO
import os
import re
from icecream import ic

# Mapping des vérifications pour des noms plus lisibles
VERIFICATION_MAPPING = {
    # Host checks
    'daemon_json_check': 'Configuration daemon.json',
    'docker_socket_check': 'Socket Docker',
    'docker_versions_check': 'Versions Docker',
    'rootless_check': 'Mode rootless',
    'os_versions_check': 'Versions OS',
    'docker_registry_check': 'Registre Docker',
    'ipv6_forwarding_check': 'Forwarding IPv6',
    
    # Container checks
    'docker_container_capabilities_check': 'Capacités du conteneur',
    'docker_container_registry_check': 'Registre d\'images',
    'docker_container_sensitives_check': 'Données sensibles',
    'docker_container_volumes_check': 'Volumes',
    'docker_container_ports_check': 'Ports exposés',
}

def highlight_linux_paths(text):
    """Détecte et marque les chemins Linux avec la classe CSS"""
    if not isinstance(text, str):
        return text
    
    # Pattern pour détecter les chemins Linux
    # Matche les chemins commençant par / et contenant des caractères typiques
    path_pattern = r'/[a-zA-Z0-9._/-]+'
    
    def replace_path(match):
        path = match.group(0)
        # Vérifier que c'est bien un chemin (pas juste un slash)
        if len(path) > 1 and not path.endswith('/'):
            return f'<span class="linux-path">{path}</span>'
        return path
    
    return re.sub(path_pattern, replace_path, text)

def status_class(status):
    if status is False:
        return 'status-ko', 'VULNÉRABLE'
    if status is True:
        return 'status-ok', 'SÉCURISÉ'
    if status is None:
        return 'status-skipped', 'NON VÉRIFIABLE'
    if status == 'success':
        return 'status-ok', 'SÉCURISÉ'
    if status == 'skipped':
        return 'status-skipped', 'IGNORÉ'
    if status == 'info':
        return 'status-info', 'INFO'
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
                    elif key == 'volumes':
                        if isinstance(value, list) and value:
                            # Traiter les volumes comme une liste de dictionnaires
                            volume_details = []
                            for vol in value:
                                if isinstance(vol, dict):
                                    source = vol.get('Source', 'N/A')
                                    destination = vol.get('Destination', 'N/A')
                                    volume_details.append(f"{source} → {destination}<br>")
                                    volume_details.append(f"Mode: {vol.get('Mode', '')}<br>")
                                else:
                                    volume_details.append(str(vol))
                            details.append(' '.join(volume_details))
                        else:
                            details.append("Aucun volume monté")
                    elif key == 'ports':
                        if isinstance(value, list) and value:
                            port_lines = []
                            for port in value:
                                if isinstance(port, dict):
                                    # Afficher tous les champs du dict sur une ligne, séparés par ', '
                                    port_lines.append(', '.join(f"{k}: {v}" for k, v in port.items()))
                                else:
                                    port_lines.append(str(port))
                            details.append('<br>'.join(port_lines))
                        else:
                            details.append("Aucun port exposé")
                    elif key == 'registry_type':
                        details.append(f"Type: {value}")
                    elif key == 'uses_private_registry':
                        details.append("Registre privé" if value else "Registre public")
                    elif key == 'local_version':
                        details.append(f"Version locale: {value}")
                    elif key == 'remote_version':
                        details.append(f"Version distante: {value}")
                    elif key == 'message':
                        # Essayer de parser le message comme JSON
                        try:
                            import json
                            msg_val = value
                            if isinstance(msg_val, str):
                                parsed = json.loads(msg_val)
                                if isinstance(parsed, list) and all(isinstance(p, dict) for p in parsed):
                                    port_lines = []
                                    for port in parsed:
                                        port_lines.append(', '.join(f"{k}: {v}" for k, v in port.items()))
                                    details.append('<br>'.join(port_lines))
                                else:
                                    details.append(msg_val)
                            else:
                                details.append(str(msg_val))
                        except Exception:
                            details.append(str(value))
                    else:
                        details.append(value)
            
            detail_text = '<br>'.join(details) if details else ''
            # Appliquer la mise en évidence des chemins Linux
            detail_text = highlight_linux_paths(detail_text)
            return cls, txt, detail_text
        else:
            # Dictionnaire sans status, afficher toutes les valeurs
            details = []
            for key, value in val.items():
                if isinstance(value, list):
                    details.append(f"{key}: {', '.join(value)}")
                else:
                    details.append(f"{key}: {value}")
            detail_text = '<br> '.join(details)
            # Appliquer la mise en évidence des chemins Linux
            detail_text = highlight_linux_paths(detail_text)
            return 'status-info', 'INFO', detail_text
    elif isinstance(val, list):
        detail_text = ', '.join(str(item) for item in val)
        # Appliquer la mise en évidence des chemins Linux
        detail_text = highlight_linux_paths(detail_text)
        return 'status-info', 'INFO', detail_text
    elif isinstance(val, str):
        # Essayer de parser le JSON string
        try:
            import json
            parsed = json.loads(val)
            return format_verification_value(parsed)
        except:
            # Appliquer la mise en évidence des chemins Linux
            highlighted_val = highlight_linux_paths(val)
            return 'status-info', 'INFO', highlighted_val
    else:
        cls, txt = status_class(val)
        return cls, txt, ''

def get_verification_name(key):
    """Retourne le nom lisible d'une vérification"""
    return VERIFICATION_MAPPING.get(key, key.replace('_', ' ').title())

def count_vuln_and_secure(report_data):
    vuln = 0
    secure = 0
    skipped = 0
    info = 1
    def count_in_dict(d):
        nonlocal vuln, secure, skipped, info
        for key, v in d.items():
            if isinstance(v, dict) and 'status' in v:
                if v['status'] is False:
                    vuln += 1
                elif v['status'] is True and key != 'running':
                    secure += 1
                elif v['status'] == "skipped":
                    skipped += 1
                elif v['status'] == 'info':
                    info += 1
            elif isinstance(v, dict):
                count_in_dict(v)
            elif isinstance(v, str):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, dict) and 'status' in parsed:
                        if parsed['status'] is False:
                            vuln += 1
                        elif parsed['status'] is True and key != 'running':
                            secure += 1
                        elif parsed['status'] == "skipped":
                            skipped += 1
                        elif parsed['status'] =='info':
                            info += 1
                except:
                    pass
    count_in_dict(report_data.get('host', {}))
    for cdata in report_data.get('containers', {}).values():
        count_in_dict(cdata)
    return vuln, secure, skipped, info

def generate_html_report(agent_name, report_date, report_data, logo_url=None, css_path=None):
    ic(report_data)
    vuln, secure, skipped, info = count_vuln_and_secure(report_data)
    # Page de couverture
    html = '<div class="cover">'
    if logo_url:
        html += f'<img src="{logo_url}" class="cover-logo"/>'
    html += f'<div class="cover-title">Rapport DockerAudit</div>'
    html += f'<div class="cover-agent">Agent : {agent_name}</div>'
    html += f'<div class="cover-date">Date du rapport : {report_date}</div>'
    html += '<div class="cover-intro">Ce rapport présente l\'état de sécurité de l\'hôte et des conteneurs Docker audités.</div>'
    # Tableau de synthèse sur la première page
    html += '<div class="section" style="margin-top:2em<br>">'
    html += '<h2 style="font-size:1.3em<br>">Résumé des vérifications</h2>'
    html += '<table class="security-table" style="max-width:400px<br>margin-bottom:2em<br>">'
    html += '<thead><tr><th>Type</th><th>Nombre</th></tr></thead>'
    html += f'<tr><td class="status-ko">Vulnérabilités</td><td style="text-align:center<br>font-weight:bold<br>">{vuln}</td></tr>'
    html += f'<tr><td class="status-ok">Sécurisées</td><td style="text-align:center<br>font-weight:bold<br>">{secure}</td></tr>'
    html += f'<tr><td class="status-skipped">Ignorées</td><td style="text-align:center<br>font-weight:bold<br>">{skipped}</td></tr>'
    html += f'<tr><td class="status-info">Informations</td><td style="text-align:center<br>font-weight:bold<br>">{info}</td></tr>'
    html += '</table>'
    html += '</div>'
    html += '</div><div style="page-break-after: always<br>"></div>'

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
            detail_txt = 'En cours d\'exécution' if running else 'Arrêté'
            html += f'<tr><td class="verification-name">État du conteneur</td><td class="status-info">INFO</td><td class="detail">{detail_txt}</td></tr>'
        html += '</tbody></table>'

        # Générer les recommandations pour les checks vulnérables
        recommandations = []
        for k, v in cdata.items():
            if k in ('container_name', 'image', 'running'):
                continue
            # On gère les cas où v est un dict avec status
            if isinstance(v, dict) and v.get('status', None) is False:
                # Utiliser le message si présent
                msg = v.get('message')
                if msg:
                    recommandations.append(msg)
                else:
                    # Phrase générique selon le type de check
                    if 'volume' in k:
                        recommandations.append("Vérifiez les permissions des volumes montés.")
                    elif 'port' in k:
                        recommandations.append("Un ou plusieurs ports sont exposés publiquement. Restreindre l'accès si possible.")
                    elif 'rootless' in k:
                        recommandations.append("Le conteneur fonctionne avec l'utilisateur root. Passez en mode rootless.")
                    elif 'capabilities' in k:
                        recommandations.append("Vérifiez les capacités du conteneur.")
                    elif 'registry' in k:
                        recommandations.append("Vérifiez les registres utilisés par le conteneur.")
                    elif 'sensitives' in k:
                        recommandations.append("Vérifiez les données sensibles du conteneur.")
                    else:
                        recommandations.append(f"Vulnérabilité détectée sur : {get_verification_name(k)}.")
        # Afficher le tableau des recommandations s'il y en a
        if recommandations:
            html += '<div class="reco-section" style="margin-top:1em">'
            html += '<table class="reco-table" style="border-collapse: collapse; width: 100%; font-size: 0.95em;">'
            html += '<thead><tr style="background-color: #ffecec;"><th style="border: 1px solid #f5c2c2; padding: 6px; text-align: left;">Recommandations</th></tr></thead>'
            html += '<tbody>'
            for reco in recommandations:
                html += f'<tr><td style="border: 1px solid #f5c2c2; padding: 6px;">{reco}</td></tr>'
            html += '</tbody></table></div>'
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

