@echo off
title Cinetopia - Lanceur Simple
color 0A

echo.
echo  ========================================
echo  🎬 CINETOPIA - LANCEUR SIMPLE
echo  ========================================
echo.

echo [INFO] Suppression de l'ancien environnement virtuel...
if exist venv rmdir /s /q venv

echo [INFO] Création d'un nouvel environnement virtuel...
python -m venv venv

echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip

echo [INFO] Installation des packages essentiels...
python -m pip install Django==5.0.6
python -m pip install python-dotenv==1.0.0
python -m pip install requests==2.31.0

echo [INFO] Tentative d'installation des packages ML (optionnels)...
python -m pip install numpy --only-binary=numpy || echo [WARNING] Numpy non installé
python -m pip install pandas --only-binary=pandas || echo [WARNING] Pandas non installé  
python -m pip install scikit-learn --only-binary=scikit-learn || echo [WARNING] Scikit-learn non installé

echo [INFO] Tentative d'installation de mysqlclient...
python -m pip install mysqlclient || echo [WARNING] MySQLclient non installé - utilisation de SQLite

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
python manage.py makemigrations
python manage.py migrate

echo [INFO] Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo.
echo  ========================================
echo  🚀 DÉMARRAGE DU SERVEUR
echo  ========================================
echo.
echo [INFO] Serveur accessible sur : http://127.0.0.1:8000
echo [INFO] Pour arrêter : Ctrl+C
echo.

python manage.py runserver 127.0.0.1:8000

echo.
echo [INFO] Serveur arrêté
pause