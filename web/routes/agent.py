from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, session
from services.agent_service import AgentService
from utils.date_utils import compute_next_scans
from utils.pdf_report import create_pdf_report
import base64
import hashlib
import json
from Crypto.Cipher import AES
from io import BytesIO
from functools import wraps
from icecream import ic

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash("Veuillez vous connecter.", "error")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

agent_bp = Blueprint('web_agent', __name__)

@agent_bp.route("/agent/<int:agent_id>", methods=["GET", "POST"])
@login_required
def agent_detail(agent_id):
    """Page de détail d'un agent"""
    company_id = session.get("id_company")
    
    agent_data = AgentService.get_agent_by_id_and_company(agent_id, company_id)
    if not agent_data:
        flash("Agent non trouvé ou accès interdit", "error")
        return redirect(url_for("main.dashboard"))
    
    # Convertir le dict en objet pour compatibilité
    class AgentObj:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)
    
    agent_obj = AgentObj(agent_data)
    
    success = error = None
    
    if request.method == "POST":
        # Logique de mise à jour de l'agent
        try:
            # Calculer le nouvel intervalle
            days = int(request.form.get('scan_days', 0))
            hours = int(request.form.get('scan_hours', 0))
            minutes = int(request.form.get('scan_minutes', 0))
            scan_interval = days*86400 + hours*3600 + minutes*60
            
            if scan_interval >= 3600:
                update_data = {
                    'scan_interval': scan_interval,
                    'enabled': 1 if request.form.get('enabled') == 'on' else 0
                }
                
                success_update = AgentService.update_agent(agent_id, company_id, update_data)
                if success_update:
                    flash("Configuration mise à jour avec succès.", "success")
                    return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))
                else:
                    error = "Erreur lors de la mise à jour de l'agent."
            else:
                error = "L'intervalle minimum est de 1 heure."
        except Exception as e:
            error = f"Erreur lors de la mise à jour: {str(e)}"
    
    # Calcul du prochain scan
    if agent_obj.scan_interval:
        prochain_scan, scan_suivant = compute_next_scans(agent_obj.next_scan_date_, agent_obj.scan_interval)
    else:
        prochain_scan = scan_suivant = None
    
    # Décomposer scan_interval pour l'affichage
    scan_days = scan_hours = scan_minutes = scan_seconds = 0
    if agent_obj.scan_interval:
        total = int(agent_obj.scan_interval)
        scan_days = total // 86400
        total %= 86400
        scan_hours = total // 3600
        total %= 3600
        scan_minutes = total // 60
        scan_seconds = total % 60
    
    # Récupérer les rapports
    reports = AgentService.get_agent_reports(agent_id, company_id)
    
    reports = sorted(reports, key=lambda r: r['date_'] if isinstance(r, dict) else r.date_, reverse=True)

    str_scan_suivant = agent_obj.next_scan_date_.strftime('%Y-%m-%d %H:%M:%S')

    return render_template(
        'agent.html',
        agent=agent_obj,
        reports=reports,
        success=success,
        error=error,
        prochain_scan=prochain_scan,
        scan_suivant=str_scan_suivant,
        scan_days=scan_days,
        scan_hours=scan_hours,
        scan_minutes=scan_minutes
    )

@agent_bp.route("/agent/<int:agent_id>/download_certificate")
@login_required
def download_agent_certificate(agent_id):
    """Télécharger le certificat public de l'agent"""
    company_id = session.get("id_company")
    
    certificate_data = AgentService.get_agent_certificate(agent_id, company_id)
    if not certificate_data or not certificate_data.get("certificate"):
        flash("Certificat non trouvé pour cet agent", "error")
        return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))
    
    try:
        certificate_stream = BytesIO(certificate_data["certificate"].encode('utf-8'))
        certificate_stream.seek(0)
        
        return send_file(
            certificate_stream,
            as_attachment=True,
            download_name=f"agent_{agent_id}_certificate.pem",
            mimetype='application/x-pem-file'
        )
    except Exception as e:
        ic(e)
        flash(f"Erreur lors du téléchargement", "error")
        return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))

@agent_bp.route("/agent/<int:agent_id>/download_report/<int:report_id>", methods=["POST"])
@login_required
def download_agent_report(agent_id, report_id):
    """Télécharger un rapport déchiffré"""
    company_id = session.get("id_company")
    
    password = request.form.get('report_password')
    if not password:
        flash("Mot de passe requis", "error")
        return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))
    
    # Récupérer le rapport
    from entity.report import Report
    from database.database import Database
    
    db = Database()
    report = db.session.query(Report).filter_by(
        id_report=report_id, 
        id_agent=agent_id, 
        id_company=company_id
    ).first()
    
    if not report:
        db.close()
        flash("Rapport non trouvé", "error")
        return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))
    
    try:
        # Déchiffrement
        key = hashlib.sha256(password.encode()).digest()
        iv = bytes.fromhex(report.salt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(base64.b64decode(report.dataB64))
        
        # Enlever le padding PKCS7
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]
        
        report_data = json.loads(decrypted.decode('utf-8'))
        
        agent_name = AgentService.get_agent_name_by_id(agent_id)

        # Créer le PDF via html
        from utils.pdf_report_html import html_to_pdf, generate_html_report

        import os
        logo_path = os.path.abspath("static/images/logo.png")
        logo_url = f"file://{logo_path}"
        css_path = "static/style/report.css"

        html = generate_html_report(
            agent_name,
            report.date_,
            report_data,
            logo_url=logo_url,
            css_path=css_path
        )
        buffer = html_to_pdf(html)
        
        db.close()
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"rapport_{report.date_}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        db.close()
        ic(e)
        flash(f"Impossible de déchiffrer le rapport", "error")
        return redirect(url_for("web_agent.agent_detail", agent_id=agent_id))

@agent_bp.route("/agent/delete/<int:agent_id>", methods=["POST"])
@login_required
def delete_agent(agent_id):
    """Supprimer un agent"""
    company_id = session.get("id_company")
    
    success = AgentService.delete_agent(agent_id, company_id)
    if success:
        flash("Agent supprimé avec succès", "success")
    else:
        flash("Erreur lors de la suppression de l'agent", "error")
    
    return redirect(url_for("main.dashboard")) 