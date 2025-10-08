# Docker Audit SaaS

Une plateforme SaaS complète pour l'audit et la surveillance de conteneurs Docker, permettant aux entreprises de gérer leurs agents d'audit et de consulter les rapports de sécurité.

## 🚀 Fonctionnalités

### Pour les Administrateurs
- **Gestion des entreprises** : Création et administration des comptes entreprises
- **Gestion des utilisateurs** : Création et gestion des comptes utilisateurs par entreprise
- **Surveillance des agents** : Monitoring de l'état de santé des agents d'audit
- **Rapports globaux** : Accès aux rapports d'audit de toutes les entreprises

### Pour les Agents
- **Interface d'agent** : Interface dédiée pour les agents d'audit
- **API d'agent** : Endpoints REST pour l'envoi de rapports d'audit
- **Gestion des scans** : Planification et exécution des audits Docker
- **Rapports de sécurité** : Génération et envoi de rapports d'audit

### Sécurité
- **Authentification JWT** : Système d'authentification sécurisé
- **Gestion des rôles** : Différenciation entre administrateurs et agents
- **Isolation par entreprise** : Chaque entreprise accède uniquement à ses données

## 🏗️ Architecture

```
Docker Audit SaaS/
├── api/                    # API REST
│   └── routes/
│       ├── auth.py        # Authentification
│       ├── admin.py       # Gestion admin
│       ├── agent.py       # Gestion agents
│       └── agent_api.py   # API agents
├── web/                    # Interface web
│   └── routes/
│       ├── main.py        # Pages principales
│       ├── admin.py       # Interface admin
│       └── agent.py       # Interface agent
├── database/              # Gestion base de données
├── entity/                # Modèles de données
├── services/              # Services métier
├── utils/                 # Utilitaires
├── templates/             # Templates HTML
├── static/                # Assets statiques
└── pki/                   # Certificats PKI
```

## 🛠️ Technologies

- **Backend** : Flask (Python)
- **Base de données** : MariaDB/MySQL
- **Authentification** : JWT (JSON Web Tokens)
- **Conteneurisation** : Docker & Docker Compose
- **Frontend** : HTML/CSS/JavaScript avec Jinja2

## 📋 Prérequis

- Python 3.8+
- Docker et Docker Compose
- MariaDB/MySQL
- Git

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <repository-url>
cd Docker-Audit-SaaS
```

### 2. Configuration de l'environnement

```bash
# Copier le fichier d'exemple
cp .env_sample .env

# Éditer le fichier .env avec vos valeurs
nano .env
```

Variables d'environnement requises :
```env
SECRET_KEY=your_secret_key_here
USER_DB=audit
PASSWORD_DB=toor
HOST=localhost
DATABASE=audit
```

### 3. Démarrage de la base de données

```bash
# Démarrer MariaDB avec Docker Compose
docker-compose up -d mariadb

# Attendre que la base soit prête (environ 30 secondes)
```

### 4. Initialisation de la base de données

```bash
# Se connecter à MariaDB
mysql -h localhost -P 3326 -u audit -p audit

# Exécuter le script de création des tables
source create_tables.sql;
```

### 5. Installation des dépendances Python

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 6. Démarrage de l'application

```bash
# Démarrer l'application
python app.py
```

L'application sera accessible sur `http://localhost:80`

## 🎯 Utilisation

### Interface Web

#### Administrateur
- **URL** : `http://localhost/admin`
- **Identifiants par défaut** : `admin` / `admin`
- **Fonctionnalités** :
  - Gestion des entreprises
  - Gestion des utilisateurs
  - Surveillance des agents
  - Consultation des rapports

#### Agent
- **URL** : `http://localhost/agent`
- **Fonctionnalités** :
  - Interface de gestion des audits
  - Consultation des rapports
  - Configuration des scans

### API REST

#### Authentification
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

#### Gestion des agents
```bash
# Lister les agents
GET /api/agents

# Créer un agent
POST /api/agents
{
  "name": "agent-name",
  "id_company": 1
}

# Mettre à jour un agent
PUT /api/agents/{id}
```

#### API Agent (pour les agents d'audit)
```bash
# Envoyer un rapport d'audit
POST /api/report
Authorization: Bearer {agent_token}
{
  "dataB64": "base64_encoded_report_data",
  "agent_name": "agent-name"
}
```

## 📊 Structure de la base de données

### Tables principales

- **Company** : Entreprises clientes
- **User_** : Utilisateurs du système
- **Agent** : Agents d'audit Docker
- **Report** : Rapports d'audit générés

### Relations

- Une entreprise peut avoir plusieurs utilisateurs
- Une entreprise peut avoir plusieurs agents
- Un agent génère plusieurs rapports
- Chaque rapport est lié à un agent et une entreprise

## 🔧 Scripts utiles

### Démarrage automatique
```bash
# Utiliser le script de démarrage
chmod +x Demarrage.sh
./Demarrage.sh
```

### Tests
```bash
# Exécuter les tests
python test_delete_company.py
```

## 🐳 Déploiement avec Docker

### Build de l'image
```bash
docker build -t docker-audit-saas .
```

### Démarrage complet
```bash
docker-compose up -d
```

## 🔒 Sécurité

- **Authentification JWT** : Tokens sécurisés pour l'API
- **Isolation des données** : Chaque entreprise accède uniquement à ses données
- **Validation des entrées** : Validation côté serveur de toutes les données
- **Gestion des sessions** : Sessions sécurisées pour l'interface web

## 📝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

**Docker Audit SaaS** - Une solution complète pour l'audit de conteneurs Docker en mode SaaS.
