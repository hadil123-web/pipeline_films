import subprocess
import sys
import os

print("🚀 Lancement du pipeline...")

# Récupère le chemin complet du Python actif (celui du venv)
python_exec = sys.executable

try:
    # Étape 1 : Scraping
    subprocess.run([python_exec, "scripts/scraper_Films.py"], check=True)

    # Étape 2 : Nettoyage
    subprocess.run([python_exec, "scripts/Nettoyage_et_transformation_Films.py"], check=True)

    print("✅ Pipeline terminé avec succès !")

except subprocess.CalledProcessError as e:
    print(f"❌ Erreur pendant le pipeline : {e}")
