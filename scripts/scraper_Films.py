import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import pandas as pd
import os

# === Configuration générale ===
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    )
}

# === Liste des films à scraper ===
URLS = [
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=2954.html",   # Le Prête-nom
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=20297.html",  # Séduite et abandonnée
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=61282.html",  # Avatar
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=11010.html",  # Box of Moonlight
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=23170.html",  # Le Combat de Kyoshiro Nemuri
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=14637.html",  # Marie et le curé
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=32745.html",  # Youngblood
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=8292.html",   # L'Avocat du diable
    "https://www.allocine.fr/film/fichefilm_gen_cfilm=32741.html"   # Fanfan
]

# === Fonctions ===

def get_soup(url):
    """Télécharge le HTML d'une page et renvoie un objet BeautifulSoup"""
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def find_spectator_page(soup, base_url):
    """Cherche le lien vers la page 'critiques spectateurs'"""
    for a in soup.find_all("a", href=True):
        txt = (a.get_text() or "").strip().lower()
        href = a["href"]
        if "spectateur" in txt or "critique spectateur" in txt or "critiques spectateurs" in href:
            return urljoin(base_url, href)
    return None


def parse_note_from_element(el):
    """Extrait une note numérique d’un élément HTML"""
    sel = el.select_one("span.stareval-note, span[class*='note'], span[class*='rating']")
    if sel and sel.get_text(strip=True):
        s = re.sub(r"[^\d,\.]", "", sel.get_text(strip=True)).replace(",", ".")
        try:
            return float(s)
        except:
            pass
    for attr in ("data-note", "data-rating", "data-score"):
        if el.has_attr(attr):
            s = re.sub(r"[^\d\.]", "", str(el[attr]).replace(",", "."))
            try:
                return float(s)
            except:
                pass
    return None


def extract_reviews_from_soup(soup):
    """Récupère tous les avis utilisateurs d’une page"""
    reviews = []
    review_blocks = soup.select("div.review-card-content, p.content-txt")

    for rb in review_blocks[:200]:
        review_text = rb.get_text(" ", strip=True)
        if review_text:
            note = None
            prev_sib = rb.find_previous_sibling()
            if prev_sib:
                note = parse_note_from_element(prev_sib)
            reviews.append({"review": review_text, "user_note": note})

    return reviews


def scrape_allocine(url):
    """Scrape un film donné et renvoie le titre + les avis"""
    soup_home = get_soup(url)
    spec_url = find_spectator_page(soup_home, url)
    soup = get_soup(spec_url) if spec_url else soup_home

    title_tag = soup_home.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Titre inconnu"

    reviews = extract_reviews_from_soup(soup)
    return title, reviews


# === Exécution principale ===
if __name__ == "__main__":
    os.makedirs("scripts/data", exist_ok=True)
    all_data = []

    for url in URLS:
        try:
            title, reviews = scrape_allocine(url)
            for r in reviews:
                all_data.append({
                    "film_title": title,
                    "film_url": url,
                    "user_note": r["user_note"],
                    "review": r["review"]
                })
            print(f"[INFO] {len(reviews)} avis récupérés pour {title}")
        except Exception as e:
            print(f"[ERROR] Impossible de scraper {url}: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv("scripts/data/avis_films_bruts.csv", index=False, encoding="utf-8-sig")
    print("\n✅ Dataset sauvegardé dans scripts/data/avis_films_bruts.csv")
