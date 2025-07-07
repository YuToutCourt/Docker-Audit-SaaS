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


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
jwt = JWTManager(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user') or not session.get('is_admin'):
            flash("It is admin access !", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Tableau de bord utilisateur : liste des agents et leurs statuts."""
    if 'id_company' not in session:
        flash('Session expirée, veuillez vous reconnecter.', 'error')
        return redirect(url_for('login'))

    db = Database()
    agents = db.session.query(Agent).filter_by(id_company=session['id_company']).all()
    db.close()
    return render_template('dashboard.html', agents=agents)


@app.route('/agent/<int:agent_id>', methods=['GET', 'POST'])
def agent(agent_id):

    if 'id_company' not in session:
        flash('Session expirée, veuillez vous reconnecter.', 'error')
        return redirect(url_for('login'))

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
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Échec de l'authentification
            error = 'Identifiant ou mot de passe invalide.'

    # Pour GET et POST avec erreur, on affiche le formulaire
    return render_template('login.html', error=error)

@app.route('/logout')
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
    db.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@admin_required
def admin_create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        is_admin = 1 if 'is_admin' in request.form else 0
        id_company = request.form['id_company']

        db = Database()
        if db.session.query(User).filter_by(username=username).first():
            db.close()
            flash("Username already used", "error")
            return redirect(url_for('admin_create_user'))

        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            password=hashed_password,
            email=email,
            enabled=1,
            is_admin=is_admin,
            id_company=id_company
        )
        db.session.add(user)
        db.session.commit()
        db.close()
        flash("User created", "success")
        return redirect(url_for('admin_users'))
    return render_template('admin_create_user.html')


@app.route('/generate_certificate')
def generate_certificate():
    company_name = session.get('user', 'Entreprise')
    generate_entreprise_pki(company_name)
    cert_path = "ca_cert.pem"
    if os.path.exists(cert_path):
        return send_file(cert_path, as_attachment=True)
    else:
        flash("Erreur lors de la génération du certificat.", "error")
        return redirect(url_for('dashboard'))


if  __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
