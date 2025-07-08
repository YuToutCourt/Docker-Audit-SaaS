import os
from icecream import ic
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import requests
from flask_jwt_extended import JWTManager, jwt_required
from werkzeug.security import generate_password_hash

from api.route import api
from database.database import Database
from entity.agent import Agent
from entity.user import User
from functools import wraps
from pki.certificate_manager import generate_entreprise_pki
from entity.company import Company


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user') or not session.get('is_admin'):
            flash("Accès réservé à l'administration.", "error")
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
            agent.next_scan_date_ = request.form.get('next_scan')
            agent.enabled = 1 if request.form.get('enabled') == 'on' else 0
            db.session.commit()
            success = 'Configuration mise à jour avec succès.'
        except Exception as e:
            db.session.rollback()
            error = "Erreur lors de la mise à jour de l'agent."
    response = render_template('agent.html', agent=agent, success=success, error=error)
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
            
@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin_panel.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    db = Database()
    users = db.session.query(User).all()
    # Récupérer tous les id_company uniques
    company_ids = list(set([u.id_company for u in users if u.id_company]))
    # Récupérer les sociétés
    companies = db.session.query(Company).filter(Company.id_company.in_(company_ids)).all() if company_ids else []
    company_names = {c.id_company: c.name for c in companies}
    db.close()
    return render_template('admin_users.html', users=users, company_names=company_names)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        id_company = request.form['id_company']

        db = Database()
        if db.session.query(User).filter_by(username=username).first():
            db.close()
            flash("Nom d'utilisateur déjà utilisé.", "error")
            return redirect(url_for('admin_create_user'))

        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            enabled=1,
            is_admin=0,  # Toujours créer des utilisateurs non-admin
            id_company=id_company
        )
        db.session.add(user)
        db.session.commit()
        db.close()
        flash("Utilisateur créé avec succès.", "success")
        return redirect(url_for('admin_users'))
    return render_template('admin_create_user.html')

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    db = Database()
    user = db.session.query(User).filter_by(id=user_id).first()
    if user and user.username == session.get('user'):
        db.close()
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
        return redirect(url_for('admin_users'))
    if not user:
        db.close()
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    db.close()
    flash("Utilisateur supprimé avec succès.", "success")
    return redirect(url_for('admin_users'))

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

@app.route('/admin/companies', methods=['GET', 'POST'])
@admin_required
def admin_companies():
    db = Database()
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            db.close()
            flash("Nom requis.", "error")
            return redirect(url_for('admin_companies'))
        # Générer la CA pour l'entreprise
        ca_id = generate_entreprise_pki(name)
        # Créer l'entreprise avec la CA
        company = Company(name=name, company_pki_id=ca_id)
        db.session.add(company)
        db.session.commit()
        db.close()
        flash("Entreprise créée avec succès.", "success")
        return redirect(url_for('admin_companies'))
    companies = db.session.query(Company).all()
    db.close()
    return render_template('admin_company.html', companies=companies)

@app.route('/admin/companies/delete/<int:company_id>', methods=['POST'])
@admin_required
def admin_delete_company(company_id):
    db = Database()
    company = db.session.query(Company).filter_by(id_company=company_id).first()
    if not company:
        db.close()
        flash("Entreprise introuvable.", "error")
        return redirect(url_for('admin_companies'))
    db.session.delete(company)
    db.session.commit()
    db.close()
    flash("Entreprise supprimée avec succès.", "success")
    return redirect(url_for('admin_companies'))

if  __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
