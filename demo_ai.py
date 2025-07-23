"""
Démonstration des fonctionnalités IA de l'assistant vocal
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def demo_ai_assistant():
    print("🚀 DÉMONSTRATION ASSISTANT VOCAL IA AMÉLIORÉ")
    print("=" * 60)
    print("🤖 Nouvelles fonctionnalités IA intégrées:")
    print("   • Recherche intelligente d'applications")
    print("   • Suggestions alternatives automatiques")
    print("   • Analyse de commandes ambiguës")
    print("   • Aide contextuelle dynamique")
    print("-" * 60)
    
    # Créer l'assistant (sans TTS pour la démo)
    assistant = AssistantVocal()
    
    # Désactiver TTS pour la démo
    def mock_speak(text):
        print(f"🔊 [Assistant]: {text}")
    
    assistant.speak = mock_speak
    
    # Démonstration 1: Recherche intelligente
    print("\n🎯 DÉMONSTRATION 1: Recherche intelligente d'applications")
    print("-" * 50)
    
    smart_searches = [
        ("ouvre Netflix", "Recherche directe classique"),
        ("lance le navigateur", "IA trouve Chrome/Firefox via synonyme"),
        ("je veux écrire un document", "IA comprend et trouve Word"),
        ("démarre une app pour les calculs", "IA trouve la calculatrice")
    ]
    
    for query, description in smart_searches:
        print(f"\n📝 Test: '{query}'")
        print(f"   💡 Objectif: {description}")
        
        app_key, app_data = assistant.find_application(query)
        
        if app_key:
            print(f"   ✅ Résultat: {app_data['nom']}")
        else:
            print(f"   ❌ Non trouvé")
    
    # Démonstration 2: Suggestions alternatives
    print("\n\n🎯 DÉMONSTRATION 2: Suggestions IA pour applications introuvables")
    print("-" * 50)
    
    unknown_apps = ["Spotify", "Photoshop", "Steam"]
    
    for app in unknown_apps:
        print(f"\n📝 Application demandée: '{app}'")
        suggestions = assistant.ai_suggest_alternatives(app)
        print(f"   🤖 Suggestions IA: {suggestions}")
    
    # Démonstration 3: Analyse de commandes
    print("\n\n🎯 DÉMONSTRATION 3: Analyse IA de commandes ambiguës")
    print("-" * 50)
    
    ambiguous_commands = [
        "je veux regarder un film",
        "besoin de faire des calculs", 
        "ouvrir quelque chose pour écrire",
        "écouter de la musique"
    ]
    
    for cmd in ambiguous_commands:
        print(f"\n📝 Commande: '{cmd}'")
        analysis = assistant.ai_analyze_command(cmd)
        print(f"   🤖 Analyse IA: {analysis}")
        
        if "ACTION" in analysis:
            print(f"   ✅ L'IA identifie une action à exécuter")
        else:
            print(f"   ❓ L'IA identifie une question")
    
    # Démonstration 4: Aide contextuelle
    print("\n\n🎯 DÉMONSTRATION 4: Aide contextuelle intelligente")
    print("-" * 50)
    
    help_scenarios = [
        "aide",
        "comment ça marche",
        "que peux-tu faire",
        "je ne sais pas quoi dire"
    ]
    
    for scenario in help_scenarios:
        print(f"\n📝 Demande: '{scenario}'")
        help_text = assistant.ai_help_context(scenario)
        print(f"   🤖 Aide IA: {help_text}")
    
    print("\n" + "=" * 60)
    print("🎉 DÉMONSTRATION TERMINÉE")
    print("💡 L'assistant vocal est maintenant équipé d'IA pour:")
    print("   • Mieux comprendre vos demandes")
    print("   • Suggérer des alternatives intelligentes") 
    print("   • Fournir de l'aide contextuelle")
    print("   • Analyser des commandes ambiguës")
    print("\n🚀 Testez-le en disant: 'Assistant, lance le navigateur' ou 'Assistant, aide'")

if __name__ == "__main__":
    demo_ai_assistant()
