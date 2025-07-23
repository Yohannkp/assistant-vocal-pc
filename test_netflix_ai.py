"""
Test Netflix avec les nouvelles fonctionnalités IA
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_netflix_with_ai():
    print("🎬 TEST NETFLIX AVEC AMÉLIORATIONS IA")
    print("=" * 50)
    
    # Créer l'assistant (sans TTS pour éviter les blocages)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour les tests
    def mock_speak(text):
        print(f"🔇 [Assistant]: {text}")
    
    assistant.speak = mock_speak
    
    # Test de différentes formulations pour Netflix avec IA
    netflix_phrases = [
        "ouvre Netflix",
        "lance l'application de films",  # Test IA : devrait comprendre Netflix
        "je veux regarder un film",      # Test IA : devrait comprendre Netflix
        "démarre l'app de streaming",    # Test IA : devrait comprendre Netflix
        "ouvre une app inexistante"      # Test suggestions IA
    ]
    
    print("🧪 Tests Netflix avec IA:")
    print("-" * 30)
    
    for phrase in netflix_phrases:
        print(f"\n📝 Phrase: '{phrase}'")
        
        # Simuler le processus complet comme dans l'assistant
        success, message = assistant.action_ouvrir_application({"application": phrase})
        
        print(f"   📊 Résultat: {'✅' if success else '❌'}")
        print(f"   💬 Message: {message}")
        
        if "Netflix" in message:
            print("   🎉 Netflix détecté avec succès !")

if __name__ == "__main__":
    test_netflix_with_ai()
