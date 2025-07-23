"""
🎤 Assistant Vocal PC - Démarrage Interactif
===========================================
"""

def demarrer_assistant():
    """Démarre l'assistant vocal avec menu interactif"""
    
    print("🚀 ASSISTANT VOCAL PC")
    print("=" * 50)
    print("📱 411 applications scannées automatiquement")
    print("🎯 1049 commandes vocales mappées")
    print("🤖 IA Mistral intégrée")
    print("🗣️ Voix française Hortense")
    print("=" * 50)
    
    print("\n🎛️ Options de démarrage :")
    print("1. 🧪 Tester les composants d'abord")
    print("2. 🚀 Démarrer directement l'assistant")
    print("3. 📋 Voir les applications disponibles")
    print("4. ❓ Aide et exemples de commandes")
    print("5. 🚪 Quitter")
    
    while True:
        try:
            choix = input("\n👉 Votre choix (1-5) : ").strip()
            
            if choix == "1":
                print("\n🧪 Lancement des tests...")
                from assistant_vocal import AssistantVocal
                assistant = AssistantVocal()
                assistant.test_components()
                
                continuer = input("\n🚀 Voulez-vous démarrer l'assistant maintenant ? (o/n) : ")
                if continuer.lower() in ['o', 'oui', 'y', 'yes']:
                    print("\n🎤 Démarrage de l'assistant vocal...")
                    assistant.run()
                break
                
            elif choix == "2":
                print("\n🚀 Démarrage direct de l'assistant...")
                print("💡 Dites 'Assistant' pour m'activer !")
                from assistant_vocal import AssistantVocal
                assistant = AssistantVocal()
                assistant.run()
                break
                
            elif choix == "3":
                print("\n📋 Chargement des applications...")
                from assistant_vocal import AssistantVocal
                assistant = AssistantVocal()
                
                print(f"\n🎯 {len(assistant.applications)} applications disponibles :")
                print("-" * 40)
                
                # Afficher les 20 premières applications
                for i, (key, data) in enumerate(list(assistant.applications.items())[:20], 1):
                    print(f"{i:2d}. {data['nom']}")
                
                if len(assistant.applications) > 20:
                    print(f"... et {len(assistant.applications) - 20} autres applications")
                
                print(f"\n💡 Exemples de commandes :")
                print("• 'Assistant, ouvre Chrome'")
                print("• 'Assistant, lance Android Studio'")
                print("• 'Assistant, démarre Audacity'")
                
            elif choix == "4":
                print("\n❓ AIDE - EXEMPLES DE COMMANDES")
                print("=" * 40)
                print("\n🎤 ACTIVATION :")
                print("Dites 'Assistant' pour activer l'écoute")
                
                print("\n🚀 ACTIONS (ouvrir applications) :")
                print("• 'Assistant, ouvre Chrome'")
                print("• 'Assistant, lance Android Studio'")
                print("• 'Assistant, démarre Audacity'")
                print("• 'Assistant, ouvre Docker Desktop'")
                
                print("\n❓ QUESTIONS (envoyées à Mistral AI) :")
                print("• 'Assistant, comment programmer en Python ?'")
                print("• 'Assistant, explique-moi l'IA'")
                print("• 'Assistant, quelle est la météo ?'")
                
                print("\n⚙️ COMMANDES SYSTÈME :")
                print("• 'Assistant, liste les applications'")
                print("• 'Assistant, test voix'")
                print("• 'Assistant, fini' (quitter conversation)")
                print("• 'Assistant, au revoir' (arrêter assistant)")
                
            elif choix == "5":
                print("\n👋 À bientôt !")
                break
                
            else:
                print("❌ Choix invalide. Veuillez choisir entre 1 et 5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Arrêt demandé. À bientôt !")
            break
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            break

if __name__ == "__main__":
    demarrer_assistant()
