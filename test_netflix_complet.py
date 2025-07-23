"""
Test final de Netflix avec la nouvelle logique d'extraction
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_netflix_final():
    print("🎬 TEST FINAL NETFLIX - EXTRACTION + OUVERTURE")
    print("=" * 60)
    
    # Créer l'assistant (sans TTS pour éviter les blocages)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour les tests
    def mock_speak(text):
        print(f"🔇 [TTS désactivé] {text}")
    
    assistant.speak = mock_speak
    
    # Test de différentes formulations pour Netflix
    netflix_phrases = [
        "ouvre l'application Netflix",
        "lance Netflix", 
        "démarre Netflix",
        "ouvre Netflix",
        "exécute Netflix"
    ]
    
    print("🔍 Tests de recherche Netflix:")
    print("-" * 40)
    
    for phrase in netflix_phrases:
        print(f"\n📝 Phrase: '{phrase}'")
        app_key, app_data = assistant.find_application(phrase)
        
        if app_key and "netflix" in app_key.lower():
            print(f"   ✅ Extraction réussie: {app_data['nom']}")
            
            # Tester l'ouverture
            print("   🚀 Test d'ouverture...")
            params = {"application": app_key}
            success, message = assistant.action_ouvrir_application(params)
            
            print(f"   📊 Résultat ouverture: {'✅' if success else '❌'}")
            print(f"   💬 Message: {message}")
            
            if success:
                print("   🎉 SUCCÈS COMPLET !")
                return True
            else:
                print("   ⚠️ Problème d'ouverture")
        else:
            print(f"   ❌ Extraction échouée")
    
    print("\n" + "=" * 60)
    return False

if __name__ == "__main__":
    success = test_netflix_final()
    if success:
        print("🎬 Netflix fonctionne parfaitement maintenant !")
    else:
        print("❌ Il reste des problèmes à corriger")
