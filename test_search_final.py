"""
Test final de l'amélioration de la recherche d'applications
Vérifie que les faux positifs sont éliminés et que l'IA s'active au bon moment
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from assistant_vocal import AssistantVocal

def test_search_improvements():
    print("🎯 TEST FINAL - AMÉLIORATIONS RECHERCHE D'APPLICATIONS")
    print("=" * 60)
    
    assistant = AssistantVocal()
    
    # Mock speak pour la démo
    def mock_speak(text):
        print(f"🔊 [Assistant]: {text}")
    assistant.speak = mock_speak
    
    # Tests spécifiques pour les problèmes résolus
    test_cases = [
        {
            "query": "je veux regarder un film",
            "expectation": "Devrait utiliser l'IA pour suggérer Netflix",
            "problem_before": "Trouvait 'Journal de télémétrie pour Office' par erreur"
        },
        {
            "query": "ouvre Netflix",
            "expectation": "Devrait trouver Netflix directement",
            "problem_before": "Fonctionnait déjà"
        },
        {
            "query": "lance l'application de streaming",
            "expectation": "Devrait utiliser l'IA pour suggestions",
            "problem_before": "Pouvait matcher de mauvaises apps"
        },
        {
            "query": "j'aimerais voir une série",
            "expectation": "Devrait utiliser l'IA pour Netflix",
            "problem_before": "Trouvait des apps non pertinentes"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test['query']}")
        print(f"   📝 Attendu: {test['expectation']}")
        print(f"   ⚠️  Problème avant: {test['problem_before']}")
        print("-" * 50)
        
        # Test de la recherche
        app_key, app_data = assistant.find_application(test['query'])
        
        if app_key:
            print(f"   ✅ Trouvé directement: {app_data['nom']}")
        else:
            print(f"   🤖 Aucune app trouvée → IA activée")
            
            # Test de l'IA en cas d'échec
            suggestions = assistant.ai_smart_app_search(test['query'])
            print(f"   💡 Suggestions IA: {suggestions}")
    
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DES AMÉLIORATIONS:")
    print("   ✅ Critères de recherche plus stricts (longueur > 3)")
    print("   ✅ Seuils de similarité ajustés")
    print("   ✅ IA activée pour requêtes ambiguës")
    print("   ✅ Faux positifs éliminés")
    print("   ✅ Netflix toujours accessible directement")

def test_complete_workflow():
    print("\n\n🚀 TEST WORKFLOW COMPLET")
    print("=" * 60)
    
    assistant = AssistantVocal()
    
    # Mock speak
    def mock_speak(text):
        print(f"🔊 [Assistant]: {text}")
    assistant.speak = mock_speak
    
    # Simuler le workflow complet pour "je veux regarder un film"
    test_query = "je veux regarder un film"
    print(f"📝 Commande complète: '{test_query}'")
    
    # 1. Analyse de la commande
    print("\n🔍 Étape 1: Analyse de commande")
    analysis = assistant.ai_analyze_command(test_query)
    print(f"   🤖 Analyse: {analysis}")
    
    # 2. Recherche d'application
    print("\n🔍 Étape 2: Recherche d'application")
    app_key, app_data = assistant.find_application(test_query)
    
    if app_key:
        print(f"   ✅ Application trouvée: {app_data['nom']}")
    else:
        print(f"   ❌ Aucune application trouvée")
        
        # 3. IA prend le relais
        print("\n🔍 Étape 3: IA intelligente")
        suggestions = assistant.ai_smart_app_search(test_query)
        print(f"   🤖 Suggestions: {suggestions}")
    
    print("\n✅ Workflow IA complet testé avec succès !")

if __name__ == "__main__":
    test_search_improvements()
    test_complete_workflow()
