import pandas as pd
import re
import string
import os

# === Fichiers d'entrée et de sortie ===
input_file = "scripts/data/avis_films_bruts.csv"
output_file = "scripts/data/films_clean.csv"

# Vérification que le fichier d'entrée existe
if not os.path.exists(input_file):
    print(f"❌ Fichier introuvable : {input_file}")
    exit()

print(f"📂 Chargement du fichier brut : {input_file}")
df = pd.read_csv(input_file)

# === Fonction de nettoyage du texte ===
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"<.*?>", " ", text)  # Retirer balises HTML
    text = re.sub(r"http\S+|www\S+", " ", text)  # Retirer liens
    text = text.translate(str.maketrans("", "", string.punctuation))  # Retirer ponctuation
    text = re.sub(r"\s+", " ", text).strip()  # Nettoyer espaces multiples
    return text

# Application du nettoyage
print("🧹 Nettoyage des textes en cours...")
df["clean_review"] = df["review"].apply(clean_text)

# === Suppression des doublons ===
before = len(df)
df = df.drop_duplicates(subset=["film_title", "clean_review"])
after = len(df)
print(f"🧩 Nombre de doublons supprimés : {before - after}")

# === Analyse de sentiment à partir de la note ===
def assign_sentiment(note):
    try:
        if pd.isna(note):
            return "Inconnu"
        elif note < 3:
            return "Négatif"
        elif note == 3:
            return "Neutre"
        else:
            return "Positif"
    except:
        return "Inconnu"

df["sentiment"] = df["user_note"].apply(assign_sentiment)

# === Sélection et sauvegarde du jeu de données final ===
df_clean = df[["film_title", "user_note", "film_url", "review", "clean_review", "sentiment"]]

os.makedirs("scripts/data", exist_ok=True)
df_clean.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"✅ Fichier nettoyé et enrichi sauvegardé : {output_file}")
print(df_clean.head(3))
