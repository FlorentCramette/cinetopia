#!/usr/bin/env python
"""
🗃️ Initialisation Simple Base de Données Préproduction
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Exécute une commande"""
    print(f"  🔧 {command}")
    return subprocess.run(command, shell=True, capture_output=True, text=True)

def main():
    print("""
    🗃️ INITIALISATION BASE PRÉPRODUCTION
    ===================================
    """)
    
    # Sauvegarder .env actuel
    if Path('.env').exists():
        print("📁 Sauvegarde de la configuration actuelle...")
        result = run_command('copy .env .env.backup')
    
    # Copier la config préproduction
    print("⚙️  Application de la configuration préproduction...")
    result = run_command('copy .env.preprod .env')
    if result.returncode != 0:
        print(f"❌ Erreur: {result.stderr}")
        return 1
    
    # Supprimer ancienne base SQLite
    if Path('db_preprod.sqlite3').exists():
        Path('db_preprod.sqlite3').unlink()
        print("  ✅ Ancienne base supprimée")
    
    # Migrations
    print("🗃️ Création de la base de données...")
    result = run_command('python manage.py makemigrations')
    if result.returncode != 0:
        print(f"❌ Erreur makemigrations: {result.stderr}")
    
    result = run_command('python manage.py migrate')
    if result.returncode != 0:
        print(f"❌ Erreur migrate: {result.stderr}")
    else:
        print("  ✅ Base de données créée")
    
    # Créer superutilisateur
    print("👤 Création d'un superutilisateur de test...")
    create_superuser_script = """
from django.contrib.auth.models import User
User.objects.filter(username='admin_test').delete()
User.objects.create_superuser('admin_test', 'admin@test.com', 'testpass123')
print('Superutilisateur créé: admin_test / testpass123')
"""
    
    with open('create_user.py', 'w') as f:
        f.write(create_superuser_script)
    
    result = run_command('python manage.py shell < create_user.py')
    if result.returncode == 0:
        print("  ✅ Utilisateur test créé")
    else:
        print(f"  ⚠️  Erreur création utilisateur: {result.stderr}")
    
    # Nettoyer
    if Path('create_user.py').exists():
        Path('create_user.py').unlink()
    
    # Restaurer .env original
    print("🔄 Restauration de la configuration originale...")
    if Path('.env.backup').exists():
        result = run_command('copy .env.backup .env')
        if Path('.env.backup').exists():
            Path('.env.backup').unlink()
        print("  ✅ Configuration restaurée")
    
    print("\n🎉 BASE DE DONNÉES PRÉPRODUCTION PRÊTE!")
    print("📁 Fichier: db_preprod.sqlite3")
    print("👤 Admin: admin_test / testpass123")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())