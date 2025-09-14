@echo off
title Cinetopia - Lanceur Rapide et Fiable
color 0A

echo.
echo  ========================================
echo  🎬 CINETOPIA - LANCEUR RAPIDE
echo  ========================================
echo.

REM Supprimer proprement l'ancien environnement
echo [INFO] Nettoyage de l'environnement...
if exist venv (
    echo [INFO] Suppression de l'ancien environnement virtuel...
    timeout /t 2 /nobreak >nul
    rmdir /s /q venv 2>nul
)

echo [INFO] Création d'un nouvel environnement virtuel...
python -m venv venv --clear
if errorlevel 1 (
    echo [ERROR] Impossible de créer l'environnement virtuel
    pause
    exit /b 1
)

echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip --quiet

echo [INFO] Installation des packages essentiels...
python -m pip install Django==5.0.6 --quiet
python -m pip install python-dotenv==1.0.0 --quiet  
python -m pip install requests==2.31.0 --quiet

echo [INFO] Installation des packages optionnels...
python -m pip install numpy pandas scikit-learn mysqlclient --quiet 2>nul || echo [WARNING] Certains packages ML non installés

echo.
echo [INFO] Vérification du fichier .env...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo [SUCCESS] Fichier .env créé à partir de .env.example
        echo [ACTION] Configuration nécessaire - ouverture du fichier...
        notepad .env
        echo.
        echo Appuyez sur une touche après avoir configuré .env...
        pause >nul
    ) else (
        echo [ERROR] Fichier .env.example introuvable
        pause
        exit /b 1
    )
)

echo [INFO] Configuration de la base de données...
python manage.py makemigrations --verbosity=0 2>nul
python manage.py migrate --verbosity=0

echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput --verbosity=0 2>nul

echo.
echo  ========================================
echo  🚀 DÉMARRAGE DU SERVEUR DJANGO
echo  ========================================
echo.
echo [SUCCESS] ✅ Environnement prêt !
echo [INFO] 🌐 Serveur accessible sur : http://127.0.0.1:8000
echo [INFO] ⏹️  Pour arrêter : Ctrl+C
echo.

REM Ouvrir automatiquement le navigateur
start http://127.0.0.1:8000

python manage.py runserver 127.0.0.1:8000

echo.
echo [INFO] Serveur arrêté
pause