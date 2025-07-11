"""
Module de configuration de sécurité pour l'application Flask
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Configuration de sécurité centralisée"""
    
    # Configuration des cookies de session
    SESSION_COOKIE_SECURE = True  # Cookies uniquement en HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protection contre XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF
    SESSION_COOKIE_MAX_AGE = 3600  # Expiration en 1 heure
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Configuration JWT
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Configuration Talisman (headers de sécurité)
    CSP_POLICY = {
        'default-src': ['\'self\''],
        'script-src': ['\'self\'', '\'unsafe-inline\''],
        'style-src': ['\'self\'', '\'unsafe-inline\''],
        'img-src': ['\'self\'', 'data:', 'https:'],
        'font-src': ['\'self\'', 'https:'],
        'connect-src': ['\'self\''],
        'frame-ancestors': ['\'none\'']
    }
    
    # Configuration en fonction de l'environnement
    @staticmethod
    def get_config(environment='development'):
        """Retourne la configuration selon l'environnement"""
        if environment == 'production':
            return {
                'SESSION_COOKIE_SECURE': True,
                'SESSION_COOKIE_HTTPONLY': True,
                'SESSION_COOKIE_SAMESITE': 'Strict',
                'SESSION_COOKIE_MAX_AGE': 1800,  # 30 minutes en production
                'PERMANENT_SESSION_LIFETIME': timedelta(minutes=30),
                'FORCE_HTTPS': True,
                'STRICT_TRANSPORT_SECURITY': True,
                'STRICT_TRANSPORT_SECURITY_MAX_AGE': 31536000,
            }
        else:
            return {
                'SESSION_COOKIE_SECURE': False,  # False pour le développement local
                'SESSION_COOKIE_HTTPONLY': True,
                'SESSION_COOKIE_SAMESITE': 'Lax',
                'SESSION_COOKIE_MAX_AGE': 3600,  # 1 heure en développement
                'PERMANENT_SESSION_LIFETIME': timedelta(hours=1),
                'FORCE_HTTPS': False,
                'STRICT_TRANSPORT_SECURITY': False,
                'STRICT_TRANSPORT_SECURITY_MAX_AGE': 31536000,
            }

class SecurityMiddleware:
    """Middleware pour ajouter des headers de sécurité supplémentaires"""
    
    @staticmethod
    def add_security_headers(response):
        """Ajoute des headers de sécurité à la réponse"""
        # Headers de sécurité supplémentaires
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response

def validate_session_security(session):
    """Valide la sécurité de la session"""
    # Vérification de la présence des champs requis
    required_fields = ['user_id', 'user', 'login_time', 'csrf_token']
    for field in required_fields:
        if field not in session:
            return False
    
    # Vérification de l'expiration
    login_time = session.get('login_time', 0)
    import time
    if time.time() - login_time > 3600:  # 1 heure
        return False
    
    return True

def sanitize_input(data):
    """Nettoie les données d'entrée"""
    if isinstance(data, str):
        # Suppression des caractères dangereux
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            data = data.replace(char, '')
        return data.strip()
    return data 