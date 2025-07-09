import base64
import os
from icecream import ic
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import requests
from flask_jwt_extended import JWTManager
import json
import hashlib
from Crypto.Cipher import AES

from api.route import api
from database.database import Database
from entity.agent import Agent
from functools import wraps
from entity.report import Report
from utils.pdf_report import create_pdf_report
from utils.date_utils import compute_next_scans
from admin.route import admin

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(admin, url_prefix='/admin')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash("Veuillez vous connecter.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord utilisateur : liste des agents et leurs statuts."""

    db = Database()
    agents = db.session.query(Agent).filter_by(id_company=session['id_company']).all()
    db.close()
    return render_template('dashboard.html', agents=agents)


@app.route('/agent/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def agent(agent_id):
    db = Database()
    agent = db.session.query(Agent).filter_by(id_agent=agent_id, id_company=session['id_company']).first()
    success = error = None

    if not agent:
        db.close()
        flash('Agent non trouvé ou accès interdit.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            agent.next_scan_date_ = compute_next_scans(agent.next_scan_date_, agent.scan_interval)[0]
            agent.enabled = 1 if request.form.get('enabled') == 'on' else 0
            # Nouveau : récupérer chaque champ
            days = int(request.form.get('scan_days', 0))
            hours = int(request.form.get('scan_hours', 0))
            minutes = int(request.form.get('scan_minutes', 0))
            # seconds = int(request.form.get('scan_seconds', 0))
            scan_interval = days*86400 + hours*3600 + minutes*60
            if scan_interval >= 3600:
                agent.scan_interval = scan_interval
            db.session.commit()
            success = 'Configuration mise à jour avec succès.'
        except Exception as e:
            ic(e)
            db.session.rollback()
            error = "Erreur lors de la mise à jour de l'agent."
    # Calcul du prochain scan prévu et du scan suivant via utilitaire
    prochain_scan, scan_suivant = compute_next_scans(agent.next_scan_date_, agent.scan_interval)
    # Pour l'affichage (décomposer scan_interval)
    scan_days = scan_hours = scan_minutes = scan_seconds = 0
    if agent.scan_interval:
        total = int(agent.scan_interval)
        scan_days = total // 86400
        total %= 86400
        scan_hours = total // 3600
        total %= 3600
        scan_minutes = total // 60
        scan_seconds = total % 60
    reports = db.session.query(Report).filter_by(id_agent=agent_id).order_by(Report.date_.desc()).all()
    ic(scan_suivant)
    response = render_template(
        'agent.html',
        agent=agent,
        reports=reports,
        success=success,
        error=error,
        prochain_scan=prochain_scan,
        scan_suivant=scan_suivant,
        scan_days=scan_days,
        scan_hours=scan_hours,
        scan_minutes=scan_minutes
    )
    db.close()
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Appel à l'API pour l'authentification
        response = requests.post(
            'http://127.0.0.1:80/api/login',
            json={'username': username, 'password': password}
        )

        ic(response.status_code)

        if response.status_code == 200:
            data = response.json()
            session.clear()
            session['user'] = username
            session['is_admin'] = data.get('is_admin', 0)
            session['id_company'] = data['id_company']
            session['access_token'] = data['access_token']
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Échec de l'authentification
            error = 'Identifiant ou mot de passe invalide.'

    # Pour GET et POST avec erreur, on affiche le formulaire
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    """Déconnexion de l'utilisateur."""
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))


@app.route('/new_agent', methods=['POST'])
@login_required
def new_agent():

    name = request.form['name']

    response = requests.post(
        'http://127.0.0.1:80/api/add_agent',
        json={'name': name},
        headers={'Authorization': f'Bearer {session["access_token"]}'}
    )

    ic(response.status_code)
    if response.status_code == 201:
        flash('Création de l\'agent réussie.', 'success')
    else:
        flash('Échec de la création de l\'agent.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/agent/delete/<int:agent_id>', methods=['POST'])
@login_required
def delete_agent(agent_id):
    db = Database()
    agent = db.session.query(Agent).filter_by(id_agent=agent_id, id_company=session['id_company']).first()
    if not agent:
        db.close()
        flash("Agent introuvable ou accès interdit.", "error")
        return redirect(url_for('dashboard'))
    db.session.delete(agent)
    db.session.commit()
    db.close()
    flash("Agent supprimé avec succès.", "success")
    return redirect(url_for('dashboard'))

@app.route('/agent/<int:agent_id>/download_certificate')
@login_required
def download_agent_certificate(agent_id):
    """Télécharger le certificat public de l'agent."""
    
    db = Database()
    agent = db.session.query(Agent).filter_by(id_agent=agent_id, id_company=session['id_company']).first()
    
    if not agent:
        db.close()
        flash('Agent non trouvé ou accès interdit.', 'error')
        return redirect(url_for('dashboard'))
    
    if not agent.public_key:
        db.close()
        flash('Aucun certificat trouvé pour cet agent.', 'error')
        return redirect(url_for('agent', agent_id=agent_id))
    
    try:
        # Créer un fichier temporaire en mémoire avec le certificat
        from io import BytesIO
        certificate_data = agent.public_key.encode('utf-8')
        certificate_stream = BytesIO(certificate_data)
        certificate_stream.seek(0)
        
        db.close()
        
        # Retourner le fichier en tant que téléchargement
        return send_file(
            certificate_stream,
            as_attachment=True,
            download_name=f"{agent.name}_certificate.pem",
            mimetype='application/x-pem-file'
        )
        
    except Exception as e:
        db.close()
        flash(f'Erreur lors du téléchargement du certificat: {str(e)}', 'error')
        return redirect(url_for('agent', agent_id=agent_id))

@app.route('/agent/<int:agent_id>/download_report/<int:id_report>', methods=['POST'])
@login_required
def download_agent_report(agent_id, id_report):
    password = request.form.get('report_password')
    if not password:
        flash("Mot de passe requis.", "error")
        return redirect(url_for('agent', agent_id=agent_id))
    db = Database()
    agent = db.session.query(Agent).filter_by(id_agent=agent_id, id_company=session['id_company']).first()
    report = db.session.query(Report).filter_by(id_report=id_report, id_agent=agent_id).first()
    if not agent or not report:
        db.close()
        flash("Rapport ou agent introuvable.", "error")
        return redirect(url_for('agent', agent_id=agent_id))
    key = hashlib.sha256(password.encode()).digest()
    iv = bytes.fromhex(report.salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(report.dataB64))
    db.close()
    # Enlève le padding PKCS7 si besoin
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    try:
        report_data = json.loads(decrypted.decode('utf-8'))
    except Exception:
        flash("Déchiffrement ou format du rapport invalide.", "error")
        return redirect(url_for('agent', agent_id=agent_id))
    buffer = create_pdf_report(agent.name, report.date_, report_data)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"rapport_{report.date_}.pdf",
        mimetype='application/pdf'
    )

if  __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
