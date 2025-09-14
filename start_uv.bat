@echo off
title Cinetopia - Lanceur Ultra-Rapide avec UV
color 0A

echo.
echo  ========================================
echo  🚀 CINETOPIA - LANCEUR ULTRA-RAPIDE
echo  ========================================
echo.

echo [INFO] Vérification d'uv...
uv --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation d'uv pour des installations ultra-rapides...
    pip install uv
    if errorlevel 1 (
        echo [ERROR] Impossible d'installer uv, veuillez l'installer manuellement
        echo [INFO] Commande: pip install uv
        pause
        exit /b 1
    )
)

echo [SUCCESS] uv détecté - utilisation pour l'installation rapide

echo [INFO] Suppression de l'ancien environnement virtuel...
if exist venv (
    echo [INFO] Tentative de suppression...
    rmdir /s /q venv 2>nul
    if exist venv (
        echo [WARNING] Certains fichiers sont verrouillés, création d'un nouvel environnement...
    )
)

echo [INFO] Création de l'environnement virtuel avec uv...
uv venv venv
if errorlevel 1 (
    echo [WARNING] Échec avec uv, utilisation de python...
    python -m venv venv
)

echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo [INFO] Installation ultra-rapide des dépendances avec uv...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Échec avec uv, tentative avec pip...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [INFO] Installation des packages essentiels uniquement...
        uv pip install Django==5.0.6 python-dotenv==1.0.0 requests==2.31.0
    )
)

echo.
echo [INFO] Vérification du fichier .env...
if not exist .env (
    copy .env.example .env
    echo [ACTION] Veuillez configurer .env et relancer
    notepad .env
    pause
    exit /b
)

echo [INFO] Configuration de la base de données...
python manage.py makemigrations 2>nul
python manage.py migrate

echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput 2>nul

echo.
echo  ========================================
echo  🎬 DÉMARRAGE DU SERVEUR DJANGO
echo  ========================================
echo.
echo [SUCCESS] Serveur accessible sur : http://127.0.0.1:8000
echo [INFO] Pour arrêter : Ctrl+C
echo [INFO] Recommandations ML désactivées si packages non installés
echo.

python manage.py runserver 127.0.0.1:8000

echo.
echo [INFO] Serveur arrêté
pause