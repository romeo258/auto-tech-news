import requests
import markdown
import pandas as pd
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from dateutil import parser as date_parser
from datetime import datetime
import os
import re

# ===========================
# FONCTION POUR NOMS DE FICHIERS SÉCURISÉS
# ===========================

def slugify(text):
    """
    Nettoie un texte pour en faire un nom de fichier valide sous Linux/Windows.
    - Retire accents et caractères spéciaux
    - Remplace tout caractère interdit par '_'
    - Limite à 150 caractères
    """
    # Remplace les caractères interdits
    text = re.sub(r"[^\w\-\. ]", "_", text)

    # Remplace les espaces par des underscores
    text = text.replace(" ", "_")

    # Limite longueur pour éviter erreurs GitHub
    return text[:150]


# ===========================
# CONFIG SCRAPER
# ===========================

QUERIES = [
    ("IA", "intelligence artificielle"),
    ("Tech", "technologie"),
    ("Véhicules électriques", "voiture electrique"),
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

OUTPUT_DIR = "articles_generated"

# Crée le dossier si absent (évite erreurs GitHub Actions)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================
# FONCTION POUR RÉCUPÉRER LES NEWS
# ===========================

def fetch_feed(topic, query):
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        desc = item.findtext("description") or ""
        pub_raw = item.findtext("pubDate") or ""

        try:
            pub_date = date_parser.parse(pub_raw)
        except:
            pub_date = datetime.now()

        items.append({
            "topic": topic,
            "title": title,
            "desc": desc,
            "date": pub_date,
            "link": link
        })

    return items


# ===========================
# GÉNÉRATION D'ARTICLE
# ===========================

def generate_article(data):
    title = data["title"]
    topic = data["topic"]
    source = data["link"]

    final_title = f"{title} : Analyse complète et impact {topic} en 2026"

    md = f"""
---
title: "{final_title}"
date: {datetime.now().strftime('%Y-%m-%d')}
meta_description: "{title} — analyse complète et implications dans le domaine {topic}."
tags: [{topic.lower()}, tech, ia, actualite]
---

## {title}

{data['desc']}

## Pourquoi cette nouvelle est importante
Cette actualité joue un rôle déterminant dans le secteur {topic}. Elle influence les stratégies, l’innovation et les usages futurs.

## Ce que cela change dans le domaine {topic}
- Impacts immédiats
- Risques et opportunités
- Influence sur le marché mondial
- Conséquences technologiques

## Analyse générale
Voici notre analyse de l’impact global de cette nouvelle dans la tech et l’IA.

## Lien source
{source}

## FAQ

### Pourquoi cette actualité est-elle importante ?
Elle influence directement le secteur {topic}, les modèles économiques et les futures innovations.

### Quel impact pour 2026 ?
Les experts anticipent une intensification des innovations, une concurrence accrue et une évolution rapide des usages.

"""

    # Nettoyage du nom de fichier
    safe_title = slugify(final_title)

    # Crée dossier si absent
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Chemin final
    filename = f"{OUTPUT_DIR}/{safe_title}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    print("Article généré :", filename)


# ===========================
# MAIN : LOGIQUE GLOBALE
# ===========================

def main():
    all_items = []

    for topic, query in QUERIES:
        feed = fetch_feed(topic, query)
        all_items.extend(feed)

    # Prend les 5 news les plus récentes
    all_items = sorted(all_items, key=lambda x: x["date"], reverse=True)[:5]

    for item in all_items:
        generate_article(item)


if __name__ == "__main__":
    main()
