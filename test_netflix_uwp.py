#!/usr/bin/env python3
"""
🧪 Test spécifique de l'ouverture Netflix UWP
"""

from assistant_vocal import AssistantVocal

def test_netflix_uwp():
    """Test de l'ouverture Netflix avec gestion UWP"""
    print("🧪 TEST D'OUVERTURE NETFLIX UWP")
    print("=" * 50)
    
    # Initialiser l'assistant (mode silencieux)
    assistant = AssistantVocal()
    
    # Chercher Netflix
    print("🔍 Recherche de Netflix...")
    app_key, app_data = assistant.find_application("netflix")
    
    if app_key:
        print(f"✅ Netflix trouvé:")
        print(f"   Nom: {app_data['nom']}")
        print(f"   Chemin: {app_data['chemin']}")
        print(f"   Processus: {app_data['processus']}")
        
        # Test d'ouverture
        print(f"\n🚀 Test d'ouverture...")
        success, message = assistant.action_ouvrir_application({"application": "netflix"})
        
        print(f"\n📊 RÉSULTAT:")
        print(f"   Succès: {'✅' if success else '❌'}")
        print(f"   Message: {message}")
        
        if success:
            print(f"\n🎉 NETFLIX DEVRAIT S'OUVRIR MAINTENANT!")
            print(f"   Si ce n'est pas le cas, vérifiez que Netflix est installé")
            print(f"   depuis le Microsoft Store.")
        else:
            print(f"\n💡 SOLUTIONS ALTERNATIVES:")
            print(f"   1. Ouvrez le Microsoft Store")
            print(f"   2. Recherchez 'Netflix'")
            print(f"   3. Installez ou mettez à jour l'application")
            
    else:
        print("❌ Netflix non trouvé dans les applications scannées")

if __name__ == "__main__":
    test_netflix_uwp()
