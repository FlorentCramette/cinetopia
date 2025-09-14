#!/usr/bin/env python3
"""
Cinetopia - Lanceur d'application
================================

Script de lancement automatisé pour l'application Django Cinetopia.
Vérifie l'environnement, configure les dépendances et lance le serveur.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Affiche la bannière de l'application."""
    print(f"\n{Colors.CYAN}{'='*50}")
    print(f"{Colors.GREEN}{Colors.BOLD}🎬 CINETOPIA - LANCEUR APPLICATION")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")

def print_status(message, status_type="INFO"):
    """Affiche un message de statut coloré."""
    color_map = {
        "INFO": Colors.WHITE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }
    color = color_map.get(status_type, Colors.WHITE)
    print(f"{color}[{status_type}] {message}{Colors.END}")

def run_command(command, shell=True, capture_output=False):
    """Exécute une commande et retourne le résultat."""
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, shell=shell)
            return result.returncode == 0, ""
    except Exception as e:
        print_status(f"Erreur lors de l'exécution de '{command}': {e}", "ERROR")
        return False, ""

def check_python():
    """Vérifie que Python est installé."""
    success, version = run_command("python --version", capture_output=True)
    if success:
        print_status(f"Python détecté: {version}", "SUCCESS")
        return True
    else:
        print_status("Python n'est pas installé ou n'est pas dans le PATH", "ERROR")
        print_status("Veuillez installer Python 3.8+ depuis https://python.org", "ERROR")
        return False

def setup_env_file():
    """Configure le fichier .env si nécessaire."""
    if not Path(".env").exists():
        print_status("Fichier .env manquant !", "WARNING")
        if Path(".env.example").exists():
            print_status("Copie de .env.example vers .env...", "INFO")
            import shutil
            shutil.copy(".env.example", ".env")
            print_status("Veuillez configurer le fichier .env avec vos paramètres :", "WARNING")
            print_status("- SECRET_KEY", "INFO")
            print_status("- DB_PASSWORD", "INFO")
            print_status("- WEATHER_API_KEY (optionnel)", "INFO")
            
            # Ouvrir le fichier .env selon l'OS
            if platform.system() == "Windows":
                os.system("notepad .env")
            elif platform.system() == "Darwin":  # macOS
                os.system("open -e .env")
            else:  # Linux
                os.system("nano .env || vim .env || gedit .env")
            
            input("\nAppuyez sur Entrée après avoir configuré .env...")
        else:
            print_status("Fichier .env.example introuvable !", "ERROR")
            return False
    return True

def check_uv():
    """Vérifie si uv est installé, sinon l'installe."""
    success, _ = run_command("uv --version", capture_output=True)
    if success:
        print_status("uv détecté - utilisation pour l'installation rapide", "SUCCESS")
        return True
    else:
        print_status("Installation d'uv pour des installations plus rapides...", "INFO")
        success, _ = run_command("pip install uv")
        if success:
            print_status("uv installé avec succès", "SUCCESS")
            return True
        else:
            print_status("Échec de l'installation d'uv, utilisation de pip classique", "WARNING")
            return False

def setup_virtual_env():
    """Configure l'environnement virtuel avec uv."""
    venv_path = Path("venv")
    use_uv = check_uv()
    
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print_status("Création de l'environnement virtuel...", "INFO")
        if use_uv:
            success, _ = run_command("uv venv venv")
        else:
            success, _ = run_command("python -m venv venv")
        
        if not success:
            print_status("Erreur lors de la création de l'environnement virtuel", "ERROR")
            return False
        
        if use_uv:
            print_status("Installation rapide des dépendances avec uv...", "INFO")
            pip_cmd = f"uv pip install -r requirements.txt --python {python_exe}"
            success, _ = run_command(pip_cmd)
        else:
            print_status("Mise à jour de pip, setuptools et wheel...", "INFO")
            upgrade_cmd = f"{python_exe} -m pip install --upgrade pip setuptools wheel"
            success, _ = run_command(upgrade_cmd)
            
            print_status("Installation des dépendances avec pip...", "INFO")
            pip_cmd = f"{python_exe} -m pip install -r requirements.txt"
            success, _ = run_command(pip_cmd)
        
        if not success:
            print_status("Erreur lors de l'installation des dépendances", "ERROR")
            if use_uv:
                print_status("Tentative avec pip classique...", "WARNING")
                pip_cmd = f"{python_exe} -m pip install -r requirements.txt"
                success, _ = run_command(pip_cmd)
            
            if not success:
                print_status("Installation des packages essentiels uniquement...", "WARNING")
                essential_packages = [
                    "Django==5.0.6",
                    "python-dotenv==1.0.0", 
                    "requests==2.31.0"
                ]
                
                for package in essential_packages:
                    print_status(f"Installation de {package}...", "INFO")
                    if use_uv:
                        install_cmd = f"uv pip install {package} --python {python_exe}"
                    else:
                        install_cmd = f"{python_exe} -m pip install {package}"
                    run_command(install_cmd)
    
    print_status("Environnement virtuel configuré", "SUCCESS")
    return str(python_exe)

def setup_database(python_exe):
    """Configure la base de données."""
    print_status("Vérification de la base de données...", "INFO")
    
    # Créer les migrations si nécessaire
    makemigrations_cmd = f"{python_exe} manage.py makemigrations"
    run_command(makemigrations_cmd)
    
    # Appliquer les migrations
    migrate_cmd = f"{python_exe} manage.py migrate"
    success, _ = run_command(migrate_cmd)
    if not success:
        print_status("Erreur lors des migrations", "WARNING")
    
    # Collecter les fichiers statiques
    print_status("Collecte des fichiers statiques...", "INFO")
    collectstatic_cmd = f"{python_exe} manage.py collectstatic --noinput"
    run_command(collectstatic_cmd, capture_output=True)

def start_server(python_exe):
    """Démarre le serveur Django."""
    print(f"\n{Colors.CYAN}{'='*50}")
    print(f"{Colors.GREEN}{Colors.BOLD}🚀 DÉMARRAGE DU SERVEUR DJANGO")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}\n")
    
    print_status("Serveur accessible sur : http://127.0.0.1:8000", "SUCCESS")
    print_status("Pour arrêter le serveur : Ctrl+C", "INFO")
    print()
    
    try:
        server_cmd = f"{python_exe} manage.py runserver 127.0.0.1:8000"
        run_command(server_cmd, capture_output=False)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Arrêt du serveur...{Colors.END}")
    except Exception as e:
        print_status(f"Erreur lors du démarrage du serveur: {e}", "ERROR")
    finally:
        print_status("Serveur arrêté", "INFO")

def main():
    """Point d'entrée principal."""
    print_banner()
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("manage.py").exists():
        print_status("Fichier manage.py non trouvé !", "ERROR")
        print_status("Assurez-vous d'être dans le répertoire racine du projet", "ERROR")
        return 1
    
    # Vérifications et configuration
    if not check_python():
        return 1
    
    if not setup_env_file():
        return 1
    
    python_exe = setup_virtual_env()
    if not python_exe:
        return 1
    
    setup_database(python_exe)
    start_server(python_exe)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())