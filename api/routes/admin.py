from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from services.admin_service import AdminService
from validator.validator import Validator

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Récupérer tous les utilisateurs (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    users = AdminService.get_all_users()
    return jsonify({"users": users}), 200

@admin_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user():
    """Créer un nouvel utilisateur (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    company_id = data.get("id_company")
    
    # Validation
    try:
        Validator().check_param(username=username, password=password, id_company=company_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    success = AdminService.create_user(username, password, company_id)
    if success:
        return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"error": "Failed to create user"}), 400

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    """Supprimer un utilisateur (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    success = AdminService.delete_user(user_id)
    if success:
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"error": "User not found or deletion failed"}), 404

@admin_bp.route("/companies", methods=["GET"])
@jwt_required()
def get_companies():
    """Récupérer toutes les entreprises (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    companies = AdminService.get_all_companies()
    return jsonify({"companies": companies}), 200

@admin_bp.route("/companies", methods=["POST"])
@jwt_required()
def create_company():
    """Créer une nouvelle entreprise (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    name = data.get("name")
    
    # Validation
    try:
        Validator().check_param(name=name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    success = AdminService.create_company(name)
    if success:
        return jsonify({"message": "Company created successfully"}), 201
    else:
        return jsonify({"error": "Failed to create company"}), 400

@admin_bp.route("/companies/<int:company_id>", methods=["DELETE"])
@jwt_required()
def delete_company(company_id):
    """Supprimer une entreprise (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    success = AdminService.delete_company(company_id)
    if success:
        return jsonify({"message": "Company deleted successfully"}), 200
    else:
        return jsonify({"error": "Company not found or deletion failed"}), 404

@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """Récupérer les statistiques globales (admin seulement)"""
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    stats = AdminService.get_global_stats()
    return jsonify(stats), 200 