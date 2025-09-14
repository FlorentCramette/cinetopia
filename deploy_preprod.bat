@echo off
title Cinetopia - Déploiement Préproduction
color 0E

echo.
echo  ========================================
echo  🚀 CINETOPIA - DEPLOIEMENT PREPROD
echo  ========================================
echo.

echo [INFO] Configuration de l'environnement de préproduction...

REM Sauvegarder l'ancien .env
if exist .env (
    echo [INFO] Sauvegarde de la configuration actuelle...
    copy .env .env.backup
)

REM Utiliser la configuration préproduction
echo [INFO] Application de la configuration préproduction...
copy .env.preprod .env

echo [INFO] Création d'un environnement virtuel propre...
if exist venv_preprod rmdir /s /q venv_preprod 2>nul
python -m venv venv_preprod --clear

echo [INFO] Activation de l'environnement de préproduction...
call venv_preprod\Scripts\activate.bat

echo [INFO] Installation des dépendances en mode production...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo.
echo [INFO] Configuration de la base de données préproduction...
python manage.py makemigrations --verbosity=0 2>nul
python manage.py migrate --verbosity=0

echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput --verbosity=0

echo [INFO] Vérification de la configuration...
python manage.py check --deploy

echo.
echo [INFO] Tests automatisés en environnement préproduction...
python test_app.py

echo.
echo  ========================================
echo  🌐 SERVEUR PRÉPRODUCTION
echo  ========================================
echo.
echo [SUCCESS] ✅ Environnement préproduction prêt !
echo [INFO] 🌐 Serveur accessible sur : http://127.0.0.1:8080
echo [INFO] 🔒 Mode : Production (DEBUG=False)
echo [INFO] ⏹️  Pour arrêter : Ctrl+C
echo.

REM Ouvrir le navigateur sur le port de préproduction
start http://127.0.0.1:8080

echo [INFO] Démarrage du serveur en mode préproduction...
python manage.py runserver 127.0.0.1:8080

echo.
echo [INFO] Tests préproduction terminés
echo [INFO] Restauration de la configuration originale...
if exist .env.backup (
    copy .env.backup .env
    del .env.backup
)

pause