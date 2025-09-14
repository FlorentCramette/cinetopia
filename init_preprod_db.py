#!/usr/bin/env python
"""
🗃️ Initialisation Base de Données Préproduction
Configuration et peuplement de la base SQLite pour les tests
"""

import os
import sys
import django
from pathlib import Path
import csv
import logging

# Configuration Django avec .env.preprod
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')

# Sauvegarder l'ancien .env et utiliser .env.preprod
if Path('.env').exists():
    if Path('.env.backup').exists():
        os.remove('.env.backup')
    os.rename('.env', '.env.backup')

if Path('.env.preprod').exists():
    import shutil
    shutil.copy('.env.preprod', '.env')

# Initialiser Django
django.setup()

logger = logging.getLogger(__name__)

def create_database():
    """Créer et migrer la base de données"""
    print("🗃️ Création de la base de données préproduction...")
    
    # Supprimer l'ancienne base si elle existe
    db_file = Path('db_preprod.sqlite3')
    if db_file.exists():
        db_file.unlink()
        print("  ✅ Ancienne base supprimée")
    
    # Migrations
    os.system('python manage.py makemigrations --verbosity=0')
    os.system('python manage.py migrate --verbosity=0')
    print("  ✅ Base de données créée et migrée")

def load_movie_data():
    """Charger les données de films depuis le CSV"""
    print("🎬 Chargement des données de films...")
    
    try:
        from myapp_cinetopia.models import Movie
        
        # Vérifier si les données existent déjà
        if Movie.objects.exists():
            print("  ℹ️  Données déjà présentes, suppression...")
            Movie.objects.all().delete()
        
        # Charger depuis le CSV
        csv_path = Path('myapp_cinetopia/data/french_movies_with_keywords.csv')
        if not csv_path.exists():
            print("  ❌ Fichier CSV non trouvé")
            return False
        
        movies_created = 0
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    movie = Movie.objects.create(
                        title=row.get('title', ''),
                        overview=row.get('overview', ''),
                        release_date=row.get('release_date', '2000-01-01') or '2000-01-01',
                        vote_average=float(row.get('vote_average', 0)) if row.get('vote_average') else 0,
                        vote_count=int(row.get('vote_count', 0)) if row.get('vote_count') else 0,
                        genres=row.get('genres', ''),
                        keywords=row.get('keywords', ''),
                        director=row.get('director', ''),
                        actors=row.get('cast', ''),
                        poster_path=row.get('poster_path', '')
                    )
                    movies_created += 1
                    
                    if movies_created % 100 == 0:
                        print(f"    📽️  {movies_created} films chargés...")
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la création du film: {e}")
                    continue
        
        print(f"  ✅ {movies_created} films chargés en base")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du chargement: {e}")
        return False

def create_test_superuser():
    """Créer un superutilisateur pour les tests"""
    print("👤 Création d'un utilisateur de test...")
    
    try:
        from django.contrib.auth.models import User
        
        # Supprimer l'utilisateur test s'il existe
        User.objects.filter(username='admin_test').delete()
        
        # Créer le superutilisateur
        User.objects.create_superuser(
            username='admin_test',
            email='admin@cinetopia.test',
            password='testpass123'
        )
        
        print("  ✅ Utilisateur test créé (admin_test / testpass123)")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la création: {e}")
        return False

def test_database():
    """Tester la base de données"""
    print("🧪 Test de la base de données...")
    
    try:
        from myapp_cinetopia.models import Movie
        from django.contrib.auth.models import User
        
        # Test des modèles
        movie_count = Movie.objects.count()
        user_count = User.objects.count()
        
        print(f"  📊 {movie_count} films en base")
        print(f"  👥 {user_count} utilisateur(s)")
        
        # Test d'une requête simple
        if movie_count > 0:
            sample_movie = Movie.objects.first()
            print(f"  🎬 Film test: {sample_movie.title}")
        
        print("  ✅ Base de données fonctionnelle")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        return False

def restore_original_env():
    """Restaurer le fichier .env original"""
    if Path('.env.backup').exists():
        if Path('.env').exists():
            os.remove('.env')
        os.rename('.env.backup', '.env')
        print("  ✅ Configuration originale restaurée")

def main():
    """Fonction principale"""
    print("""
    🗃️ INITIALISATION BASE DE DONNÉES PRÉPRODUCTION
    ===============================================
    Configuration SQLite pour les tests préproduction
    """)
    
    success = True
    
    try:
        # 1. Créer la base de données
        create_database()
        
        # 2. Charger les données de films
        if not load_movie_data():
            success = False
        
        # 3. Créer un utilisateur de test
        if not create_test_superuser():
            success = False
        
        # 4. Tester la base
        if not test_database():
            success = False
        
        print("\n" + "="*50)
        if success:
            print("🎉 BASE DE DONNÉES PRÉPRODUCTION PRÊTE!")
            print("✅ Tous les composants sont opérationnels")
            print("\nInformations de connexion:")
            print("  📁 Base de données: db_preprod.sqlite3")
            print("  👤 Utilisateur test: admin_test")
            print("  🔑 Mot de passe: testpass123")
        else:
            print("❌ ERREURS LORS DE L'INITIALISATION")
            print("⚠️  Vérifiez les logs ci-dessus")
            
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        success = False
    
    finally:
        # Toujours restaurer l'environnement original
        restore_original_env()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())