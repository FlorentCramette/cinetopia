# Lanceurs Cinetopia

Ce dossier contient plusieurs options pour lancer facilement l'application Cinetopia.

## 🚀 Options de lancement

### 1. Lanceur principal (Recommandé)
```bash
python start_cinetopia.py
```
**Avantages :**
- Cross-platform (Windows, macOS, Linux)
- Interface colorée et informative
- Gestion automatique de l'environnement virtuel
- Vérifications complètes avant démarrage

### 2. Lanceur Windows (Double-clic)
```bash
cinetopia.bat
```
**Avantages :**
- Démarrage en un double-clic
- Pas besoin d'ouvrir un terminal
- Lance automatiquement le script Python

### 3. Lanceur PowerShell
```powershell
.\start_cinetopia.ps1
```
**Avantages :**
- Interface PowerShell moderne
- Gestion d'erreurs avancée
- Couleurs et formatage

### 4. Lanceur Batch classique
```bash
start_cinetopia.bat
```
**Avantages :**
- Compatible avec tous les Windows
- Interface simple et claire
- Gestion automatique de l'environnement

## 📋 Ce que font les lanceurs

1. **Vérification de Python** : S'assure que Python est installé
2. **Configuration .env** : Copie .env.example si .env n'existe pas
3. **Environnement virtuel** : Crée et active automatiquement l'environnement
4. **Dépendances** : Installe les packages nécessaires
5. **Base de données** : Applique les migrations Django
6. **Fichiers statiques** : Collecte les assets
7. **Serveur** : Lance Django sur http://127.0.0.1:8000

## ⚙️ Configuration automatique

Les lanceurs vérifient et configurent automatiquement :

- Environnement virtuel Python
- Fichier de configuration .env
- Migrations de base de données
- Collection des fichiers statiques
- Dépendances Python

## 🔧 Résolution de problèmes

### Python non trouvé
Installez Python 3.8+ depuis [python.org](https://python.org)

### Erreur de base de données
Vérifiez vos paramètres MySQL dans le fichier .env

### Erreur de permissions PowerShell
Exécutez : `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Port 8000 occupé
Changez le port dans le lanceur ou arrêtez l'autre service

## 📝 Personnalisation

Vous pouvez modifier les lanceurs pour :
- Changer le port par défaut
- Ajouter des vérifications supplémentaires
- Modifier l'interface utilisateur
- Ajouter des options de développement

## 🎯 Utilisation recommandée

1. **Développement** : `python start_cinetopia.py`
2. **Démo rapide** : Double-clic sur `cinetopia.bat`
3. **PowerShell users** : `.\start_cinetopia.ps1`