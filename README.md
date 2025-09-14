# Cinetopia - Système de Recommandation de Films

Cinetopia est une application web Django qui propose des recommandations de films personnalisées basées sur un algorithme de machine learning utilisant la méthode des k-plus proches voisins (KNN).

## 🎯 Fonctionnalités

- **Authentification utilisateur** : Inscription et connexion sécurisées
- **Recommandations de films** : Algorithme KNN pour suggérer des films similaires
- **Interface intuitive** : Interface utilisateur moderne et responsive
- **Données météo** : Intégration d'une API météo pour enrichir l'expérience
- **Base de données de films français** : Catalogue de films français avec métadonnées complètes

## 🚀 Installation

### Prérequis

- Python 3.8+
- MySQL 5.7+ ou MariaDB 10.2+
- pip (gestionnaire de paquets Python)

### Configuration

1. **Cloner le repository**
   ```bash
   git clone https://github.com/votre-username/cinetopia.git
   cd cinetopia
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de l'environnement**
   - Copier `.env.example` vers `.env`
   - Modifier les variables d'environnement dans `.env` :
   ```env
   SECRET_KEY=votre-clé-secrète-django
   DEBUG=True
   DB_NAME=cinetopia_db
   DB_USER=votre_utilisateur_mysql
   DB_PASSWORD=votre_mot_de_passe_mysql
   DB_HOST=localhost
   DB_PORT=3306
   WEATHER_API_KEY=votre_clé_api_weather
   ```

5. **Configuration de la base de données**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

L'application sera accessible à l'adresse : http://127.0.0.1:8000/

## 🏗️ Architecture

### Structure du projet

```
cinetopia/
├── cinetopia/                 # Configuration principale Django
│   ├── __init__.py
│   ├── settings.py           # Configuration Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuration WSGI
│   └── config.py            # Configuration des variables d'environnement
├── myapp_cinetopia/          # Application principale
│   ├── models.py            # Modèles de données
│   ├── views.py             # Vues Django
│   ├── forms.py             # Formulaires Django
│   ├── services.py          # Services (recommandation, météo)
│   ├── templates/           # Templates HTML
│   ├── static/             # Fichiers statiques (CSS, JS, images)
│   └── data/               # Données des films
├── requirements.txt         # Dépendances Python
├── .env.example            # Exemple de configuration
└── README.md              # Ce fichier
```

### Technologies utilisées

- **Backend** : Django 5.0.6
- **Base de données** : MySQL
- **Machine Learning** : scikit-learn (KNN, TF-IDF)
- **Data Processing** : pandas, numpy
- **API externe** : WeatherAPI
- **Frontend** : HTML, CSS, JavaScript

## 🤖 Algorithme de Recommandation

L'algorithme utilise :

1. **Vectorisation TF-IDF** : Transformation des caractéristiques textuelles des films
2. **K-Nearest Neighbors** : Recherche des films les plus similaires
3. **Caractéristiques combinées** :
   - Genre du film
   - Synopsis
   - Réalisateur
   - Acteurs principaux
   - Mots-clés
   - Note et date de sortie

## 📊 API

### Endpoints disponibles

- `GET /` - Page de connexion
- `GET /home/` - Page d'accueil (authentification requise)
- `GET /movie/` - Formulaire de recherche de film
- `POST /movie/` - Soumission de recherche
- `GET /results/` - Résultats de recommandation
- `POST /recommend/` - API JSON pour recommandations

## 🔧 Configuration avancée

### Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `SECRET_KEY` | Clé secrète Django | ✅ |
| `DEBUG` | Mode debug | ✅ |
| `DB_NAME` | Nom de la base de données | ✅ |
| `DB_USER` | Utilisateur MySQL | ✅ |
| `DB_PASSWORD` | Mot de passe MySQL | ✅ |
| `DB_HOST` | Hôte MySQL | ✅ |
| `DB_PORT` | Port MySQL | ✅ |
| `WEATHER_API_KEY` | Clé API WeatherAPI | ❌ |

### Déploiement

Pour un déploiement en production :

1. Configurer `DEBUG=False`
2. Ajouter votre domaine dans `ALLOWED_HOSTS`
3. Configurer un serveur web (nginx, Apache)
4. Utiliser un serveur WSGI (gunicorn, uWSGI)
5. Configurer une base de données de production

## 🧪 Tests

```bash
python manage.py test
```

## 📝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **Votre Nom** - *Développement initial* - [Votre GitHub](https://github.com/votre-username)

## 🙏 Remerciements

- Données de films fournies par [source des données]
- API météo par [WeatherAPI](https://weatherapi.com/)
- Framework Django et la communauté Python

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub ou contacter [votre-email@example.com]