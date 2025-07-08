import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from icecream import ic
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from entity.agent import Agent
from entity.ca import Ca
from validator.validator import Validator
from database.database import Database, dbo
from pki.certificate_manager import generate_agent_pki, verify_certificate

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

api = Blueprint('api', __name__)

@api.route("/login", methods=["POST"])
def login():
    """Connexion via user/password et génération d'un JWT"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = Database()
    user = db.login_user(username, password)
    db.close()

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


@api.route("/send", methods=["POST"])
def send_data():
    try:
        dbo_session = dbo()
        json_data = request.get_json()
        cert_pem = json_data.get("cert").encode("utf-8")
        report = json_data.get("data")

        if not cert_pem:
            return jsonify({"message": "Missing certificate"}), 403

        # Charger le certificat PEM
        id_ca = Agent.get_ca_id_from_cert(dbo_session, cert_pem)
        ca_cert = Ca.get_ca_from_id(dbo_session, id_ca).encode("utf-8")

        if verify_certificate(cert_pem, ca_cert):
            ic(report)
            #TODO : Intégration du rapport
            return jsonify({"message": f"success"}), 200

    except Exception as e:
        ic(e)
        return jsonify({"message": "Error hacker will not get the info"}), 500


@api.route("/add_agent", methods=["POST"])
@jwt_required()
def add_agent():
    json_data = request.get_json()
    name = json_data.get("name")

    ic(name)

    Validator().check_param(name=name)
    
    claims = get_jwt()
    company_id = claims.get("id_company")
    retrieve_agent_pki = generate_agent_pki(company_id, name)
    pub = retrieve_agent_pki.get("pub")
    priv = retrieve_agent_pki.get("priv")
    dbo_session = dbo()
    try:
        # Vérifier si l'id_company existe
        if not company_id:
            dbo_session.close()
            return jsonify({"error": "Invalid company"}), 403

        existing_agent = dbo_session.query(Agent).filter_by(name=name, id_company=company_id).first()
        id_ca = Agent.get_ca_id_from_company(dbo_session, company_id).id_ca
        if existing_agent:
            dbo_session.close()
            return jsonify({"error": "Agent already exists"}), 400


        if Agent.add_new_agent(dbo_session, name, priv, pub, company_id, id_ca):
            response = jsonify({"message": "Agent created successfully"})
            return response, 201
        else:
            response = jsonify({"message": "Unknow Error"})
            return response, 500

    except Exception as e:
        dbo_session.rollback()
        dbo_session.close()
        ic(e)
        return jsonify({"error": "Internal server error"}), 500
