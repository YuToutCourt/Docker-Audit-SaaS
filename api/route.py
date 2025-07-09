import datetime
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from icecream import ic
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from entity.agent import Agent
from entity.company import Company
from entity.ca import Ca
from entity.report import Report
from entity.user import User
from validator.validator import Validator
from database.database import dbo
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

    user = User.login_user(username, password)

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
        json_data = request.get_json()
        cert_pem = json_data.get("cert").encode("utf-8")
        report = json_data.get("data")
        salt = json_data.get("IV")

        ic(salt)

        if not cert_pem:
            return jsonify({"message": "Missing certificate"}), 403


        agent = Agent.get_agent_from_cert(cert_pem)

        # Check la date du scan et la date de today pour voir si on accepte le scan
        scan_date = Agent.get_scan_date_from_cert(cert_pem)
        today = datetime.datetime.now()
        if scan_date > today:
            return jsonify({"message": "Le prochain scan n'est pas encore prêt"}), 403

        # Charger le certificat PEM
        id_ca = agent.id_ca
        ca_cert = Ca.get_publickey_from_ca_id(id_ca)
        
        if not ca_cert:
            return jsonify({"message": "CA not found"}), 403
            
        ca_cert = ca_cert.encode("utf-8")

    
        if verify_certificate(cert_pem, ca_cert):
            Report.add_new_report(datetime.datetime.now(), report, agent.id_agent, agent.id_company, salt)
            #TODO : Intégration du rapport
            return jsonify({"message": f"success"}), 200

    except Exception as e:
        ic(e)
        return jsonify({"message": "Internal Server Error"}), 500

@api.route("/get_agent_info", methods=["POST"])
def get_agent_info():
    try:
        dbo_session = dbo()
        json_data = request.get_json()
        cert_pem = json_data.get("cert").encode("utf-8")

        if not cert_pem:
            return jsonify({"message": "Missing certificate"}), 403

        agent = Agent.get_agent_from_cert(cert_pem)
        # Charger le certificat PEM
        id_ca = agent.id_ca
        ca_cert = Ca.get_publickey_from_ca_id(id_ca)
        
        if not ca_cert:
            return jsonify({"message": "CA not found"}), 403
            
        ca_cert = ca_cert.encode("utf-8")
        status = agent.enabled

        if verify_certificate(cert_pem, ca_cert):
            scan_date = Agent.get_scan_date_from_cert(cert_pem)
            return jsonify({"activated": f"{bool(status)}","date": f"{scan_date}"}), 200

    except Exception as e:
        ic(e)
        return jsonify({"message": "Internal Server Error"}), 500


@api.route("/add_agent", methods=["POST"])
@jwt_required()
def add_agent():
    json_data = request.get_json()
    name = json_data.get("name")

    Validator().check_param(name=name)
    
    claims = get_jwt()
    company_id = claims.get("id_company")
    retrieve_agent_pki = generate_agent_pki(company_id, name)
    pub = retrieve_agent_pki.get("pub")
    priv = retrieve_agent_pki.get("priv")
    try:
        # Vérifier si l'id_company existe
        if not company_id:
            return jsonify({"error": "Invalid company"}), 403

        id_ca = Company.get_ca_id_from_company(company_id)

        if not id_ca:
            return jsonify({"error": "Invalid CA"}), 403

        if Agent.check_if_agent_already_exist(name, company_id):
            return jsonify({"error": "Agent already exists"}), 400

        agent = Agent(
            name=name,
            next_scan_date_="1970/01/01 00:00:00",
            id_company= company_id,
            health_check=0,
            private_key=priv,
            public_key=pub,
            id_ca=id_ca
        )

        if agent.add():
            response = jsonify({"message": "Agent created successfully"})
            return response, 201
        else:
            response = jsonify({"message": "Unknow Error"})
            return response, 500

    except Exception as e:
        ic(e)
        return jsonify({"error": "Internal Server Error"}), 500
