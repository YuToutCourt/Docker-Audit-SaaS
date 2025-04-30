import os
from icecream import ic
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

from api.route import api, token_required

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
    # TODO : Remplacez cet exemple par un vrai appel à votre base de données
    return render_template('dashboard.html', agents=agents)


@app.route('/agent/<int:agent_id>')
@token_required
def agent(agent_id):
    """Page de détails d'un agent."""
    # TODO : Remplacez cet exemple par un vrai appel à votre base de données
    
    agent = next((agent for agent in agents if agent['id'] == agent_id), None)
    if agent is None:
        flash('Agent non trouvé.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('agent.html', agent=agent)


@app.route('/login', methods=['GET'])
def login():
    """Page de connexion."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # TODO : remplacez cette vérification par votre logique (BDD, LDAP, etc.)
        if username == 'admin' and password == 'password':
            # Authentification réussie
            session.clear()
            session['user'] = username
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))  # ou la page d’accueil de l’utilisateur
        else:
            # Échec de l’authentification
            error = 'Identifiant ou mot de passe invalide.'

    # Pour GET et POST avec erreur, on affiche le formulaire
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Déconnexion de l’utilisateur."""
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))
            



if  __name__ == '__main__':
    app.run(debug=True, port=2424)
