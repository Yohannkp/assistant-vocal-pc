"""
Test rapide de l'ouverture de Netflix avec la nouvelle logique UWP
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_netflix_fixed():
    print("🧪 TEST NETFLIX AVEC CORRECTION UWP")
    print("=" * 50)
    
    # Créer l'assistant (sans TTS pour éviter les blocages)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour les tests
    def mock_speak(text):
        print(f"🔇 [TTS désactivé] {text}")
    
    assistant.speak = mock_speak
    
    # Test d'ouverture de Netflix
    print("🔍 Test d'ouverture de Netflix...")
    
    params = {"application": "netflix"}
    success, message = assistant.action_ouvrir_application(params)
    
    print(f"\n📊 RÉSULTAT:")
    print(f"   Succès: {'✅' if success else '❌'}")
    print(f"   Message: {message}")
    
    if success:
        print("\n🎉 SUCCÈS ! Netflix devrait maintenant s'ouvrir")
    else:
        print("\n❌ Échec. Vérifiez les détails ci-dessus")

if __name__ == "__main__":
    test_netflix_fixed()
