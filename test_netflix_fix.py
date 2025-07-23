#!/usr/bin/env python3
"""
🧪 Test de la recherche Netflix améliorée
"""

from assistant_vocal import AssistantVocal

def test_netflix_search():
    """Test spécifique pour Netflix"""
    print("🧪 TEST DE LA RECHERCHE NETFLIX AMÉLIORÉE")
    print("=" * 50)
    
    # Initialiser l'assistant
    assistant = AssistantVocal()
    
    # Tests de recherche Netflix
    test_queries = [
        "netflix",
        "ouvre netflix", 
        "lance netflix",
        "démarre netflix",
        "Netflix",
        "NETFLIX"
    ]
    
    print(f"📱 {len(assistant.applications)} applications chargées")
    print(f"🎯 {len(assistant.app_commands_map)} commandes vocales mappées")
    
    for query in test_queries:
        print(f"\n🔍 Test: '{query}'")
        app_key, app_data = assistant.find_application(query)
        
        if app_key:
            print(f"✅ TROUVÉ: {app_data['nom']}")
            print(f"   Clé: {app_key}")
            print(f"   Chemin: {app_data['chemin']}")
        else:
            print(f"❌ NON TROUVÉ")
    
    # Test d'ouverture réelle
    print(f"\n🚀 TEST D'OUVERTURE NETFLIX:")
    print("-" * 30)
    
    success, message = assistant.action_ouvrir_application({"application": "netflix"})
    print(f"Résultat: {'✅' if success else '❌'} {message}")

if __name__ == "__main__":
    test_netflix_search()
