from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from services.admin_service import AdminService
from services.auth_service import AuthService
from validator.validator import Validator
from functools import wraps

admin_bp = Blueprint('web_admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            flash("Veuillez vous connecter.", "error")
            return redirect(url_for('main.login'))
        if not session.get('is_admin'):
            flash("Accès admin requis", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    """Tableau de bord admin"""
    stats = AdminService.get_global_stats()
    return render_template("admin_panel.html", stats=stats)

@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    """Gestion des utilisateurs"""
    users = AdminService.get_all_users()
    companies = AdminService.get_all_companies()
    
    # Créer un dictionnaire des noms d'entreprises
    company_names = {company['id_company']: company['name'] for company in companies}
    
    return render_template("admin_users.html", users=users, companies=companies, company_names=company_names)

@admin_bp.route("/admin/users", methods=["POST"])
@admin_required
def admin_create_user():
    """Créer un utilisateur"""
    username = request.form.get("username")
    password = request.form.get("password")
    company_id = request.form.get("id_company")
    email = request.form.get("email")
    
    try:
        Validator().check_param(username=username, password=password, id_company=company_id)
        success = AdminService.create_user(username, password, company_id, email)
        if success:
            flash("Utilisateur créé avec succès", "success")
        else:
            flash("Erreur lors de la création de l'utilisateur", "error")
    except ValueError as e:
        flash(str(e), "error")
    
    return redirect(url_for("web_admin.admin_users"))

@admin_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    """Supprimer un utilisateur"""
    success = AdminService.delete_user(user_id)
    if success:
        flash("Utilisateur supprimé avec succès", "success")
    else:
        flash("Erreur lors de la suppression de l'utilisateur", "error")
    
    return redirect(url_for("web_admin.admin_users"))

@admin_bp.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
@admin_required
def admin_toggle_user(user_id):
    """Activer/désactiver un utilisateur"""
    success = AdminService.toggle_user_enabled(user_id)
    if success:
        flash("Statut de l'utilisateur modifié.", "success")
    else:
        flash("Erreur lors du changement de statut.", "error")
    return redirect(url_for("web_admin.admin_users"))

@admin_bp.route("/admin/companies")
@admin_required
def admin_companies():
    """Gestion des entreprises"""
    companies = AdminService.get_all_companies()
    
    # Calculer les statistiques pour chaque entreprise
    from entity.user import User
    from entity.agent import Agent
    
    company_stats = {}
    for company in companies:
        user_count = User.get_count_user_by_id_company(company['id_company'])
        agent_count = Agent.get_count_agent_by_id_company(company['id_company'])
        
        company_stats[company['id_company']] = {
            'user_count': user_count,
            'agent_count': agent_count
        }
    
    return render_template("admin_company.html", companies=companies, company_stats=company_stats)

@admin_bp.route("/admin/companies", methods=["POST"])
@admin_required
def admin_create_company():
    """Créer une entreprise"""
    name = request.form.get("name")
    
    try:
        Validator().check_param(name=name)
        success = AdminService.create_company(name)
        if success:
            flash("Entreprise créée avec succès", "success")
        else:
            flash("Erreur lors de la création de l'entreprise", "error")
    except ValueError as e:
        flash(str(e), "error")
    
    return redirect(url_for("web_admin.admin_companies"))

@admin_bp.route("/admin/companies/<int:company_id>/delete", methods=["POST"])
@admin_required
def admin_delete_company(company_id):
    """Supprimer une entreprise"""
    success = AdminService.delete_company(company_id)
    if success:
        flash("Entreprise supprimée avec succès", "success")
    else:
        flash("Erreur lors de la suppression de l'entreprise", "error")
    
    return redirect(url_for("web_admin.admin_companies")) 

@admin_bp.route("/admin/companies/<int:company_id>/toggle", methods=["POST"])
@admin_required
def admin_toggle_company(company_id):
    """Activer/désactiver une entreprise (avec cascade sur utilisateurs et agents)"""
    success = AdminService.toggle_company_enabled(company_id)
    if success:
        flash("Statut de l'entreprise modifié avec cascade sur les utilisateurs et agents.", "success")
    else:
        flash("Erreur lors du changement de statut de l'entreprise.", "error")
    return redirect(url_for("web_admin.admin_companies")) 