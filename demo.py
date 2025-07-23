"""
Démonstration de l'Assistant Vocal PC
====================================

Ce script montre toutes les fonctionnalités de l'assistant vocal.
"""

import time
from assistant_test import AssistantVocalTest

def demo_conversation():
    """Démonstration d'une conversation typique avec l'assistant"""
    
    print("🎬 DÉMONSTRATION DE L'ASSISTANT VOCAL")
    print("=" * 50)
    
    # Initialiser l'assistant
    assistant = AssistantVocalTest()
    
    # Questions de démonstration
    demo_questions = [
        "Salut ! Comment ça va ?",
        "Peux-tu m'expliquer ce qu'est l'intelligence artificielle ?",
        "Écris-moi une fonction Python pour calculer le PGCD de deux nombres",
        "Quels sont les avantages des modèles LLM locaux ?",
        "Donne-moi 3 conseils pour bien programmer en Python",
        "Explique-moi la différence entre une liste et un tuple en Python",
        "Comment optimiser les performances d'un script Python ?",
        "Résume les principes de la programmation orientée objet"
    ]
    
    print(f"\n🎯 Démonstration avec {len(demo_questions)} questions types")
    print("⏳ Chaque question sera envoyée automatiquement...")
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'='*60}")
        print(f"📝 Question {i}/{len(demo_questions)}: {question}")
        print(f"{'='*60}")
        
        # Pause pour lire la question
        time.sleep(2)
        
        # Envoyer la question à l'assistant
        response = assistant.query_mistral(question)
        
        if response:
            print(f"\n🤖 Réponse de Mistral:")
            print(f"📄 {response}")
        else:
            print("❌ Erreur lors de la génération de la réponse")
        
        # Pause entre les questions
        print(f"\n⏳ Pause avant la prochaine question...")
        time.sleep(3)
    
    print(f"\n🎉 Démonstration terminée !")
    print("="*50)
    
    # Statistiques finales
    print(f"\n📊 Résumé de la démonstration:")
    print(f"✅ {len(demo_questions)} questions traitées")
    print(f"🤖 Modèle utilisé: {assistant.model_name}")
    print(f"🌐 Serveur: {assistant.ollama_url}")
    
    return True

def demo_interactive():
    """Mode démo interactif"""
    
    print("\n🎮 MODE DÉMONSTRATION INTERACTIF")
    print("=" * 40)
    print("💡 Posez vos propres questions à l'assistant")
    print("💡 Tapez 'demo auto' pour la démo automatique")
    print("💡 Tapez 'quit' pour quitter")
    
    assistant = AssistantVocalTest()
    
    while True:
        try:
            question = input("\n🎤 Votre question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'stop']:
                break
            elif question.lower() == 'demo auto':
                demo_conversation()
                continue
            elif not question:
                continue
            
            response = assistant.query_mistral(question)
            
            if response:
                print(f"\n🤖 Assistant: {response}")
            else:
                print("❌ Erreur lors du traitement")
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 Fin de la démonstration interactive")

def main():
    """Fonction principale de démonstration"""
    
    print("🚀 ASSISTANT VOCAL PC - DÉMONSTRATION")
    print("="*50)
    
    print("\nModes de démonstration disponibles:")
    print("1. Démonstration automatique (8 questions prédéfinies)")
    print("2. Démonstration interactive (posez vos questions)")
    print("3. Les deux modes")
    
    try:
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            demo_conversation()
        elif choice == "2":
            demo_interactive()
        elif choice == "3":
            demo_conversation()
            input("\nAppuyez sur Entrée pour passer au mode interactif...")
            demo_interactive()
        else:
            print("Choix invalide. Lancement du mode automatique par défaut.")
            demo_conversation()
            
    except KeyboardInterrupt:
        print("\n\n👋 Démonstration interrompue")
    except Exception as e:
        print(f"\n❌ Erreur durant la démonstration: {e}")
    
    print("\n🎬 Merci d'avoir testé l'Assistant Vocal PC !")

if __name__ == "__main__":
    main()
