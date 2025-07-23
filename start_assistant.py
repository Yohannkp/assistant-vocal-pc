#!/usr/bin/env python3
"""
🚀 Lanceur de l'Assistant Vocal PC
Démarre l'assistant avec toutes les fonctionnalités :
- 411 applications scannées automatiquement
- Reconnaissance vocale française
- IA Mistral intégrée
- Actions intelligentes
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assistant_vocal import main

if __name__ == "__main__":
    print("🎤 Démarrage de l'Assistant Vocal PC")
    print("🤖 Avec 411 applications et IA Mistral")
    print("=" * 50)
    main()
