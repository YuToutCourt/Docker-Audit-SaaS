import jwt, os
from datetime import datetime, timedelta, timezone, UTC
from dotenv import load_dotenv
from functools import wraps
from flask import Blueprint, jsonify, request, session
from icecream import ic
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from entity.agent import Agent
from entity.company import Company
from entity.report import Report
from entity.user import User
from validator.validator import Validator
from database.database import Database, SessionLocal

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
        json_data = request.get_json()
        token = json_data.get("company_agent_token")
        date = json_data.get("date")
        data = json_data.get("data")
        id_agent = json_data.get("id_agent")

        Validator().check_param(date=date, data=data, id_agent=id_agent, token=token)

        company = Company().get_company_by_agent_token(token)
        if not company:
            return jsonify({"error": "Invalid token"}), 401

        Report().insert_data(date, data, id_agent, company.id)

        return jsonify({"message": "Data received successfully"})

    except (ValueError, Exception) as e:
        ic(e)
        return jsonify({"message": "Error hacker will not get the info"}), 500


@api.route("/add_agent", methods=["POST"])
def add_agent():
    json_data = request.get_json()
    token = json_data.get("company_agent_token")
    name = json_data.get("name")
    date = datetime.now().strftime("%y-%m-%d %H:%M:%S")

    ic(name, token, date)

    Validator().check_param(name=name, token=token)

    session = SessionLocal()
    try:
        # Vérifier si le token existe dans Company
        company = Company.get_company_by_agent_token(session, token)
        if not company:
            session.close()
            return jsonify({"error": "Invalid token"}), 403

        existing_agent = session.query(Agent).filter_by(name=name, id_company=company.id_company).first()
        if existing_agent:
            session.close()
            return jsonify({"error": "Agent already exists"}), 400

        # Créer l'agent pour cette company
        agent = Agent(
            name=name,
            next_scan_date_=date,
            enabled=1,
            health_check=None,
            id_company=company.id_company
        )
        session.add(agent)
        session.commit()
        response = jsonify({"message": "Agent created successfully", "id_company": company.id_company})
        session.close()

        return response, 201

    except Exception as e:
        session.rollback()
        session.close()
        ic(e)
        return jsonify({"error": "Internal server error"}), 500


@api.route("/health", methods=["GET"])
def hello():
    return jsonify({"message": "I'm alive!"})