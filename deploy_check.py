"""
Script de vérification avant déploiement
"""
import os
import sys
import django
from pathlib import Path

def check_environment():
    """Vérifie que l'environnement est correctement configuré."""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier que le fichier .env existe
    if not Path('.env').exists():
        print("❌ Fichier .env manquant. Copiez .env.example vers .env et configurez-le.")
        return False
    
    # Vérifier les variables d'environnement critiques
    required_vars = ['SECRET_KEY', 'DB_PASSWORD']
    missing_vars = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables d'environnement manquantes: {', '.join(missing_vars)}")
        return False
    
    print("✅ Configuration d'environnement OK")
    return True

def check_database():
    """Vérifie la connexion à la base de données."""
    print("🔍 Vérification de la base de données...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        print("✅ Connexion à la base de données OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def check_migrations():
    """Vérifie l'état des migrations."""
    print("🔍 Vérification des migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Créer les migrations si nécessaire
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Appliquer les migrations
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migrations OK")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False

def check_static_files():
    """Vérifie les fichiers statiques."""
    print("🔍 Vérification des fichiers statiques...")
    
    static_dir = Path('myapp_cinetopia/static')
    if not static_dir.exists():
        print("❌ Dossier static manquant")
        return False
    
    print("✅ Fichiers statiques OK")
    return True

def main():
    """Point d'entrée principal."""
    print("🚀 Vérification du projet Cinetopia avant déploiement")
    print("=" * 60)
    
    checks = [
        check_environment,
        check_database,
        check_migrations,
        check_static_files
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 Toutes les vérifications sont passées! Le projet est prêt.")
        print("\n📋 Prochaines étapes:")
        print("1. Créer un repository sur GitHub")
        print("2. Ajouter l'origine remote: git remote add origin <URL>")
        print("3. Pousser le code: git push -u origin main")
    else:
        print("❌ Certaines vérifications ont échoué. Veuillez corriger les erreurs.")
        sys.exit(1)

if __name__ == '__main__':
    main()