# 🤖 Assistant Vocal PC avec Ollama Mistral

Un assistant vocal intelligent qui utilise votre modèle Mistral local via l'API Ollama. L'assistant peut fonctionner en mode vocal (reconnaissance vocale + synthèse) ou en mode texte selon les composants disponibles.

## 🚀 Fonctionnalités

- ✅ **Communication avec Mistral** via API Ollama locale
- 🎤 **Reconnaissance vocale** (Google Speech Recognition)
- 🔊 **Synthèse vocale** (Text-to-Speech)
- 💬 **Mode hybride** : vocal + texte selon disponibilité
- 🎯 **Commandes intelligentes** : contrôle vocal et textuel
- 🔧 **Tests automatiques** de tous les composants
- 🌐 **Interface simple** et intuitive

## 📋 Prérequis

### Système
- **Windows 10/11** (testé)
- **Python 3.7+**
- **Ollama** installé et en fonctionnement
- **Modèle Mistral** disponible dans Ollama

### Vérification Ollama
```powershell
# Vérifier qu'Ollama fonctionne
ollama list

# Démarrer le serveur si nécessaire
ollama serve

# Tester l'accès
curl http://127.0.0.1:11434
```

## 🔧 Installation

### 1. Installation automatique
```powershell
# Exécuter le script d'installation
.\installer.bat
```

### 2. Installation manuelle
```powershell
# Installer les dépendances Python
pip install -r requirements.txt

# Ou installation individuelle
pip install requests speech_recognition pyttsx3 pyaudio pygame
```

### 3. Dépendances audio (optionnelles)
Pour la reconnaissance vocale, vous pourriez avoir besoin d'installer :
- **PyAudio** : `pip install pyaudio`
- **Microsoft Visual C++ Build Tools** (si erreur PyAudio)

## 🎮 Utilisation

### Modes disponibles

#### 1. Assistant Test (Texte uniquement)
```powershell
python assistant_test.py
```
- Mode texte pur
- Idéal pour tester la connexion Mistral
- Pas de composants audio requis

#### 2. Assistant Hybride (Recommandé)
```powershell
python assistant_hybride.py
```
- Détection automatique des composants audio
- Choix du mode au démarrage :
  - **Mode interactif** : clavier + vocal
  - **Mode vocal pur** : mot de réveil "Assistant"
  - **Mode texte** : clavier uniquement

#### 3. Assistant Vocal Complet
```powershell
python assistant_vocal.py
```
- Nécessite tous les composants audio
- Mode vocal avancé avec mot de réveil

### Commandes vocales/textuelles

| Commande | Action |
|----------|--------|
| `"Assistant"` | Mot de réveil (mode vocal) |
| `"aide"` / `"help"` | Affiche l'aide |
| `"test"` | Lance les tests de connexion |
| `"mode texte"` | Force le mode texte |
| `"mode vocal"` | Active le mode vocal |
| `"quit"` / `"au revoir"` | Quitte l'assistant |

## 📁 Structure du Projet

```
Assistant local PC/
├── assistant_vocal.py      # Version complète avec audio
├── assistant_hybride.py    # Version hybride (recommandée)
├── assistant_test.py       # Version test (texte uniquement)
├── test_mistral_api.ps1    # Scripts de test PowerShell
├── test_mistral_simple.ps1 # Test API simple
├── requirements.txt        # Dépendances Python
├── installer.bat          # Script d'installation Windows
└── README.md              # Ce fichier
```

## 🔧 Configuration

### Paramètres modifiables
```python
# Dans les fichiers .py
ollama_url = "http://127.0.0.1:11434"    # URL du serveur Ollama
model_name = "mistral:instruct"          # Nom du modèle à utiliser
```

### Modèles compatibles
- `mistral:instruct` ✅ (testé)
- `mistral:latest` ✅
- `deepseek-coder:latest` ✅ (testé)
- Autres modèles Ollama 🔄 (à tester)

## 🧪 Tests et Dépannage

### Tests automatiques
```powershell
# Test complet de l'assistant
python assistant_hybride.py
# Puis taper "test"

# Test API uniquement
python assistant_test.py
# Puis taper "test"
```

### Problèmes courants

#### 1. Erreur "Ollama inaccessible"
```powershell
# Vérifier le service Ollama
ollama serve

# Tester manuellement
curl http://127.0.0.1:11434
```

#### 2. Erreur "Modèle Mistral non trouvé"
```powershell
# Installer Mistral
ollama pull mistral:instruct

# Vérifier les modèles
ollama list
```

#### 3. Erreur composants audio
```powershell
# Réinstaller les dépendances audio
pip uninstall pyaudio speech_recognition pyttsx3
pip install pyaudio speech_recognition pyttsx3

# Ou utiliser le mode texte uniquement
python assistant_test.py
```

#### 4. Erreur de reconnaissance vocale
- Vérifier le microphone dans Windows
- Autoriser l'accès au microphone pour Python
- Utiliser le mode texte : `"mode texte"`

## 📊 Performances

### Temps de réponse typiques
- **Première requête** : 5-15 secondes (chargement modèle)
- **Requêtes suivantes** : 0.3-3 secondes
- **Reconnaissance vocale** : 1-2 secondes
- **Synthèse vocale** : instantanée

### Consommation ressources
- **RAM** : 2-8 GB (selon le modèle)
- **CPU** : Variable selon la longueur des réponses
- **Disque** : 776 MB - 4.1 GB (selon le modèle)

## 🔒 Confidentialité

- ✅ **100% local** : aucune donnée envoyée sur internet
- ✅ **Pas de tracking** : aucune télémétrie
- ✅ **Contrôle total** : vos données restent sur votre PC
- ✅ **Open source** : code entièrement visible

## 🎯 Exemples d'utilisation

### Questions générales
- *"Explique-moi l'intelligence artificielle"*
- *"Quelle heure est-il ?"*
- *"Comment ça marche l'informatique quantique ?"*

### Programmation
- *"Écris une fonction Python pour trier une liste"*
- *"Comment optimiser ce code ?"*
- *"Explique les design patterns"*

### Assistance quotidienne
- *"Aide-moi à rédiger un email"*
- *"Donne-moi des idées de recettes"*
- *"Résume ce texte"*

## 🚧 Développement

### Ajouter des fonctionnalités
```python
# Dans process_command()
if "nouvelle_commande" in command_lower:
    # Votre code ici
    self.speak("Nouvelle fonctionnalité activée")
```

### Changer de modèle
```python
# Modifier la variable
self.model_name = "deepseek-coder:latest"  # ou autre modèle
```

### Personnaliser la voix
```python
# Dans setup_tts()
self.tts_engine.setProperty('rate', 150)     # Vitesse
self.tts_engine.setProperty('volume', 1.0)   # Volume
```

## 📞 Support

### Logs et débogage
L'assistant affiche des informations détaillées :
- 🤖 Actions de l'assistant
- ⏱️ Temps de réponse
- 🔢 Tokens générés
- ❌ Erreurs avec détails

### Problèmes fréquents
1. **Pas de son** → Vérifier le volume système
2. **Microphone non détecté** → Vérifier les permissions
3. **Réponses lentes** → Modèle trop volumineux
4. **Erreurs réseau** → Vérifier Ollama

---

## 🎉 Félicitations !

Vous avez maintenant un assistant vocal intelligent 100% local ! 🎊

**Prochaines étapes possibles :**
- Intégrer d'autres modèles Ollama
- Ajouter des commandes personnalisées
- Créer une interface graphique
- Connecter des APIs externes locales

Profitez bien de votre assistant personnel ! 🤖✨
