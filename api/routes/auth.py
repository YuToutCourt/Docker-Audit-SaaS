from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from entity.user import User
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Connexion via user/password et génération d'un JWT"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON requises"}), 400
    
    username = data.get("username")
    password = data.get("password")

    user = AuthService.authenticate_user(username, password)

    if user:
        additional_claims = {
            "is_admin": user.is_admin,
            "id_company": user.id_company
        }
        access_token = create_access_token(identity=username, additional_claims=additional_claims)
        
        return jsonify({
            "access_token": access_token,
            "id_company": user.id_company,
            "is_admin": user.is_admin,
        })

    return jsonify({"error": "Identifiants invalides"}), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Déconnexion (invalidation du token côté client)"""
    return jsonify({"message": "Logged out successfully"}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Récupérer les informations de l'utilisateur connecté"""
    claims = get_jwt()
    username = get_jwt_identity()
    
    return jsonify({
        "username": username,
        "is_admin": claims.get("is_admin"),
        "id_company": claims.get("id_company")
    }), 200 