from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from services.agent_service import AgentService
from services.auth_service import AuthService
from functools import wraps

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """Page d'accueil"""
    return render_template("index.html")

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Page de connexion"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = AuthService.authenticate_user(username, password)
        if user:
            session["user_id"] = user.id_user
            session["user"] = user.username  # Changé de "username" à "user"
            session["is_admin"] = user.is_admin
            session["id_company"] = user.id_company
            flash("Connexion réussie !", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Identifiants invalides", "error")
    
    return render_template("login.html")

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
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Tableau de bord utilisateur"""
    company_id = session.get("id_company")
    
    agents = AgentService.get_agents_by_company(company_id)
    return render_template("dashboard.html", agents=agents)

@main_bp.route("/agents")
@login_required
def agents():
    """Page des agents"""
    company_id = session.get("id_company")
    
    agents = AgentService.get_agents_by_company(company_id)
    return render_template("agents.html", agents=agents)

@main_bp.route("/reports")
@login_required
def reports():
    """Page des rapports"""
    company_id = session.get("id_company")
    
    reports = AgentService.get_all_reports_by_company(company_id)

    return render_template("reports.html", reports=reports)

@main_bp.route("/new_agent", methods=["POST"])
@login_required
def new_agent():
    """Créer un nouvel agent"""
    company_id = session.get("id_company")
    
    name = request.form.get("name")
    if not name:
        flash("Le nom de l'agent est requis", "error")
        return redirect(url_for("main.dashboard"))
    
    success = AgentService.create_agent(name, company_id)
    if success:
        flash("Agent créé avec succès", "success")
    else:
        flash("Erreur lors de la création de l'agent", "error")
    
    return redirect(url_for("main.dashboard")) 