import os
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from datetime import timedelta

# Import des blueprints
from api.routes.auth import auth_bp
from api.routes.agent import agent_bp
from api.routes.admin import admin_bp
from api.routes.agent_api import agent_api_bp
from web.routes.main import main_bp
from web.routes.admin import admin_bp as web_admin_bp
from web.routes.agent import agent_bp as web_agent_bp

# Import de la base de données
from database.database import Database

# Import de la configuration de sécurité
from web.security import SecurityConfig, SecurityMiddleware

load_dotenv()

def create_app():
    """Factory function pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Détermination de l'environnement
    environment = os.getenv('FLASK_ENV', 'development')
    security_config = SecurityConfig.get_config(environment)
    
    # Configuration de base
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Tokens sans expiration pour le développement
    
    # Application de la configuration de sécurité
    for key, value in security_config.items():
        app.config[key] = value
    
    # Configuration JWT sécurisée
    app.config['JWT_COOKIE_SECURE'] = security_config['SESSION_COOKIE_SECURE']
    app.config['JWT_COOKIE_HTTPONLY'] = True
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialisation JWT
    jwt = JWTManager(app)
    
    # Configuration Talisman pour les headers de sécurité
    Talisman(
        app,
        content_security_policy=SecurityConfig.CSP_POLICY,
        force_https=security_config.get('FORCE_HTTPS', False),
        strict_transport_security=security_config.get('STRICT_TRANSPORT_SECURITY', True),
        strict_transport_security_max_age=security_config.get('STRICT_TRANSPORT_SECURITY_MAX_AGE', 31536000),
        frame_options='DENY'
    )
    
    # Middleware pour les headers de sécurité supplémentaires
    @app.after_request
    def add_security_headers(response):
        return SecurityMiddleware.add_security_headers(response)
    
    # Enregistrement des blueprints API
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(agent_bp, url_prefix='/api/agents')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(agent_api_bp, url_prefix='/api')
    
    # Debug: afficher toutes les routes enregistrées
    print("Routes enregistrées:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    # Enregistrement des blueprints Web
    app.register_blueprint(main_bp)
    app.register_blueprint(web_admin_bp, url_prefix='/admin')
    app.register_blueprint(web_agent_bp)
    
    # Initialisation de la base de données
    with app.app_context():
        db = Database()
        db.close()
    
    return app

# Création de l'application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
