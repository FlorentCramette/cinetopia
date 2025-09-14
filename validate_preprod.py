#!/usr/bin/env python
"""
🚀 Validation Finale Préproduction Cinetopia
Script de validation complète avant fusion vers main
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_command(command, capture_output=True):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"

def check_git_status():
    """Vérifie l'état du repository git"""
    print("🔍 Vérification de l'état Git...")
    
    # Vérifier la branche actuelle
    success, branch_output, _ = run_command("git branch --show-current")
    if success:
        current_branch = branch_output.strip()
        print(f"  📍 Branche actuelle: {current_branch}")
    
    # Vérifier les changements non commitées
    success, status_output, _ = run_command("git status --porcelain")
    if success and status_output.strip():
        print("  ⚠️  Changements non commitées détectés:")
        print(f"     {status_output}")
        return False
    
    # Vérifier les commits en avance
    success, ahead_output, _ = run_command("git log origin/dev..HEAD --oneline")
    if success and ahead_output.strip():
        commits = ahead_output.strip().split('\n')
        print(f"  📤 {len(commits)} commit(s) en avance sur origin/dev")
    
    return True

def run_comprehensive_tests():
    """Exécute tous les tests disponibles"""
    print("🧪 Exécution des tests complets...")
    
    test_results = {}
    
    # Tests préproduction
    success, output, error = run_command("python test_preprod.py")
    test_results['preprod'] = {
        'success': success,
        'output': output,
        'error': error
    }
    
    # Tests de base
    if Path("test_app.py").exists():
        success, output, error = run_command("python test_app.py")
        test_results['base'] = {
            'success': success,
            'output': output,
            'error': error
        }
    
    return test_results

def check_security():
    """Vérifications de sécurité"""
    print("🔒 Vérifications de sécurité...")
    
    security_issues = []
    
    # Vérifier les fichiers sensibles
    sensitive_files = [".env", ".env.dev", ".env.local"]
    for file in sensitive_files:
        if Path(file).exists():
            # Vérifier si le fichier est dans .gitignore
            success, gitignore_content, _ = run_command("cat .gitignore")
            if success and file not in gitignore_content:
                security_issues.append(f"Fichier sensible {file} non ignoré par Git")
    
    # Vérifier les clés secrètes dans le code
    success, grep_output, _ = run_command('grep -r "SECRET_KEY.*=" . --include="*.py" --exclude-dir=venv*')
    if success and "SECRET_KEY" in grep_output and "os.environ" not in grep_output:
        security_issues.append("Clé secrète possiblement hardcodée")
    
    return security_issues

def generate_deployment_report():
    """Génère un rapport de déploiement"""
    print("📋 Génération du rapport de déploiement...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "branch": "preprod",
        "status": "ready",
        "checks": {}
    }
    
    # Informations Git
    success, branch, _ = run_command("git branch --show-current")
    if success:
        report["current_branch"] = branch.strip()
    
    success, last_commit, _ = run_command("git log -1 --format='%H %s'")
    if success:
        report["last_commit"] = last_commit.strip()
    
    # Sauvegarder le rapport
    with open("deployment_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Fonction principale de validation"""
    print("""
    🚀 VALIDATION FINALE PRÉPRODUCTION
    ===================================
    Vérification complète avant fusion vers main
    """)
    
    validation_passed = True
    
    # 1. Vérification Git
    if not check_git_status():
        print("❌ Problèmes Git détectés")
        validation_passed = False
    else:
        print("✅ État Git correct")
    
    # 2. Tests complets
    test_results = run_comprehensive_tests()
    all_tests_passed = all(result['success'] for result in test_results.values())
    
    if all_tests_passed:
        print("✅ Tous les tests sont passés")
    else:
        print("❌ Certains tests ont échoué")
        for test_name, result in test_results.items():
            if not result['success']:
                print(f"  - {test_name}: ÉCHEC")
                if result['error']:
                    print(f"    Erreur: {result['error']}")
        validation_passed = False
    
    # 3. Vérifications de sécurité
    security_issues = check_security()
    if security_issues:
        print("❌ Problèmes de sécurité détectés:")
        for issue in security_issues:
            print(f"  - {issue}")
        validation_passed = False
    else:
        print("✅ Sécurité validée")
    
    # 4. Génération du rapport
    report = generate_deployment_report()
    print(f"✅ Rapport généré: deployment_report.json")
    
    # Résultat final
    print("\n" + "="*50)
    if validation_passed:
        print("🎉 VALIDATION RÉUSSIE!")
        print("✅ Le projet est prêt pour la fusion vers main")
        print("\nProchaines étapes:")
        print("  1. git checkout main")
        print("  2. git merge preprod")
        print("  3. git push origin main")
        print("  4. Déploiement en production")
        return 0
    else:
        print("❌ VALIDATION ÉCHOUÉE!")
        print("⚠️  Corrigez les problèmes avant de continuer")
        print("\nActions requises:")
        print("  1. Corriger les erreurs identifiées")
        print("  2. Commitez les corrections")
        print("  3. Relancer la validation")
        return 1

if __name__ == "__main__":
    sys.exit(main())