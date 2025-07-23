"""
Test Coqui TTS - Voix Naturelles
================================
Test des voix disponibles avec Coqui TTS
"""

from TTS.api import TTS
import time
import pygame
import os

def list_available_models():
    """Liste les modèles TTS disponibles"""
    print("🎯 Modèles TTS disponibles:")
    
    # Modèles français recommandés
    french_models = [
        "tts_models/fr/mai/tacotron2-DDC",
        "tts_models/fr/css10/vits",
        "tts_models/multilingual/multi-dataset/xtts_v2"
    ]
    
    # Modèles anglais de haute qualité
    english_models = [
        "tts_models/en/ljspeech/tacotron2-DDC",
        "tts_models/en/ljspeech/vits",
        "tts_models/en/ljspeech/fast_pitch",
        "tts_models/en/jenny/jenny"
    ]
    
    print("\n🇫🇷 Modèles français:")
    for model in french_models:
        print(f"  - {model}")
    
    print("\n🇺🇸 Modèles anglais de qualité:")
    for model in english_models:
        print(f"  - {model}")
    
    return french_models, english_models

def test_tts_model(model_name, text, output_file):
    """Test un modèle TTS spécifique"""
    try:
        print(f"\n🧪 Test du modèle: {model_name}")
        print(f"📝 Texte: {text}")
        
        start_time = time.time()
        
        # Initialiser le modèle TTS
        tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
        
        init_time = time.time() - start_time
        print(f"⏱️ Initialisation: {init_time:.2f}s")
        
        # Générer l'audio
        start_synth = time.time()
        tts.tts_to_file(text=text, file_path=output_file)
        synth_time = time.time() - start_synth
        
        print(f"⏱️ Synthèse: {synth_time:.2f}s")
        print(f"✅ Audio généré: {output_file}")
        
        # Lire l'audio généré
        play_audio(output_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur avec {model_name}: {e}")
        return False

def play_audio(file_path):
    """Lit un fichier audio avec pygame"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        print("🔊 Lecture audio... (Appuyez sur Entrée pour continuer)")
        input()
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"❌ Erreur lecture audio: {e}")

def test_french_voices():
    """Test des voix françaises"""
    print("🇫🇷 Test des voix françaises")
    print("=" * 50)
    
    text_fr = "Bonjour ! Je suis votre assistant vocal avec une voix naturelle française."
    
    french_models = [
        "tts_models/fr/mai/tacotron2-DDC",
        "tts_models/fr/css10/vits"
    ]
    
    for i, model in enumerate(french_models):
        output_file = f"test_french_{i+1}.wav"
        test_tts_model(model, text_fr, output_file)
        
        # Demander avis utilisateur
        feedback = input(f"Comment trouvez-vous cette voix ? (1-5, 5=excellent): ")
        print(f"📊 Note: {feedback}/5")

def test_english_voices():
    """Test des voix anglaises pour comparaison"""
    print("\n🇺🇸 Test des voix anglaises (pour comparaison)")
    print("=" * 50)
    
    text_en = "Hello! I am your voice assistant with a natural English voice."
    
    english_models = [
        "tts_models/en/ljspeech/vits",
        "tts_models/en/jenny/jenny"
    ]
    
    for i, model in enumerate(english_models):
        output_file = f"test_english_{i+1}.wav"
        test_tts_model(model, text_en, output_file)
        
        feedback = input(f"Comment trouvez-vous cette voix ? (1-5, 5=excellent): ")
        print(f"📊 Note: {feedback}/5")

def test_multilingual():
    """Test du modèle multilingue XTTS v2"""
    print("\n🌍 Test du modèle multilingue XTTS v2")
    print("=" * 50)
    
    try:
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        
        texts = {
            "français": "Bonjour ! Cette voix multilingue peut parler français naturellement.",
            "english": "Hello! This multilingual voice can speak English naturally too."
        }
        
        for lang, text in texts.items():
            output_file = f"test_multilingual_{lang}.wav"
            print(f"\n🗣️ Test en {lang}:")
            test_tts_model(model_name, text, output_file)
            
            feedback = input(f"Note pour {lang} (1-5): ")
            print(f"📊 Note: {feedback}/5")
    
    except Exception as e:
        print(f"❌ Modèle multilingue non disponible: {e}")

def cleanup_files():
    """Nettoie les fichiers de test"""
    test_files = [
        "test_french_1.wav", "test_french_2.wav",
        "test_english_1.wav", "test_english_2.wav",
        "test_multilingual_français.wav", "test_multilingual_english.wav"
    ]
    
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"🗑️ Supprimé: {file}")
        except:
            pass

def main():
    print("🎤 Test Coqui TTS - Voix Naturelles")
    print("=" * 50)
    
    # Installer pygame si nécessaire
    try:
        import pygame
    except ImportError:
        print("📦 Installation de pygame pour la lecture audio...")
        os.system("pip install pygame")
        import pygame
    
    # Lister les modèles
    french_models, english_models = list_available_models()
    
    print("\n🚀 Début des tests...")
    print("Attention: Le premier téléchargement de modèle peut prendre du temps")
    
    # Tests
    try:
        # Test voix françaises
        test_french_voices()
        
        # Test voix anglaises pour comparaison
        choice = input("\nTester aussi les voix anglaises ? (o/n): ").lower()
        if choice in ['o', 'oui', 'y', 'yes']:
            test_english_voices()
        
        # Test multilingue
        choice = input("\nTester le modèle multilingue ? (o/n): ").lower()
        if choice in ['o', 'oui', 'y', 'yes']:
            test_multilingual()
    
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus")
    
    # Nettoyage
    choice = input("\nSupprimer les fichiers de test ? (o/n): ").lower()
    if choice in ['o', 'oui', 'y', 'yes']:
        cleanup_files()
    
    print("\n🎯 Tests terminés !")
    print("Recommandation: Choisissez le modèle avec la meilleure note pour votre assistant")

if __name__ == "__main__":
    main()
