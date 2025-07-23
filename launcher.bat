@echo off
title Assistant Vocal PC - Launcher
color 0A

echo.
echo ========================================
echo    Assistant Vocal PC avec Mistral
echo ========================================
echo.

:menu
echo Choisissez votre mode de lancement:
echo.
echo 1. Assistant Hybride (Recommande)
echo    - Auto-detection audio
echo    - Mode vocal + texte
echo.
echo 2. Assistant Test (Texte uniquement)
echo    - Pas d'audio requis
echo    - Ideal pour tester
echo.
echo 3. Assistant Vocal Complet
echo    - Necessite tous les composants audio
echo    - Mode vocal avance
echo.
echo 4. Tests de connexion
echo    - Test API Ollama/Mistral
echo    - Verification du systeme
echo.
echo 5. Installation/Mise a jour
echo    - Installer les dependances
echo    - Mettre a jour les packages
echo.
echo 0. Quitter
echo.

set /p choice="Votre choix (0-5): "

if "%choice%"=="1" goto hybride
if "%choice%"=="2" goto test
if "%choice%"=="3" goto vocal
if "%choice%"=="4" goto tests
if "%choice%"=="5" goto install
if "%choice%"=="0" goto quit

echo Choix invalide, veuillez reessayer.
echo.
goto menu

:hybride
echo.
echo Lancement de l'Assistant Hybride...
echo.
python assistant_hybride.py
echo.
echo Assistant ferme. Appuyez sur une touche pour retourner au menu.
pause >nul
goto menu

:test
echo.
echo Lancement de l'Assistant Test...
echo.
python assistant_test.py
echo.
echo Assistant ferme. Appuyez sur une touche pour retourner au menu.
pause >nul
goto menu

:vocal
echo.
echo Lancement de l'Assistant Vocal Complet...
echo.
python assistant_vocal.py
echo.
echo Assistant ferme. Appuyez sur une touche pour retourner au menu.
pause >nul
goto menu

:tests
echo.
echo Lancement des tests...
echo.
echo Test 1: Connexion Ollama
curl -s http://127.0.0.1:11434
echo.
echo.
echo Test 2: Liste des modeles
ollama list
echo.
echo Test 3: Test API simple
powershell -File test_mistral_simple.ps1
echo.
echo Tests termines. Appuyez sur une touche pour continuer.
pause >nul
goto menu

:install
echo.
echo Installation/Mise a jour des dependances...
echo.
pip install -r requirements.txt
echo.
echo Installation terminee. Appuyez sur une touche pour continuer.
pause >nul
goto menu

:quit
echo.
echo Au revoir !
echo.
timeout /t 2 >nul
exit

:error
echo.
echo Une erreur s'est produite.
echo Verifiez que Python et Ollama sont installes.
echo.
pause
goto menu
