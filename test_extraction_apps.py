"""
Test de l'extraction améliorée de noms d'applications
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_application_extraction():
    print("🧪 TEST D'EXTRACTION DE NOMS D'APPLICATIONS")
    print("=" * 60)
    
    # Créer l'assistant (sans TTS)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour les tests
    def mock_speak(text):
        print(f"🔇 [TTS désactivé] {text}")
    
    assistant.speak = mock_speak
    
    # Tests de différentes phrases
    test_phrases = [
        "ouvre l'application Netflix",
        "lance Netflix",
        "ouvre Netflix",
        "démarre l'application Chrome",
        "exécute Chrome",
        "ouvre Word",
        "lance Microsoft Word",
        "ouvre l'application Spotify",
        "démarre Skype",
        "lance le bloc-notes"
    ]
    
    print("🔍 Tests d'extraction de noms d'applications:")
    print("-" * 60)
    
    for phrase in test_phrases:
        print(f"\n📝 Phrase: '{phrase}'")
        app_key, app_data = assistant.find_application(phrase)
        
        if app_key:
            print(f"   ✅ Trouvé: {app_data['nom']} (clé: {app_key})")
        else:
            print(f"   ❌ Aucune application trouvée")
    
    print("\n" + "=" * 60)
    print("🧪 Test terminé")

if __name__ == "__main__":
    test_application_extraction()
