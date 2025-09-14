#!/usr/bin/env python3
"""
Script de test automatisé pour Cinetopia
========================================

Vérifie toutes les fonctionnalités de l'application avant déploiement.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(message, status="INFO"):
    """Affiche un message de test coloré."""
    color_map = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "ERROR": Colors.RED,
        "WARNING": Colors.YELLOW
    }
    color = color_map.get(status, Colors.BLUE)
    print(f"{color}[TEST-{status}] {message}{Colors.END}")

def run_command(command, capture_output=True, timeout=30):
    """Exécute une commande avec timeout."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout if capture_output else "", result.stderr if capture_output else ""
    except subprocess.TimeoutExpired:
        return False, "", "Timeout expired"
    except Exception as e:
        return False, "", str(e)

def test_environment():
    """Test de l'environnement de base."""
    print_test("🔍 Vérification de l'environnement de base")
    
    # Test Python
    success, version, _ = run_command("python --version")
    if success:
        print_test(f"Python détecté: {version.strip()}", "SUCCESS")
    else:
        print_test("Python non trouvé", "ERROR")
        return False
    
    # Test manage.py
    if Path("manage.py").exists():
        print_test("Fichier manage.py trouvé", "SUCCESS")
    else:
        print_test("Fichier manage.py manquant", "ERROR")
        return False
    
    # Test .env
    if Path(".env").exists():
        print_test("Fichier .env configuré", "SUCCESS")
    else:
        print_test("Fichier .env manquant - sera créé", "WARNING")
    
    return True

def test_imports():
    """Test des imports Python critiques."""
    print_test("📦 Vérification des imports Python")
    
    critical_imports = [
        ("django", "Django framework"),
        ("dotenv", "Variables d'environnement"),
        ("requests", "Requêtes HTTP")
    ]
    
    optional_imports = [
        ("pandas", "Analyse de données"),
        ("sklearn", "Machine Learning"),
        ("numpy", "Calculs numériques"),
        ("MySQLdb", "Connecteur MySQL")
    ]
    
    all_success = True
    
    # Test des imports critiques
    for module, description in critical_imports:
        try:
            __import__(module)
            print_test(f"{description} ✓", "SUCCESS")
        except ImportError:
            print_test(f"{description} ✗ (CRITIQUE)", "ERROR")
            all_success = False
    
    # Test des imports optionnels
    for module, description in optional_imports:
        try:
            __import__(module)
            print_test(f"{description} ✓", "SUCCESS")
        except ImportError:
            print_test(f"{description} ✗ (optionnel)", "WARNING")
    
    return all_success

def test_django_setup():
    """Test de la configuration Django."""
    print_test("⚙️ Vérification de la configuration Django")
    
    # Configurer Django d'abord
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')
    
    # Test check Django (sans --quiet pour Django 5.0)
    success, output, error = run_command("python manage.py check")
    if success:
        print_test("Configuration Django valide", "SUCCESS")
    else:
        print_test(f"Erreurs de configuration: {error}", "ERROR")
        return False
    
    # Test migrations
    success, output, error = run_command("python manage.py showmigrations")
    if success:
        print_test("Migrations détectées", "SUCCESS")
    else:
        print_test("Problème avec les migrations", "WARNING")
    
    return True

def test_static_files():
    """Test des fichiers statiques."""
    print_test("📁 Vérification des fichiers statiques")
    
    static_paths = [
        "myapp_cinetopia/static",
        "myapp_cinetopia/templates"
    ]
    
    for path in static_paths:
        if Path(path).exists():
            print_test(f"Dossier {path} trouvé", "SUCCESS")
        else:
            print_test(f"Dossier {path} manquant", "ERROR")
            return False
    
    return True

def test_data_files():
    """Test des fichiers de données."""
    print_test("📊 Vérification des données")
    
    data_file = Path("myapp_cinetopia/data/french_movies_with_keywords.csv")
    if data_file.exists():
        print_test("Fichier de données films trouvé", "SUCCESS")
        
        # Vérifier la taille du fichier
        size_mb = data_file.stat().st_size / (1024 * 1024)
        print_test(f"Taille du fichier: {size_mb:.1f} MB", "INFO")
        
        return True
    else:
        print_test("Fichier de données films manquant", "ERROR")
        return False

def test_server_start():
    """Test de démarrage du serveur (rapide)."""
    print_test("🚀 Test de démarrage du serveur")
    
    # Configurer Django d'abord
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')
    
    # Lancer le serveur en arrière-plan
    try:
        process = subprocess.Popen(
            ["python", "manage.py", "runserver", "127.0.0.1:8001", "--noreload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre que le serveur démarre
        time.sleep(8)
        
        # Tester la connexion
        try:
            response = requests.get("http://127.0.0.1:8001", timeout=15)
            if response.status_code in [200, 302, 404]:  # 404 est OK si pas de route /
                print_test("Serveur démarre correctement", "SUCCESS")
                success = True
            else:
                print_test(f"Serveur répond avec code {response.status_code}", "WARNING")
                success = True  # Toujours OK si le serveur répond
        except requests.exceptions.RequestException as e:
            print_test(f"Impossible de connecter au serveur: {e}", "ERROR")
            success = False
        
        # Arrêter le serveur
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        return success
        
    except Exception as e:
        print_test(f"Erreur lors du test serveur: {e}", "ERROR")
        return False

def test_services():
    """Test des services de l'application."""
    print_test("🔧 Test des services applicatifs")
    
    try:
        # Configurer Django d'abord
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinetopia.settings')
        
        # Import Django pour configurer les settings
        import django
        django.setup()
        
        # Test du service météo
        from myapp_cinetopia.services import weather_service
        if weather_service:
            print_test("Service météo initialisé", "SUCCESS")
        else:
            print_test("Service météo non disponible", "WARNING")
        
        # Test du service de recommandation
        from myapp_cinetopia.services import movie_service
        if movie_service and hasattr(movie_service, 'ml_available') and movie_service.ml_available:
            print_test("Service recommandation ML disponible", "SUCCESS")
        elif movie_service:
            print_test("Service recommandation initialisé (ML désactivé)", "WARNING")
        else:
            print_test("Service recommandation non disponible", "ERROR")
            return False
        
        return True
        
    except Exception as e:
        print_test(f"Erreur lors du test des services: {e}", "ERROR")
        return False

def main():
    """Point d'entrée principal."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("🧪 TESTS AUTOMATISÉS CINETOPIA")
    print(f"{'='*60}{Colors.END}\n")
    
    tests = [
        ("Environnement", test_environment),
        ("Imports Python", test_imports),
        ("Configuration Django", test_django_setup),
        ("Fichiers statiques", test_static_files),
        ("Données", test_data_files),
        ("Services", test_services),
        ("Démarrage serveur", test_server_start)
    ]
    
    results = []
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{Colors.BOLD}--- {test_name} ---{Colors.END}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print_test(f"Erreur inattendue: {e}", "ERROR")
            results.append((test_name, False))
    
    # Résumé
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}{Colors.END}")
    
    passed = sum(1 for _, success in results if success)
    failed = total_tests - passed
    
    for test_name, success in results:
        status = "✅ PASSÉ" if success else "❌ ÉCHOUÉ"
        color = Colors.GREEN if success else Colors.RED
        print(f"{color}{status:<10} {test_name}{Colors.END}")
    
    print(f"\n{Colors.BOLD}Résultat: {passed}/{total_tests} tests passés{Colors.END}")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS SONT PASSÉS - PRÊT POUR DÉPLOIEMENT !{Colors.END}")
        return 0
    elif failed <= 2:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  QUELQUES PROBLÈMES MINEURS - DÉPLOIEMENT POSSIBLE{Colors.END}")
        return 1
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ TROP D'ERREURS - CORRECTION NÉCESSAIRE AVANT DÉPLOIEMENT{Colors.END}")
        return 2

if __name__ == "__main__":
    sys.exit(main())