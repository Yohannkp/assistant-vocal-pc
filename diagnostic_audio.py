"""
Diagnostic Audio pour Assistant Vocal
====================================

Script pour diagnostiquer les problèmes de synthèse vocale
"""

import pyttsx3
import time

def test_tts_simple():
    """Test simple de TTS"""
    print("🧪 Test TTS simple...")
    
    try:
        engine = pyttsx3.init()
        engine.say("Test simple")
        engine.runAndWait()
        print("✅ Test simple réussi")
        return True
    except Exception as e:
        print(f"❌ Test simple échoué: {e}")
        return False

def test_tts_multiple():
    """Test de TTS multiple pour reproduire le problème"""
    print("🧪 Test TTS multiple...")
    
    try:
        engine = pyttsx3.init()
        
        # Configuration
        voices = engine.getProperty('voices')
        if voices:
            for voice in voices:
                if voice and 'french' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"Voix française: {voice.name}")
                    break
        
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        
        # Tests multiples
        phrases = [
            "Première phrase",
            "Deuxième phrase", 
            "Troisième phrase",
            "Quatrième phrase"
        ]
        
        for i, phrase in enumerate(phrases, 1):
            print(f"🔊 Test {i}: {phrase}")
            engine.stop()  # Arrêter avant chaque phrase
            time.sleep(0.1)
            engine.say(phrase)
            engine.runAndWait()
            time.sleep(0.2)
            print(f"✅ Test {i} terminé")
        
        print("✅ Test multiple réussi")
        return True
        
    except Exception as e:
        print(f"❌ Test multiple échoué: {e}")
        return False

def test_tts_conversation():
    """Test simulant une conversation"""
    print("🧪 Test simulation conversation...")
    
    try:
        engine = pyttsx3.init()
        
        # Configuration voix française
        voices = engine.getProperty('voices')
        if voices:
            for voice in voices:
                if voice and 'hortense' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"Voix: {voice.name}")
                    break
        
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 1.0)
        
        # Simulation conversation complète
        conversation = [
            "Présent ! Je vous écoute.",
            "Compris ! Je traite votre demande.",
            "Connexion à Mistral en cours.",
            "Réponse reçue de Mistral avec succès.",
            "Voici ma réponse test.",
            "Traitement terminé avec succès !",
            "Tâche terminée ! Que puis-je faire d'autre ?"
        ]
        
        for i, phrase in enumerate(conversation, 1):
            print(f"🗣️  Étape {i}: {phrase}")
            
            # Méthode robuste
            engine.stop()
            time.sleep(0.1)
            engine.say(phrase)
            engine.runAndWait()
            time.sleep(0.3)
            
            # Vérifier si l'utilisateur entend
            if i == 3:  # Après 3 phrases
                response = input("Entendez-vous les phrases ? (o/n): ")
                if response.lower() not in ['o', 'oui']:
                    print("❌ Problème détecté à l'étape 3")
                    return False
        
        print("✅ Simulation conversation réussie")
        return True
        
    except Exception as e:
        print(f"❌ Simulation conversation échouée: {e}")
        return False

def diagnostic_moteur():
    """Diagnostic complet du moteur TTS"""
    print("🔍 Diagnostic moteur TTS...")
    
    try:
        engine = pyttsx3.init()
        
        # Informations sur le moteur
        print(f"Moteur: {type(engine)}")
        
        # Voix disponibles
        voices = engine.getProperty('voices')
        print(f"Nombre de voix: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices):
                if voice:
                    print(f"  {i}: {voice.name}")
        
        # Propriétés actuelles
        rate = engine.getProperty('rate')
        volume = engine.getProperty('volume')
        print(f"Vitesse: {rate}")
        print(f"Volume: {volume}")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic échoué: {e}")
        return False

def main():
    print("🎯 Diagnostic Audio Assistant Vocal")
    print("=" * 50)
    
    # Tests progressifs
    tests = [
        ("Diagnostic moteur", diagnostic_moteur),
        ("Test simple", test_tts_simple),
        ("Test multiple", test_tts_multiple),
        ("Test conversation", test_tts_conversation)
    ]
    
    resultats = {}
    
    for nom, test_func in tests:
        print(f"\n{'='*20} {nom} {'='*20}")
        resultats[nom] = test_func()
        time.sleep(1)
    
    # Résumé
    print(f"\n📊 Résumé des tests:")
    for nom, resultat in resultats.items():
        status = "✅ RÉUSSI" if resultat else "❌ ÉCHOUÉ"
        print(f"  {nom}: {status}")
    
    # Recommandations
    print(f"\n💡 Recommandations:")
    if not resultats.get("Test simple", False):
        print("- Problème TTS de base - Vérifiez l'installation de pyttsx3")
    elif not resultats.get("Test multiple", False):
        print("- Problème TTS multiple - Ajoutez des délais entre les phrases")
    elif not resultats.get("Test conversation", False):
        print("- Problème TTS conversation - Réinitialisez le moteur périodiquement")
    else:
        print("- Tous les tests réussis - Le problème peut venir d'ailleurs")

if __name__ == "__main__":
    main()
