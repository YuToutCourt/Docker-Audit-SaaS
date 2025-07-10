import os
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

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

load_dotenv()

def create_app():
    """Factory function pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # Tokens sans expiration pour le développement
    
    # Initialisation JWT
    jwt = JWTManager(app)
    
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
