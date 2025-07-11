from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from services.agent_service import AgentService
from services.auth_service import AuthService
from functools import wraps
import secrets
import time

main_bp = Blueprint('main', __name__)

def generate_csrf_token():
    """Génère un token CSRF pour protéger les formulaires"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """Valide le token CSRF"""
    return token == session.get('csrf_token')

@main_bp.route("/")
def index():
    """Page d'accueil"""
    return render_template("index.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion"""
    if request.method == "POST":
        # Validation CSRF
        csrf_token = request.form.get('csrf_token')
        if not validate_csrf_token(csrf_token):
            flash("Erreur de sécurité. Veuillez réessayer.", "error")
            return render_template("login.html", csrf_token=generate_csrf_token())
        
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Validation des entrées
        if not username or not password:
            flash("Tous les champs sont requis", "error")
            return render_template("login.html", csrf_token=generate_csrf_token())
        
        user = AuthService.authenticate_user(username, password)
        if user:
            # Régénération de l'ID de session pour prévenir la fixation de session
            session.clear()
            # Créer un nouveau token de session en modifiant la session
            session['_fresh'] = True
            session['_id'] = secrets.token_hex(32)
            
            session["user_id"] = user.id_user
            session["user"] = user.username
            session["is_admin"] = user.is_admin
            session["id_company"] = user.id_company
            session["login_time"] = time.time()
            session["csrf_token"] = secrets.token_hex(32)
            
            flash("Connexion réussie !", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Identifiants invalides", "error")
    
    return render_template("login.html", csrf_token=generate_csrf_token())

@main_bp.route("/logout")
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for("main.index"))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash("Veuillez vous connecter.", "error")
            return redirect(url_for('main.login'))
        
        # Vérification de l'expiration de session (1 heure)
        login_time = session.get('login_time', 0)
        if time.time() - login_time > 3600:  # 1 heure
            session.clear()
            flash("Votre session a expiré. Veuillez vous reconnecter.", "error")
            return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Tableau de bord utilisateur"""
    company_id = session.get("id_company")
    
    agents = AgentService.get_agents_by_company(company_id)
    return render_template("dashboard.html", agents=agents, csrf_token=generate_csrf_token())

@main_bp.route("/agents")
@login_required
def agents():
    """Page des agents"""
    company_id = session.get("id_company")
    
    agents = AgentService.get_agents_by_company(company_id)
    return render_template("agents.html", agents=agents, csrf_token=generate_csrf_token())

@main_bp.route("/reports")
@login_required
def reports():
    """Page des rapports"""
    company_id = session.get("id_company")
    
    reports = AgentService.get_all_reports_by_company(company_id)

    return render_template("reports.html", reports=reports, csrf_token=generate_csrf_token())

@main_bp.route("/new_agent", methods=["POST"])
@login_required
def new_agent():
    """Créer un nouvel agent"""
    # Validation CSRF
    csrf_token = request.form.get('csrf_token')
    if not validate_csrf_token(csrf_token):
        flash("Erreur de sécurité. Veuillez réessayer.", "error")
        return redirect(url_for("main.dashboard"))
    
    company_id = session.get("id_company")
    
    name = request.form.get("name")
    if not name:
        flash("Le nom de l'agent est requis", "error")
        return redirect(url_for("main.dashboard"))
    
    # Validation et nettoyage du nom
    name = name.strip()
    if len(name) > 100:  # Limite de longueur
        flash("Le nom de l'agent est trop long", "error")
        return redirect(url_for("main.dashboard"))
    
    success = AgentService.create_agent(name, company_id)
    if success:
        flash("Agent créé avec succès", "success")
    else:
        flash("Erreur lors de la création de l'agent", "error")
    
    return redirect(url_for("main.dashboard")) 