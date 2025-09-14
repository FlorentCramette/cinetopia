@echo off
title Cinetopia - Lanceur Application
color 0A

echo.
echo  ========================================
echo  🎬 CINETOPIA - LANCEUR APPLICATION
echo  ========================================
echo.

echo [INFO] Vérification de l'environnement...

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier si le fichier .env existe
if not exist .env (
    echo [ATTENTION] Fichier .env manquant !
    echo Copie de .env.example vers .env...
    copy .env.example .env
    echo.
    echo [ACTION REQUISE] Veuillez configurer le fichier .env avec vos paramètres :
    echo - SECRET_KEY
    echo - DB_PASSWORD
    echo - WEATHER_API_KEY (optionnel)
    echo.
    notepad .env
    echo Appuyez sur une touche après avoir configuré .env...
    pause >nul
)

echo [INFO] Activation de l'environnement virtuel...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Environnement virtuel activé
) else (
    echo [ATTENTION] Environnement virtuel non trouvé
    echo Création de l'environnement virtuel...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [INFO] Installation des dépendances...
    pip install -r requirements.txt
)

echo.
echo [INFO] Vérification de la base de données...
python manage.py makemigrations --check >nul 2>&1
if errorlevel 1 (
    echo [INFO] Création des migrations...
    python manage.py makemigrations
)

python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo [INFO] Application des migrations...
    python manage.py migrate
)

echo.
echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput >nul 2>&1

echo.
echo  ========================================
echo  🚀 DÉMARRAGE DU SERVEUR DJANGO
echo  ========================================
echo.
echo [INFO] Serveur accessible sur : http://127.0.0.1:8000
echo [INFO] Pour arrêter le serveur : Ctrl+C
echo.

REM Lancer le serveur Django
python manage.py runserver 127.0.0.1:8000

echo.
echo [INFO] Serveur arrêté
pause