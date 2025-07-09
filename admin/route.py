from flask import Blueprint, flash, redirect, url_for, session, render_template, request
from functools import wraps
from entity.user import User
from entity.company import Company
from entity.agent import Agent
from werkzeug.security import generate_password_hash
from pki.certificate_manager import generate_entreprise_pki
from icecream import ic

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user') or not session.get('is_admin'):
            flash("Accès réservé à l'administration.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@admin_required
def admin_panel():
    return render_template('admin_panel.html')


@admin.route('/users')
@admin_required
def admin_users():
    users = User.get_all_users()
    # Récupérer tous les id_company uniques
    #company_ids = list(set([u.id_company for u in users if u.id_company]))
    # Récupérer les sociétés
    companies = Company.get_all_company()
    company_names = {c.id_company: c.name for c in companies}
    return render_template('admin_users.html', users=users, company_names=company_names, companies=companies)


@admin.route('/users/create', methods=['POST'])
@admin_required
def admin_create_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    id_company = request.form['id_company']
    if User.check_if_user_exist_by_username(username):
        flash("Nom d'utilisateur déjà utilisé.", "error")
        return redirect(url_for('admin.admin_create_user'))

    hashed_password = generate_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email,
        enabled=1,
        is_admin=0,  # Toujours créer des utilisateurs non-admin
        id_company=id_company
    )
    user.add()
    flash("Utilisateur créé avec succès.", "success")
    return redirect(url_for('admin.admin_users'))
    


@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Vérifier d'abord si l'utilisateur existe et n'est pas l'utilisateur connecté
    user = User.get_user_by_id(user_id)
    if user and user.username == session.get('user'):
        flash("Vous ne pouvez pas supprimer votre propre compte.", "error")
        return redirect(url_for('admin.admin_users'))
    if not user:
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for('admin.admin_users'))
    
    # Supprimer l'utilisateur
    if User.delete_user_by_id(user_id):
        flash("Utilisateur supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression de l'utilisateur.", "error")
    return redirect(url_for('admin.admin_users'))


@admin.route('/companies', methods=['GET', 'POST'])
@admin_required
def admin_companies():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash("Nom requis.", "error")
            return redirect(url_for('admin.admin_companies'))
            
        # Créer l'entreprise avec la CA
        company = Company(name=name, company_pki_id=generate_entreprise_pki(name))
        company.add()
        flash("Entreprise créée avec succès.", "success")
        return redirect(url_for('admin.admin_companies'))
    companies = Company.get_all_company()
    # Récupérer le nombre d'utilisateurs et d'agents pour chaque entreprise
    company_stats = {}
    for company in companies:
        user_count = User.get_count_user_by_id_company(company.id_company)
        agent_count = Agent.get_count_agent_by_id_company(company.id_company)
        ic(user_count, agent_count)
        company_stats[company.id_company] = {
            'user_count': user_count,
            'agent_count': agent_count
        }
    return render_template('admin_company.html', companies=companies, company_stats=company_stats)


@admin.route('/companies/delete/<int:company_id>', methods=['POST'])
@admin_required
def admin_delete_company(company_id):
    company = Company.get_company_by_id(company_id)
    if not company:
        flash("Entreprise introuvable.", "error")
        return redirect(url_for('admin.admin_companies'))
    
    # Supprimer l'entreprise
    if Company.delete_company_by_id(company_id):
        flash("Entreprise supprimée avec succès.", "success")
    else:
        flash("Erreur lors de la suppression de l'entreprise.", "error")
    return redirect(url_for('admin.admin_companies'))