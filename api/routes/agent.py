from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from services.agent_service import AgentService
from validator.validator import Validator

agent_bp = Blueprint('agent', __name__)

@agent_bp.route("/", methods=["GET"])
@jwt_required()
def get_agents():
    """Récupérer tous les agents de l'utilisateur"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    agents = AgentService.get_agents_by_company(company_id)
    return jsonify({"agents": agents}), 200

@agent_bp.route("/<int:agent_id>", methods=["GET"])
@jwt_required()
def get_agent(agent_id):
    """Récupérer un agent spécifique"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    agent = AgentService.get_agent_by_id_and_company(agent_id, company_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    
    return jsonify(agent), 200

@agent_bp.route("/", methods=["POST"])
@jwt_required()
def create_agent():
    """Créer un nouvel agent"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    data = request.get_json()
    name = data.get("name")
    
    # Validation
    try:
        Validator().check_param(name=name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    success = AgentService.create_agent(name, company_id)
    if success:
        return jsonify({"message": "Agent created successfully"}), 201
    else:
        return jsonify({"error": "Failed to create agent"}), 400

@agent_bp.route("/<int:agent_id>", methods=["PUT"])
@jwt_required()
def update_agent(agent_id):
    """Mettre à jour un agent"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    data = request.get_json()
    success = AgentService.update_agent(agent_id, company_id, data)
    
    if success:
        return jsonify({"message": "Agent updated successfully"}), 200
    else:
        return jsonify({"error": "Agent not found or update failed"}), 404

@agent_bp.route("/<int:agent_id>", methods=["DELETE"])
@jwt_required()
def delete_agent(agent_id):
    """Supprimer un agent"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    success = AgentService.delete_agent(agent_id, company_id)
    if success:
        return jsonify({"message": "Agent deleted successfully"}), 200
    else:
        return jsonify({"error": "Agent not found or access denied"}), 404

@agent_bp.route("/<int:agent_id>/certificate", methods=["GET"])
@jwt_required()
def download_certificate(agent_id):
    """Télécharger le certificat d'un agent"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    certificate = AgentService.get_agent_certificate(agent_id, company_id)
    if certificate:
        return jsonify(certificate), 200
    else:
        return jsonify({"error": "Certificate not found"}), 404

@agent_bp.route("/<int:agent_id>/reports", methods=["GET"])
@jwt_required()
def get_agent_reports(agent_id):
    """Récupérer les rapports d'un agent"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    reports = AgentService.get_agent_reports(agent_id, company_id)
    return jsonify({"reports": reports}), 200

@agent_bp.route("/<int:agent_id>/report/<int:report_id>/download", methods=["POST"])
@jwt_required()
def download_report(agent_id, report_id):
    """Télécharger un rapport déchiffré"""
    claims = get_jwt()
    company_id = claims.get("id_company")
    
    data = request.get_json()
    password = data.get("password")
    
    if not password:
        return jsonify({"error": "Password required"}), 400
    
    pdf_data = AgentService.download_report(agent_id, report_id, company_id, password)
    if pdf_data:
        return jsonify({"pdf_data": pdf_data}), 200
    else:
        return jsonify({"error": "Failed to decrypt report"}), 400 