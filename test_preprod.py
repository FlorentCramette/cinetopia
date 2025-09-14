#!/usr/bin/env python
"""
🧪 Tests Préproduction Cinetopia
Test complet en environnement de préproduction
"""

import os
import sys
import django
import subprocess
import time
import requests
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')
django.setup()

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def test_check(name, condition, success_msg="✅ OK", error_msg="❌ ERREUR"):
    """Vérifie une condition et affiche le résultat"""
    if condition:
        print(f"  {name:<40} {success_msg}")
        return True
    else:
        print(f"  {name:<40} {error_msg}")
        return False

def run_command(command, timeout=30):
    """Exécute une commande système avec timeout"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def test_database_operations():
    """Tests des opérations de base de données"""
    print_header("TESTS BASE DE DONNÉES")
    
    success_count = 0
    total_tests = 4
    
    # Test connexion
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        success_count += test_check("Connexion base de données", True)
    except Exception as e:
        test_check("Connexion base de données", False, error_msg=f"❌ {str(e)}")
    
    # Test migrations
    success, stdout, stderr = run_command("python manage.py showmigrations")
    success_count += test_check("État des migrations", success and "[ ]" not in stdout)
    
    # Test modèles
    try:
        from myapp_cinetopia.models import Movie
        movie_count = Movie.objects.count()
        success_count += test_check("Accès aux modèles", True, f"✅ {movie_count} films")
    except Exception as e:
        test_check("Accès aux modèles", False, error_msg=f"❌ {str(e)}")
    
    # Test intégrité des données
    try:
        from myapp_cinetopia.models import Movie
        sample_movie = Movie.objects.first()
        has_data = sample_movie is not None
        success_count += test_check("Intégrité des données", has_data)
    except Exception as e:
        test_check("Intégrité des données", False, error_msg=f"❌ {str(e)}")
    
    return success_count, total_tests

def test_security_configuration():
    """Tests de configuration sécurité"""
    print_header("TESTS SÉCURITÉ")
    
    success_count = 0
    total_tests = 5
    
    from django.conf import settings
    
    # Debug désactivé
    success_count += test_check("DEBUG désactivé", not settings.DEBUG)
    
    # SECRET_KEY présente
    success_count += test_check("SECRET_KEY configurée", 
                               settings.SECRET_KEY and len(settings.SECRET_KEY) > 50)
    
    # ALLOWED_HOSTS configuré
    success_count += test_check("ALLOWED_HOSTS configuré", 
                               len(settings.ALLOWED_HOSTS) > 0)
    
    # Configuration HTTPS
    success_count += test_check("Configuration HTTPS", 
                               hasattr(settings, 'SECURE_BROWSER_XSS_FILTER'))
    
    # Variables d'environnement
    env_vars = ['SECRET_KEY', 'DB_NAME']
    env_ok = all(var in os.environ for var in env_vars)
    success_count += test_check("Variables d'environnement", env_ok)
    
    return success_count, total_tests

def test_services():
    """Tests des services métier"""
    print_header("TESTS SERVICES")
    
    success_count = 0
    total_tests = 3
    
    # Service recommandations
    try:
        from myapp_cinetopia.services import movie_recommendation_service
        success_count += test_check("Service recommandations", 
                                   movie_recommendation_service is not None)
    except Exception as e:
        test_check("Service recommandations", False, error_msg=f"❌ {str(e)}")
    
    # Service météo
    try:
        from myapp_cinetopia.services import weather_service
        success_count += test_check("Service météo", 
                                   weather_service is not None)
    except Exception as e:
        test_check("Service météo", False, error_msg=f"❌ {str(e)}")
    
    # Test recommandation simple
    try:
        from myapp_cinetopia.services import movie_recommendation_service
        from myapp_cinetopia.models import Movie
        
        if Movie.objects.exists():
            sample_movie = Movie.objects.first()
            recommendations = movie_recommendation_service.get_recommendations(
                sample_movie.title, limit=3
            )
            success_count += test_check("Génération recommandations", 
                                       len(recommendations) > 0)
        else:
            test_check("Génération recommandations", False, 
                      error_msg="❌ Aucun film en base")
    except Exception as e:
        test_check("Génération recommandations", False, error_msg=f"❌ {str(e)}")
    
    return success_count, total_tests

def test_static_files():
    """Tests des fichiers statiques"""
    print_header("TESTS FICHIERS STATIQUES")
    
    success_count = 0
    total_tests = 3
    
    # Collection des fichiers statiques
    success, stdout, stderr = run_command("python manage.py collectstatic --noinput --dry-run")
    success_count += test_check("Collection fichiers statiques", success)
    
    # Présence des templates
    templates_dir = Path("myapp_cinetopia/templates")
    templates_exist = templates_dir.exists() and len(list(templates_dir.glob("*.html"))) > 0
    success_count += test_check("Templates disponibles", templates_exist)
    
    # Fichiers CSS/JS
    static_dir = Path("myapp_cinetopia/static")
    static_exist = static_dir.exists()
    success_count += test_check("Fichiers statiques", static_exist)
    
    return success_count, total_tests

def test_deployment_readiness():
    """Tests de préparation au déploiement"""
    print_header("TESTS PRÉPARATION DÉPLOIEMENT")
    
    success_count = 0
    total_tests = 4
    
    # Check deployment
    success, stdout, stderr = run_command("python manage.py check --deploy")
    success_count += test_check("Django deployment check", success)
    
    # Requirements.txt
    req_file = Path("requirements.txt")
    success_count += test_check("Fichier requirements.txt", req_file.exists())
    
    # Configuration files
    config_files = [".env.preprod", "manage.py"]
    configs_ok = all(Path(f).exists() for f in config_files)
    success_count += test_check("Fichiers de configuration", configs_ok)
    
    # Git status
    success, stdout, stderr = run_command("git status --porcelain")
    git_clean = success and len(stdout.strip()) == 0
    success_count += test_check("Repository Git propre", git_clean)
    
    return success_count, total_tests

def test_performance():
    """Tests de performance basiques"""
    print_header("TESTS PERFORMANCE")
    
    success_count = 0
    total_tests = 2
    
    # Test import models
    start_time = time.time()
    try:
        from myapp_cinetopia.models import Movie
        from myapp_cinetopia.services import movie_recommendation_service
        import_time = time.time() - start_time
        success_count += test_check("Temps d'import des modules", 
                                   import_time < 2.0, 
                                   f"✅ {import_time:.2f}s")
    except Exception as e:
        test_check("Temps d'import des modules", False, error_msg=f"❌ {str(e)}")
    
    # Test requête base de données
    start_time = time.time()
    try:
        from myapp_cinetopia.models import Movie
        count = Movie.objects.count()
        query_time = time.time() - start_time
        success_count += test_check("Temps requête base", 
                                   query_time < 1.0, 
                                   f"✅ {query_time:.2f}s ({count} films)")
    except Exception as e:
        test_check("Temps requête base", False, error_msg=f"❌ {str(e)}")
    
    return success_count, total_tests

def main():
    """Fonction principale des tests"""
    print("""
    🎬 CINETOPIA - TESTS PRÉPRODUCTION
    Validation complète avant déploiement en production
    """)
    
    total_success = 0
    total_tests = 0
    
    # Exécution de tous les tests
    test_suites = [
        ("Base de données", test_database_operations),
        ("Sécurité", test_security_configuration),
        ("Services", test_services),
        ("Fichiers statiques", test_static_files),
        ("Préparation déploiement", test_deployment_readiness),
        ("Performance", test_performance),
    ]
    
    for suite_name, test_function in test_suites:
        try:
            success, tests = test_function()
            total_success += success
            total_tests += tests
        except Exception as e:
            print(f"\n❌ ERREUR dans la suite {suite_name}: {str(e)}")
    
    # Résultats finaux
    print_header("RÉSULTATS FINAUX")
    percentage = (total_success / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n  📊 RÉSULTATS: {total_success}/{total_tests} tests réussis ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("  🎉 EXCELLENT - Prêt pour la production!")
        exit_code = 0
    elif percentage >= 80:
        print("  ✅ BON - Quelques améliorations mineures à apporter")
        exit_code = 0
    elif percentage >= 70:
        print("  ⚠️  MOYEN - Problèmes à corriger avant production")
        exit_code = 1
    else:
        print("  ❌ CRITIQUE - Corrections majeures nécessaires")
        exit_code = 2
    
    print(f"\n  🚀 Statut: {'VALIDÉ' if exit_code == 0 else 'À CORRIGER'}")
    print("  📝 Consultez les détails ci-dessus pour les actions à entreprendre")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())