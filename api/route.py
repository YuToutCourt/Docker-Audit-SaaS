import jwt, os
import datetime
from dotenv import load_dotenv
from functools import wraps
from flask import Blueprint, jsonify, request, session
from icecream import ic

from entity.agent import Agent
from entity.company import Company
from entity.report import Report
from entity.user import User
from parser.parser import Parser

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

api = Blueprint('api', __name__)

USERS = {"user": "password123"} # TEMPS DATA BASE

def token_required(f):
    """Décorateur pour exiger un JWT valide sur certaines routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token manquant"}), 401

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded  # Stocke les infos du user dans la requête
        except jwt.ExpiredSignatureError as e:
            return jsonify({"error": "Token expiré"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Token invalide"}), 401

        return f(*args, **kwargs)

    return decorated

@api.route("/login", methods=["POST"])
def login():
    """Connexion via user/password et génération d'un JWT"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) == password:
        token = jwt.encode(
            {
                "username": username,
                "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        session["token"] = token
        return jsonify({"token": token})

    return jsonify({"error": "Identifiants invalides"}), 401


import base64
import re
from datetime import datetime

def check_send_param(**kwargs):
    """
    Vérifie la validité des paramètres envoyés.
    """
    token = kwargs.get('token')
    if not token:
        raise ValueError("Company agent token missing")
    
    if len(token) > 255:
        raise ValueError("Token length is incorrect.")

    date = kwargs.get('date')
    if not date:
        raise ValueError("Date is required")
    
    if len(date) != 19:
        raise ValueError("Date length is incorrect. Expected format: 'YYYY-MM-DD HH:MM:SS'")

    try:
        datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError("Invalid date format. Expected format: 'YYYY-MM-DD HH:MM:SS'")

    data = kwargs.get('data')
    if not data or not isinstance(data, str):
        raise ValueError("Data is required and must be a string")

    try:
        base64.b64decode(data, validate=True)
    except Exception:
        raise ValueError("Data must be in base64 format")

    id_agent = kwargs.get('id_agent')
    if not id_agent or not isinstance(id_agent, int):
        raise ValueError("ID agent is required and must be an integer")


@api.route("/send", methods=["POST"])
def send_data():
    try:
        json_data = request.get_json()
        token = json_data.get("company_agent_token")
        date = json_data.get("date")
        data = json_data.get("data")
        id_agent = json_data.get("id_agent")

        check_send_param(date=date, data=data, id_agent=id_agent, token=token)

        company = Company().get_company_by_agent_token(token)
        if not company:
            return jsonify({"error": "Invalid token"}), 401

        Report().insert_data(date, data, id_agent, company.id)

        return jsonify({"message": "Data received successfully"})

    except (ValueError, Exception) as e:
        ic(e)
        return jsonify({"message": "Error hacker will not get the info"}), 500



@api.route("/health", methods=["GET"])
def hello():
    return jsonify({"message": "I'm alive!"})