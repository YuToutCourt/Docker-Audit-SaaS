import jwt, os
import datetime
from dotenv import load_dotenv
from functools import wraps
from flask import Blueprint, jsonify, request, session
from icecream import ic


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

@api.route("/send", methods=["POST"])
@token_required
def send_data():
    data = request.form.get("data")
    parser = Parser(data)

    # return jsonify(parser)


@api.route("/health", methods=["GET"])
def hello():
    return jsonify({"message": "I'm alive!"})