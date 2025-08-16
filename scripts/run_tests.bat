@echo off
REM Script batch pour lancer les tests Aegis Bot sous Windows
REM Usage: run_tests.bat [options]
REM Options: -c (coverage), -v (verbose), -i (interactive)

setlocal enabledelayedexpansion

echo.
echo 🤖 AEGIS BOT - SYSTEME DE TESTS AUTOMATISES
echo =============================================
echo.

REM Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur: Python n'est pas installé ou pas dans le PATH
    echo.
    echo 💡 Solutions:
    echo    - Installez Python depuis https://python.org
    echo    - Ajoutez Python au PATH système
    echo    - Utilisez 'py' au lieu de 'python' sur certains systèmes
    echo.
    pause
    exit /b 1
)

REM Afficher la version de Python
echo 🐍 Version Python:
python --version
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "bot.py" (
    echo ❌ Erreur: bot.py non trouvé
    echo.
    echo 📁 Répertoire actuel: %CD%
    echo 💡 Exécutez ce script depuis le répertoire racine du bot Aegis
    echo.
    pause
    exit /b 1
)

REM Vérifier si le dossier tests existe
if not exist "tests\" (
    echo ❌ Erreur: Dossier 'tests' non trouvé
    echo 💡 Le système de tests n'est pas configuré
    echo.
    pause
    exit /b 1
)

REM Construire la commande avec les arguments
set "python_cmd=python run_tests.py"

REM Passer tous les arguments au script Python
if "%~1" neq "" (
    set "python_cmd=%python_cmd% %*"
)

echo 🚀 Lancement des tests...
echo Commande: %python_cmd%
echo.

REM Lancer le script Python de tests
%python_cmd%

REM Capturer le code de retour
set exit_code=%errorlevel%

echo.
echo =============================================

if %exit_code% equ 0 (
    echo ✅ Tests terminés avec succès
) else (
    echo ❌ Tests terminés avec des erreurs (code: %exit_code%^)
)

echo.
echo 💡 Commandes utiles:
echo    run_tests.bat           - Mode interactif
echo    run_tests.bat -c        - Avec couverture de code
echo    run_tests.bat -v        - Mode verbose
echo    run_tests.bat -c -html  - Couverture + rapport HTML
echo.

REM Ne faire pause que si lancé en double-clic (pas depuis cmd)
echo %cmdcmdline% | find /i "/c" >nul
if not errorlevel 1 (
    pause
)

exit /b %exit_code%