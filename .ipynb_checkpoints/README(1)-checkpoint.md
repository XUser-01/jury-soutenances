# Partie 1 – Gestion des données de base

## Structure des fichiers

```
partie1/
├── models.py          # Modèles Django (6 entités)
├── serializers.py     # Sérialisation + validation
├── views.py           # CRUD complet (ViewSets)
├── urls.py            # Routes API
└── schema_partie1.sql # Script SQL MySQL
```

## Installation

### 1. Dépendances Python
```bash
pip install django djangorestframework django-filter mysqlclient
```

### 2. Configuration settings.py
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'partie1',   # ou le nom de votre app
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jury_soutenances',
        'USER': 'votre_user',
        'PASSWORD': 'votre_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

### 3. Créer la base de données
```bash
mysql -u root -p < schema_partie1.sql
```

### 4. Migrations Django
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Lancer le serveur
```bash
python manage.py runserver
```

## Endpoints disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| GET/POST | `/api/sessions/` | Lister / Créer sessions |
| GET/PUT/DELETE | `/api/sessions/{id}/` | Détail session |
| GET/POST | `/api/enseignants/` | Lister / Créer enseignants |
| GET | `/api/enseignants/{id}/disponibilites/` | Dispos d'un enseignant |
| GET/POST | `/api/disponibilites/` | Gérer les disponibilités |
| GET/POST | `/api/etudiants/` | Lister / Créer étudiants |
| POST | `/api/etudiants/import-csv/` | Import CSV étudiants |
| GET/POST | `/api/memoires/` | Lister / Déposer mémoires |
| POST | `/api/memoires/{id}/upload-pdf/` | Upload PDF |
| PATCH | `/api/memoires/{id}/changer-statut/` | Changer statut |
| GET/POST | `/api/salles/` | Gérer les salles |

## Format CSV pour import étudiants
```
matricule,nom,prenom,filiere,niveau
INF2025001,Sawadogo,Jean,Informatique,Master 2
INF2025002,Zongo,Fatima,Informatique,Master 2
```
