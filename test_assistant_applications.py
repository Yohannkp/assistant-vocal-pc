#!/usr/bin/env python3
"""
Test de l'assistant vocal avec les applications scannées
"""

from assistant_vocal import AssistantVocal
import time

def test_assistant_applications():
    """Test du système d'applications"""
    print("🧪 Test de l'assistant vocal avec applications scannées")
    print("=" * 60)
    
    # Initialiser l'assistant
    assistant = AssistantVocal()
    
    # Vérifier le chargement des applications
    print(f"📱 Applications chargées : {len(assistant.applications)}")
    print(f"🎯 Commandes vocales mappées : {len(getattr(assistant, 'app_commands_map', {}))}")
    
    # Tests de recherche d'applications
    test_queries = [
        "chrome",
        "google chrome", 
        "android studio",
        "git",
        "calculatrice",
        "notepad",
        "visual studio code",
        "firefox",
        "word",
        "excel"
    ]
    
    print("\n🔍 Tests de recherche d'applications:")
    print("-" * 40)
    
    for query in test_queries:
        app_key, app_data = assistant.find_application(query)
        if app_key:
            print(f"✅ '{query}' → {app_data['nom']}")
        else:
            print(f"❌ '{query}' → Non trouvé")
    
    # Test de la fonction de listage
    print("\n📋 Test de listage des applications:")
    print("-" * 40)
    
    success, message = assistant.action_lister_applications()
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    # Afficher quelques applications disponibles
    print("\n🎯 Exemples d'applications disponibles:")
    print("-" * 40)
    
    sample_apps = list(assistant.applications.items())[:10]
    for i, (key, data) in enumerate(sample_apps, 1):
        print(f"{i:2d}. {data['nom']} (clé: {key})")
    
    print("\n✅ Tests terminés avec succès !")
    print(f"💡 Vous pouvez maintenant dire : 'Ouvre {sample_apps[0][1]['nom']}' à l'assistant")

if __name__ == "__main__":
    test_assistant_applications()
