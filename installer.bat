@echo off
echo ================================================
echo Installation de l'Assistant Vocal PC
echo ================================================

echo.
echo 1. Verification de Python...
python --version
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo 2. Verification de pip...
pip --version
if %errorlevel% neq 0 (
    echo ERREUR: pip n'est pas disponible
    pause
    exit /b 1
)

echo.
echo 3. Installation des dependances Python...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERREUR lors de l'installation des dependances!
    echo.
    echo Solutions possibles:
    echo - Verifiez votre connexion internet
    echo - Executez en tant qu'administrateur
    echo - Installez manuellement: pip install speech_recognition pyttsx3 pyaudio requests
    echo.
    pause
    exit /b 1
)

echo.
echo 4. Verification d'Ollama...
curl -s http://127.0.0.1:11434 > nul 2>&1
if %errorlevel% neq 0 (
    echo ATTENTION: Ollama ne semble pas accessible sur http://127.0.0.1:11434
    echo Assurez-vous qu'Ollama est demarrer avec: ollama serve
    echo.
)

echo.
echo ================================================
echo Installation terminee avec succes!
echo ================================================
echo.
echo Pour demarrer l'assistant:
echo python assistant_vocal.py
echo.
pause
