import datetime
from flask import Blueprint, jsonify, request
from icecream import ic
from entity.agent import Agent
from entity.company import Company
from entity.ca import Ca
from entity.report import Report
from pki.certificate_manager import verify_certificate

agent_api_bp = Blueprint('agent_api', __name__)

@agent_api_bp.route("/send", methods=["POST"])
def send_data():
    """Route pour recevoir les données des agents"""
    try:
        json_data = request.get_json()
        cert_pem = json_data.get("cert").encode("utf-8")
        report = json_data.get("data")
        salt = json_data.get("IV")

        if not cert_pem:
            return jsonify({"message": "Missing certificate"}), 403

        agent = Agent.get_agent_from_cert(cert_pem)
        if not agent:
            return jsonify({"message": "Agent not found"}), 404
            
        # Check la date du scan et la date de today pour voir si on accepte le scan
        scan_date = agent.next_scan_date_
        if not scan_date:
            return jsonify({"message": "Scan date not found"}), 403
            
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
            # Ajout du rapport
            Report.add_new_report(datetime.datetime.now(), report, agent.id_agent, agent.id_company, salt)
            # Recalcul du prochain scan
            try:
                interval = agent.scan_interval or 86400  # Valeur par défaut 1 jour si non défini
                now = datetime.datetime.now()
                next_scan = now + datetime.timedelta(seconds=interval)
                agent.next_scan_date_ = next_scan.strftime('%Y-%m-%d %H:%M:%S')
                agent.update()  # Sauvegarde la nouvelle date dans la BDD
            except Exception as e:
                ic(f'Erreur mise à jour next_scan_date_: {e}')
            return jsonify({"message": "success"}), 201
        else:
            return jsonify({"message": "Invalid certificate"}), 403

    except Exception as e:
        ic(e)
        return jsonify({"message": "Internal Server Error"}), 500

@agent_api_bp.route("/get_agent_info", methods=["POST"])
def get_agent_info():
    """Route pour récupérer les informations d'un agent"""
    try:
        json_data = request.get_json()
        cert_pem = json_data.get("cert").encode("utf-8")

        if not cert_pem:
            return jsonify({"message": "Missing certificate"}), 403

        agent = Agent.get_agent_from_cert(cert_pem)
        if not agent:
            return jsonify({"message": "Unauthorized"}), 401
            
        # Charger le certificat PEM
        id_ca = agent.id_ca
        ca_cert = Ca.get_publickey_from_ca_id(id_ca)
        
        if not ca_cert:
            return jsonify({"message": "CA not found"}), 403
            
        ca_cert = ca_cert.encode("utf-8")
        status = agent.enabled

        if verify_certificate(cert_pem, ca_cert):
            scan_date = agent.next_scan_date_
            if not scan_date:
                return jsonify({"message": "Scan date not found"}), 403
                
            return jsonify({
                "activated": f"{bool(status)}",
                "date": f"{scan_date}"
            }), 200
        else:
            return jsonify({"message": "Invalid certificate"}), 403

    except Exception as e:
        ic(e)
        return jsonify({"message": "Internal Server Error"}), 500 