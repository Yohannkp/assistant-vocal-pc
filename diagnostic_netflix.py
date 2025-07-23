#!/usr/bin/env python3
"""
🔍 Diagnostic Netflix - Pourquoi l'application n'est pas trouvée
"""

import json
import os

def diagnostic_netflix():
    """Diagnostic complet de la recherche Netflix"""
    print("🔍 DIAGNOSTIC NETFLIX")
    print("=" * 50)
    
    # Charger les applications scannées
    applications_file = "applications_assistant.json"
    if not os.path.exists(applications_file):
        print("❌ Fichier applications_assistant.json non trouvé")
        return
    
    with open(applications_file, 'r', encoding='utf-8') as f:
        scanned_apps = json.load(f)
    
    print(f"📱 {len(scanned_apps)} applications chargées")
    
    # 1. Chercher Netflix dans les applications
    print("\n🎬 RECHERCHE NETFLIX DANS LES APPLICATIONS:")
    print("-" * 40)
    
    netflix_apps = []
    for app_key, app_data in scanned_apps.items():
        nom = app_data.get('nom', '').lower()
        if 'netflix' in app_key.lower() or 'netflix' in nom:
            netflix_apps.append((app_key, app_data))
    
    if netflix_apps:
        print(f"✅ {len(netflix_apps)} application(s) Netflix trouvée(s):")
        for app_key, app_data in netflix_apps:
            print(f"  🔑 Clé: '{app_key}'")
            print(f"  📋 Nom: '{app_data.get('nom', 'N/A')}'")
            print(f"  📂 Chemin: '{app_data.get('chemin', 'N/A')}'")
            print(f"  🎤 Commandes: {app_data.get('commandes', [])}")
            print("-" * 30)
    else:
        print("❌ Aucune application Netflix trouvée")
        
        # Chercher des applications similaires
        print("\n📺 APPLICATIONS MULTIMÉDIA SIMILAIRES:")
        similar = []
        for app_key, app_data in scanned_apps.items():
            nom = app_data.get('nom', '').lower()
            if any(word in nom for word in ['video', 'media', 'stream', 'play', 'film', 'tv']):
                similar.append((app_key, app_data['nom']))
        
        if similar:
            print(f"Trouvé {len(similar)} applications multimédia:")
            for i, (app_key, nom) in enumerate(similar[:10], 1):
                print(f"  {i}. {nom}")
    
    # 2. Simuler la recherche actuelle
    print(f"\n🔧 SIMULATION DE LA RECHERCHE ACTUELLE:")
    print("-" * 40)
    
    query = "ouvre netflix"
    query_clean = query.lower().strip()
    print(f"Query originale: '{query}'")
    print(f"Query nettoyée: '{query_clean}'")
    
    # Simuler app_commands_map
    app_commands_map = {}
    applications = {}
    
    for app_key, app_data in scanned_apps.items():
        applications[app_key] = app_data
        for command in app_data.get("commandes", []):
            app_commands_map[command.lower()] = app_key
    
    print(f"🎯 {len(app_commands_map)} commandes vocales mappées")
    
    # Test recherche 1: dans les commandes vocales
    print(f"\n1️⃣ RECHERCHE DANS LES COMMANDES VOCALES:")
    found_in_commands = False
    netflix_commands = []
    
    for command, app_key in app_commands_map.items():
        if 'netflix' in command:
            netflix_commands.append((command, app_key))
            if command in query_clean:
                print(f"✅ Trouvé via commande: '{command}' → {app_key}")
                found_in_commands = True
    
    if netflix_commands:
        print(f"📋 Commandes Netflix disponibles:")
        for cmd, key in netflix_commands:
            print(f"  - '{cmd}' → {key}")
    else:
        print("❌ Aucune commande Netflix trouvée")
    
    # Test recherche 2: dans les noms d'applications
    print(f"\n2️⃣ RECHERCHE DANS LES NOMS D'APPLICATIONS:")
    found_in_names = False
    
    for app_key, app_data in applications.items():
        app_key_lower = app_key.lower()
        nom_lower = app_data.get("nom", "").lower()
        
        if 'netflix' in app_key_lower or 'netflix' in nom_lower:
            print(f"📱 Application trouvée: {app_key} → {app_data.get('nom')}")
            if app_key_lower in query_clean or nom_lower in query_clean:
                print(f"✅ Match trouvé: {app_key}")
                found_in_names = True
    
    if not found_in_names:
        print("❌ Aucun match dans les noms d'applications")
    
    # Test recherche 3: recherche partielle
    print(f"\n3️⃣ RECHERCHE PARTIELLE DANS LES MOTS:")
    found_in_words = False
    
    for app_key, app_data in applications.items():
        nom_mots = app_data.get("nom", "").lower().split()
        for mot in nom_mots:
            if len(mot) > 2 and 'netflix' in mot:
                print(f"📝 Mot trouvé: '{mot}' dans {app_data.get('nom')}")
                if mot in query_clean:
                    print(f"✅ Match partiel: {app_key}")
                    found_in_words = True
    
    if not found_in_words:
        print("❌ Aucun match partiel trouvé")
    
    # Résumé du diagnostic
    print(f"\n📊 RÉSUMÉ DU DIAGNOSTIC:")
    print("-" * 40)
    
    if netflix_apps:
        print("✅ Netflix trouvé dans la base de données")
        print("❌ Problème dans la logique de recherche")
        print("\n💡 SOLUTIONS POSSIBLES:")
        print("1. Améliorer la fonction find_application")
        print("2. Vérifier les commandes vocales générées")
        print("3. Ajouter une recherche plus flexible")
    else:
        print("❌ Netflix pas dans la base de données")
        print("💡 Netflix n'est peut-être pas installé ou pas détecté lors du scan")

if __name__ == "__main__":
    diagnostic_netflix()
