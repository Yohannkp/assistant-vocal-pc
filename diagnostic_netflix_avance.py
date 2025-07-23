"""
Diagnostic avancé pour Netflix UWP
==================================
Ce script va tenter de détecter et ouvrir Netflix avec toutes les méthodes possibles
"""

import subprocess
import os
import sys
import json
import time

def test_netflix_methods():
    """Teste toutes les méthodes d'ouverture de Netflix"""
    
    print("🔍 DIAGNOSTIC AVANCÉ NETFLIX UWP")
    print("=" * 50)
    
    # Charger les données d'applications
    try:
        with open("applications_assistant.json", 'r', encoding='utf-8') as f:
            apps = json.load(f)
        
        # Trouver toutes les applications Netflix
        netflix_apps = {}
        for app_key, app_data in apps.items():
            if 'netflix' in app_key.lower() or 'netflix' in app_data.get('nom', '').lower():
                netflix_apps[app_key] = app_data
        
        print(f"📱 {len(netflix_apps)} applications Netflix trouvées:")
        for app_key, app_data in netflix_apps.items():
            print(f"   - {app_key}: {app_data.get('nom', 'N/A')}")
            print(f"     Chemin: {app_data.get('chemin', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"❌ Erreur lecture applications: {e}")
        return
    
    # Méthode 1: Lister toutes les apps UWP installées
    print("🔍 MÉTHODE 1: Recherche via PowerShell Get-AppxPackage")
    try:
        cmd = 'powershell -Command "Get-AppxPackage | Where-Object {$_.Name -like \'*Netflix*\'} | Select-Object Name, PackageFamilyName, InstallLocation"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Résultats Get-AppxPackage:")
            print(result.stdout)
        else:
            print(f"❌ Erreur Get-AppxPackage: {result.stderr}")
    except Exception as e:
        print(f"❌ Exception Get-AppxPackage: {e}")
    
    print("\n" + "-" * 50)
    
    # Méthode 2: Utiliser le registre Windows
    print("🔍 MÉTHODE 2: Recherche via registre Windows")
    try:
        cmd = 'reg query "HKEY_CURRENT_USER\\Software\\Classes\\ActivatableClasses\\Package" /s /f "Netflix" 2>nul'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0 and result.stdout:
            print("✅ Entrées registre trouvées:")
            lines = result.stdout.split('\n')[:10]  # Limiter à 10 lignes
            for line in lines:
                if line.strip():
                    print(f"   {line.strip()}")
        else:
            print("❌ Aucune entrée registre trouvée")
    except Exception as e:
        print(f"❌ Exception registre: {e}")
    
    print("\n" + "-" * 50)
    
    # Méthode 3: Tests d'ouverture avec différents chemins
    print("🚀 MÉTHODE 3: Tests d'ouverture avec différents chemins")
    
    # Chemins à tester
    test_paths = [
        "4DF9E0F8.Netflix",
        "4DF9E0F8.Netflix_mcm4njqhnhss8",
        "4DF9E0F8.Netflix_mcm4njqhnhss8!Netflix.App",
        "netflix:",
        "ms-windows-store://pdp/?productid=9wzdncrfj3tj"
    ]
    
    for i, path in enumerate(test_paths, 1):
        print(f"\n🧪 Test {i}: {path}")
        
        # Test avec explorer
        try:
            if path.startswith("ms-windows-store://"):
                cmd = f'start "" "{path}"'
            else:
                cmd = f'explorer "shell:appsfolder\\{path}"'
            
            print(f"   Commande: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            
            if result.returncode == 0:
                print(f"   ✅ Succès avec explorer!")
                time.sleep(2)  # Laisser le temps de voir si ça s'ouvre
                return path  # Retourner le chemin qui fonctionne
            else:
                print(f"   ❌ Échec explorer: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Exception explorer: {e}")
        
        # Test avec PowerShell Start-Process
        try:
            if path.startswith("ms-windows-store://"):
                cmd = f'powershell -Command "Start-Process \\"{path}\\""'
            else:
                cmd = f'powershell -Command "Start-Process \\"shell:appsfolder\\{path}\\""'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
            
            if result.returncode == 0:
                print(f"   ✅ Succès avec PowerShell!")
                time.sleep(2)
                return path
            else:
                print(f"   ❌ Échec PowerShell: {result.stderr[:100]}...")
        except Exception as e:
            print(f"   ❌ Exception PowerShell: {e}")
    
    print("\n" + "-" * 50)
    
    # Méthode 4: Ouvrir le Microsoft Store pour installer Netflix
    print("🏪 MÉTHODE 4: Ouverture du Microsoft Store")
    try:
        store_url = "ms-windows-store://pdp/?productid=9wzdncrfj3tj"
        cmd = f'start "" "{store_url}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=8)
        
        if result.returncode == 0:
            print("✅ Microsoft Store ouvert pour Netflix!")
            print("💡 Vous pouvez installer ou réinstaller Netflix depuis le Store")
        else:
            print(f"❌ Impossible d'ouvrir le Store: {result.stderr}")
    except Exception as e:
        print(f"❌ Exception Store: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNOSTIC TERMINÉ")
    print("💡 Si aucune méthode n'a fonctionné, Netflix n'est peut-être pas installé")
    print("💡 ou doit être réinstallé depuis le Microsoft Store")
    
    return None

if __name__ == "__main__":
    working_path = test_netflix_methods()
    if working_path:
        print(f"\n🎉 CHEMIN FONCTIONNEL TROUVÉ: {working_path}")
    else:
        print("\n❌ Aucun chemin fonctionnel trouvé")
