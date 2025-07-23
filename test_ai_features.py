"""
Test des nouvelles fonctionnalités IA de l'assistant vocal
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_ai_features():
    print("🤖 TEST DES FONCTIONNALITÉS IA AMÉLIORÉES")
    print("=" * 60)
    
    # Créer l'assistant (sans TTS pour éviter les blocages)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour les tests
    def mock_speak(text):
        print(f"🔇 [Assistant]: {text}")
    
    assistant.speak = mock_speak
    
    print("🧪 Tests de recherche IA intelligente:")
    print("-" * 40)
    
    # Test 1: Recherche d'application avec synonyme
    test_queries = [
        "ouvre le navigateur",  # Devrait trouver Chrome/Firefox
        "lance un éditeur de texte",  # Devrait trouver Word/Notepad
        "démarre l'app de musique",  # Pourrait trouver un lecteur audio
        "ouvre une application inexistante"  # Test de suggestions
    ]
    
    for query in test_queries:
        print(f"\n📝 Test: '{query}'")
        app_key, app_data = assistant.find_application(query)
        
        if app_key:
            print(f"   ✅ Trouvé: {app_data['nom']}")
        else:
            print(f"   ❌ Non trouvé - test suggestions...")
            # Test des suggestions IA
            suggestions = assistant.ai_suggest_alternatives("application inexistante")
            print(f"   🤖 Suggestions IA: {suggestions}")
    
    print("\n" + "-" * 40)
    print("🧪 Test d'analyse de commande par l'IA:")
    
    # Test 2: Analyse de commandes ambiguës
    ambiguous_commands = [
        "je veux regarder un film",  # Pourrait être Netflix
        "besoin de faire des calculs",  # Calculatrice
        "ouvrir quelque chose pour écrire"  # Word/Notepad
    ]
    
    for cmd in ambiguous_commands:
        print(f"\n📝 Commande ambiguë: '{cmd}'")
        analysis = assistant.ai_analyze_command(cmd)
        print(f"   🤖 Analyse IA: {analysis}")
    
    print("\n" + "-" * 40)
    print("🧪 Test d'aide contextuelle:")
    
    # Test 3: Aide contextuelle
    help_queries = [
        "aide",
        "comment ouvrir une application",
        "que puis-je faire"
    ]
    
    for query in help_queries:
        print(f"\n📝 Demande d'aide: '{query}'")
        help_response = assistant.ai_help_context(query)
        print(f"   🤖 Aide IA: {help_response}")
    
    print("\n" + "=" * 60)
    print("🎯 Tests terminés !")

if __name__ == "__main__":
    test_ai_features()
