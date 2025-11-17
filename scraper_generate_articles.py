import requests
import markdown
import pandas as pd
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from dateutil import parser as date_parser
from datetime import datetime
import os

QUERIES = [
    ("IA", "intelligence artificielle"),
    ("Tech", "technologie"),
    ("Véhicules électriques", "voiture electrique"),
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

OUTPUT_DIR = "articles_generated"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_feed(topic, query):
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
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
Analyse détaillée du contexte et de l'impact potentiel.

## Ce que cela change dans le domaine {topic}
- Innovation
- Concurrence
- Usage réel
- Marché global

## Notre avis
Une mise en perspective du sujet.

## Lien source
{source}

## FAQ

### Pourquoi cette actualité est importante ?
Elle influence le secteur {topic} d'une manière significative.

### Quel impact pour 2026 ?
Les experts estiment un changement majeur dans l'industrie.

"""

    filename = f"{OUTPUT_DIR}/{final_title.replace(' ', '_').replace(':','')}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    print("Article généré :", filename)

def main():
    all_items = []

    for topic, query in QUERIES:
        feed = fetch_feed(topic, query)
        all_items.extend(feed)

    # Garde les 5 meilleurs articles
    all_items = sorted(all_items, key=lambda x: x["date"], reverse=True)[:5]

    for item in all_items:
        generate_article(item)

if __name__ == "__main__":
    main()
