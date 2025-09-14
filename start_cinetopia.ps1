# Cinetopia - Lanceur PowerShell
# ====================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎬 CINETOPIA - LANCEUR APPLICATION" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $color = switch ($Type) {
        "INFO" { "White" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$Type] $Message" -ForegroundColor $color
}

# Vérifier si Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-StatusMessage "Python détecté: $pythonVersion" "SUCCESS"
} catch {
    Write-StatusMessage "Python n'est pas installé ou n'est pas dans le PATH" "ERROR"
    Write-StatusMessage "Veuillez installer Python 3.8+ depuis https://python.org" "ERROR"
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# Vérifier le fichier .env
if (-not (Test-Path ".env")) {
    Write-StatusMessage "Fichier .env manquant !" "WARNING"
    if (Test-Path ".env.example") {
        Write-StatusMessage "Copie de .env.example vers .env..." "INFO"
        Copy-Item ".env.example" ".env"
        Write-StatusMessage "Veuillez configurer le fichier .env avec vos paramètres" "WARNING"
        notepad .env
        Read-Host "Appuyez sur Entrée après avoir configuré .env"
    } else {
        Write-StatusMessage "Fichier .env.example introuvable !" "ERROR"
        exit 1
    }
}

# Vérifier/créer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-StatusMessage "Activation de l'environnement virtuel..." "INFO"
    & "venv\Scripts\Activate.ps1"
    Write-StatusMessage "Environnement virtuel activé" "SUCCESS"
} else {
    Write-StatusMessage "Création de l'environnement virtuel..." "INFO"
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-StatusMessage "Installation des dépendances..." "INFO"
    pip install -r requirements.txt
}

Write-Host ""
Write-StatusMessage "Vérification de la base de données..." "INFO"

# Vérifier et appliquer les migrations
try {
    $migrationCheck = python manage.py migrate --check 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Application des migrations..." "INFO"
        python manage.py makemigrations
        python manage.py migrate
    }
} catch {
    Write-StatusMessage "Erreur lors de la vérification des migrations" "WARNING"
}

# Collecter les fichiers statiques
Write-StatusMessage "Collecte des fichiers statiques..." "INFO"
python manage.py collectstatic --noinput | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DÉMARRAGE DU SERVEUR DJANGO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-StatusMessage "Serveur accessible sur : http://127.0.0.1:8000" "SUCCESS"
Write-StatusMessage "Pour arrêter le serveur : Ctrl+C" "INFO"
Write-Host ""

# Lancer le serveur Django
try {
    python manage.py runserver 127.0.0.1:8000
} catch {
    Write-StatusMessage "Erreur lors du démarrage du serveur" "ERROR"
} finally {
    Write-Host ""
    Write-StatusMessage "Serveur arrêté" "INFO"
    Read-Host "Appuyez sur Entrée pour quitter"
}