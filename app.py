import os
from icecream import ic
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import jwt as PyJWT
import datetime

from api.route import api, token_required
from database.database import Database
from entity.agent import Agent

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

agents = [
    {'id': 1, 'name': 'Agent-prod-01', 'status': 'actif', 'last_scan': '2025-04-29 14:23'},
    {'id': 2, 'name': 'Agent-staging', 'status': 'inactif', 'last_scan': '2025-04-28 09:10'},
    {'id': 3, 'name': 'Agent-test', 'status': 'actif', 'last_scan': '2025-04-30 08:45'},
]

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/dashboard')
@token_required
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
@token_required
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
            'http://127.0.0.1:2424/api/login',
            json={'username': username, 'password': password}
        )

        ic(response.status_code)

        if response.status_code == 200:
            data = response.json()
            session.clear()
            session['user'] = username
            session['token'] = data['token']
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
            



if  __name__ == '__main__':
    app.run(debug=True, port=2424)
