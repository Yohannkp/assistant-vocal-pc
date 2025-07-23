"""
Diagnostic Audio Avancé
=======================
Test pour identifier le problème TTS
"""

import pyttsx3
import time
import os
import sys

def test_basic_tts():
    """Test TTS de base"""
    print("🧪 Test TTS de base...")
    try:
        engine = pyttsx3.init()
        engine.say("Test audio de base")
        engine.runAndWait()
        print("✅ Test de base réussi")
        
        # Demander confirmation
        heard = input("Avez-vous entendu le test de base ? (o/n): ").lower()
        return heard in ['o', 'oui', 'y', 'yes']
    except Exception as e:
        print(f"❌ Test de base échoué: {e}")
        return False

def test_multiple_engines():
    """Test avec plusieurs instances"""
    print("🧪 Test instances multiples...")
    try:
        for i in range(3):
            engine = pyttsx3.init()
            engine.say(f"Test instance {i+1}")
            engine.runAndWait()
            engine.stop()
            engine = None
            time.sleep(0.5)
        print("✅ Test instances multiples réussi")
        
        heard = input("Avez-vous entendu les 3 tests ? (o/n): ").lower()
        return heard in ['o', 'oui', 'y', 'yes']
    except Exception as e:
        print(f"❌ Test instances multiples échoué: {e}")
        return False

def test_windows_sapi():
    """Test avec Windows SAPI direct"""
    print("🧪 Test Windows SAPI...")
    try:
        cmd = 'powershell -Command "Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SetOutputToDefaultAudioDevice(); $synth.Speak(\\"Test Windows SAPI\\")"'
        os.system(cmd)
        print("✅ Test SAPI réussi")
        
        heard = input("Avez-vous entendu le test SAPI ? (o/n): ").lower()
        return heard in ['o', 'oui', 'y', 'yes']
    except Exception as e:
        print(f"❌ Test SAPI échoué: {e}")
        return False

def test_voice_configuration():
    """Test configuration des voix"""
    print("🧪 Test configuration voix...")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"Voix disponibles: {len(voices) if voices else 0}")
        for i, voice in enumerate(voices):
            if voice:
                print(f"  {i}: {voice.name}")
        
        # Test avec voix française
        if voices:
            for voice in voices:
                if voice and 'hortense' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"Voix sélectionnée: {voice.name}")
                    break
        
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        
        engine.say("Test configuration voix française")
        engine.runAndWait()
        
        print("✅ Test configuration réussi")
        heard = input("Avez-vous entendu le test de configuration ? (o/n): ").lower()
        return heard in ['o', 'oui', 'y', 'yes']
    except Exception as e:
        print(f"❌ Test configuration échoué: {e}")
        return False

def test_audio_devices():
    """Test dispositifs audio"""
    print("🧪 Test dispositifs audio...")
    
    # Test avec beep système
    try:
        import winsound
        winsound.Beep(1000, 500)  # 1000Hz pendant 500ms
        print("✅ Beep système émis")
        
        heard = input("Avez-vous entendu le beep ? (o/n): ").lower()
        if not heard in ['o', 'oui', 'y', 'yes']:
            print("❌ Problème audio système détecté")
            return False
    except Exception as e:
        print(f"⚠️ Impossible de tester le beep: {e}")
    
    return True

def diagnostic_complet():
    """Diagnostic complet audio"""
    print("🎯 Diagnostic Audio Complet")
    print("=" * 50)
    
    tests = [
        ("Dispositifs audio", test_audio_devices),
        ("TTS de base", test_basic_tts),
        ("Configuration voix", test_voice_configuration),
        ("Instances multiples", test_multiple_engines),
        ("Windows SAPI", test_windows_sapi)
    ]
    
    resultats = {}
    
    for nom, test_func in tests:
        print(f"\n{'='*20} {nom} {'='*20}")
        resultats[nom] = test_func()
        time.sleep(1)
    
    # Analyse des résultats
    print(f"\n📊 Résultats:")
    for nom, resultat in resultats.items():
        status = "✅ OK" if resultat else "❌ PROBLÈME"
        print(f"  {nom}: {status}")
    
    # Recommandations
    print(f"\n💡 Diagnostic:")
    
    if not resultats.get("Dispositifs audio", False):
        print("🔴 PROBLÈME CRITIQUE: Aucun son système détecté")
        print("   → Vérifiez vos haut-parleurs/casque")
        print("   → Vérifiez le volume système")
        print("   → Testez avec un autre logiciel audio")
    elif not resultats.get("TTS de base", False):
        print("🟡 PROBLÈME TTS: pyttsx3 ne fonctionne pas")
        print("   → Réinstallez pyttsx3: pip uninstall pyttsx3 && pip install pyttsx3")
        print("   → Utilisez la méthode Windows SAPI comme alternative")
    elif not resultats.get("Instances multiples", False):
        print("🟠 PROBLÈME INSTANCES: Conflit entre plusieurs moteurs TTS")
        print("   → Utilisez une seule instance à la fois")
        print("   → Ajoutez des délais entre les synthèses")
    elif resultats.get("Windows SAPI", False):
        print("🟢 SOLUTION: Windows SAPI fonctionne")
        print("   → Utilisez exclusivement la méthode SAPI")
    else:
        print("❓ PROBLÈME MYSTÈRE: Tous les tests échouent")
        print("   → Redémarrez votre PC")
        print("   → Vérifiez les pilotes audio")

if __name__ == "__main__":
    diagnostic_complet()
