import requests
import markdown
import pandas as pd
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from dateutil import parser as date_parser
from datetime import datetime
import os
import re
import random

# ===========================
# FONCTION POUR NOMS DE FICHIERS SÉCURISÉS
# ===========================

def slugify(text):
    """
    Nettoie un texte pour en faire un nom de fichier valide sous Linux/Windows.
    - Remplace les caractères spéciaux
    - Remplace les espaces par des underscores
    - Limite à 150 caractères
    """
    text = re.sub(r"[^\w\-\. ]", "_", text)
    text = text.replace(" ", "_")
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
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===========================
# RÉCUPÉRATION DES NEWS
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
        except Exception:
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
# GÉNÉRATION D'ARTICLE - TEMPLATES VARIÉS
# ===========================

def generate_article(data):
    title = data["title"].strip()
    topic = data["topic"]
    source = data["link"].strip()
    desc = (data["desc"] or "").strip()

    main_kw = topic.lower()

    # Variations de titres SEO
    title_patterns = [
        f"{title} : analyse détaillée, enjeux cachés et impact {topic} en 2026",
        f"{title} : ce que cela change vraiment pour le secteur {topic} d’ici 2026",
        f"{title} : décryptage complet et conséquences majeures pour {topic}",
        f"{title} : pourquoi cette annonce peut bouleverser le domaine {topic} en 2026",
    ]
    final_title = random.choice(title_patterns)

    # Intros variées
    intro_patterns = [
        (
            f"L’actualité autour de **{title}** fait beaucoup parler dans l’écosystème {topic}. "
            f"Cette annonce illustre parfaitement la vitesse à laquelle les technologies liées à {topic} évoluent. "
            f"Dans cet article, nous proposons un décryptage complet : contexte, enjeux, impacts concrets et perspectives à l’horizon 2026."
        ),
        (
            f"Chaque semaine, de nouvelles annonces viennent redistribuer les cartes dans le domaine {topic}. "
            f"Parmi elles, **{title}** attire particulièrement l’attention des observateurs et des professionnels. "
            f"Voici une analyse structurée pour comprendre ce qui se joue véritablement derrière cette information."
        ),
        (
            f"Le secteur {topic} est en pleine effervescence, et **{title}** en est une nouvelle illustration. "
            f"Au-delà du titre et de la première lecture, cette actualité révèle des signaux forts sur l’orientation du marché, "
            f"les stratégies des grands acteurs et l’évolution des usages. Décryptage complet."
        ),
        (
            f"Entre effet d’annonce, réalité technologique et enjeux économiques, **{title}** mérite un examen attentif. "
            f"Pour les lecteurs qui souhaitent aller au-delà des simples brèves d’actualité, nous proposons ici une analyse détaillée, "
            f"centrée sur les impacts réels pour le secteur {topic} et les perspectives d’ici 2026."
        ),
    ]
    intro = random.choice(intro_patterns)

    # Variations de titres de sections
    h2_points = random.choice([
        "📌 Les points clés à retenir",
        "📌 Ce qu’il faut retenir en priorité",
        "📌 Les éléments essentiels de cette annonce",
        "📌 Les faits marquants à connaître"
    ])

    h2_context = random.choice([
        "🌍 Contexte : où se situe cette annonce dans le paysage {topic} ?",
        "🌍 Remettre cette actualité dans son contexte {topic}",
        "🌍 Un contexte {topic} en pleine mutation",
        "🌍 Pourquoi cette nouvelle arrive à un moment clé pour {topic}"
    ])

    h2_analysis = random.choice([
        "🧠 Analyse stratégique et lecture critique",
        "🧠 Que révèle vraiment cette annonce ?",
        "🧠 Décryptage des enjeux visibles et moins visibles",
        "🧠 Une lecture analytique au-delà du buzz"
    ])

    h2_impacts = random.choice([
        "🚀 Impacts concrets pour le secteur {topic}",
        "🚀 Conséquences possibles à court et moyen terme",
        "🚀 Comment cette annonce peut transformer {topic} d’ici 2026",
        "🚀 Ce que cela change pour les acteurs du {topic}"
    ])

    h2_market = random.choice([
        "📊 Réactions possibles du marché et des acteurs",
        "📊 Quel impact pour les entreprises, les investisseurs et les utilisateurs ?",
        "📊 Comment les différents acteurs peuvent se positionner",
        "📊 Opportunités et risques à surveiller"
    ])

    h2_conclusion = random.choice([
        "✅ Conclusion : une actualité à suivre de près",
        "✅ En résumé : pourquoi cette annonce est loin d’être anodine",
        "✅ Synthèse : ce qu’il faut retenir pour la suite",
        "✅ Ce qu’il faut garder en tête pour 2026"
    ])

    # Quelques variations d’angles
    angle_sentences = [
        f"Pour les entreprises déjà engagées dans {topic}, cette annonce est un signal à prendre au sérieux.",
        f"Pour les acteurs qui hésitaient encore à investir dans {topic}, ce type d’actualité joue souvent un rôle de déclencheur.",
        f"Pour les utilisateurs finaux, cette évolution se traduira probablement par de nouveaux services, produits ou expériences.",
        f"Pour les décideurs publics et régulateurs, ce genre d’annonce pose aussi des questions de gouvernance, de souveraineté et d’éthique."
    ]
    angle_block = " ".join(random.sample(angle_sentences, k=2))

    # 3 TEMPLATES DIFFÉRENTS : ordre + formulation varient
    template_id = random.choice([1, 2, 3])

    if template_id == 1:
        # Modèle analytique “classique”
        body = f"""
# {final_title}

## Introduction
{intro}

## {h2_points}
- Une nouvelle étape importante pour le secteur **{topic}**
- Un signal fort envoyé aux concurrents et aux partenaires
- Des enjeux technologiques, économiques et parfois géopolitiques
- Une illustration concrète de la vitesse d’évolution du marché
- Une actualité qui s’inscrit dans une tendance de fond

## 🔎 Résumé de l’information
{desc or "Les détails précis de l’annonce peuvent varier selon la source, mais l’essentiel est qu’elle marque un tournant significatif dans l’évolution du domaine."}

## {h2_context.format(topic=topic.lower())}
Le secteur **{topic}** est engagé dans une phase d’accélération où l’innovation ne se limite plus à des prototypes, mais se traduit par des déploiements concrets.  
Entre concurrence internationale, pression sur les coûts, attentes des utilisateurs et contraintes réglementaires, chaque annonce comme **{title}** doit se lire à la lumière de ce contexte global.

{angle_block}

## {h2_analysis}
Au-delà de l’information brute, cette actualité met en lumière plusieurs dynamiques :
- une volonté d’occuper le terrain médiatique sur les sujets {topic},
- un besoin de rassurer investisseurs et partenaires,
- une recherche d’avantage concurrentiel durable,
- une course à la différenciation par l’innovation.

L’analyse de **{title}** montre que l’enjeu n’est pas seulement technologique : il est aussi stratégique, commercial et parfois politique.

## {h2_impacts.format(topic=topic.lower())}
À court terme, cette annonce devrait :
- renforcer la visibilité des solutions liées à {topic},
- alimenter de nouveaux projets pilotes ou POC,
- encourager les concurrents à accélérer leurs propres feuilles de route.

À moyen terme (horizon 2026), les impacts possibles incluent :
- une adoption plus massive de ces technologies,
- une évolution des modèles économiques,
- une transformation des compétences recherchées sur le marché du travail.

## {h2_market}
Du côté des entreprises, cette actualité peut servir de point d’appui pour :
- ajuster leur stratégie {topic},
- revisiter leurs priorités d’investissement,
- communiquer à leur tour sur leurs avancées.

Pour les investisseurs, elle sert d’indicateur supplémentaire sur la maturité du marché.  
Pour les utilisateurs, elle annonce souvent de nouvelles fonctionnalités, services ou expériences à venir.

## {h2_conclusion}
En résumé, **{title}** n’est pas une simple brève parmi d’autres.  
Elle s’inscrit dans une trajectoire de fond où {topic} devient un pilier central des stratégies d’innovation et de différenciation.  
Les acteurs qui prendront le temps d’analyser ce type d’actualité et d’en tirer des enseignements concrets auront une longueur d’avance à l’horizon 2026.

## 🔗 Source de l’information
{source}
"""
    elif template_id == 2:
        # Modèle plus “journalistique / récit”
        body = f"""
# {final_title}

## Une actualité qui illustre la course à l'innovation
{intro}

Depuis plusieurs années, {topic.lower()} est devenu un terrain de compétition intense entre grands groupes, start-up et acteurs institutionnels.  
L’annonce autour de **{title}** vient ajouter un chapitre supplémentaire à ce récit, avec des enjeux multiples : image de marque, leadership technologique, conquête de nouveaux marchés.

## {h2_points}
- {topic} au centre des priorités stratégiques
- Un message adressé autant aux investisseurs qu’aux concurrents
- Des implications possibles pour la feuille de route des acteurs du secteur
- Un indicateur des tendances majeures pour les prochaines années

## Ce que l’on sait concrètement
{desc or "Les informations disponibles mettent en avant une avancée significative, mais la profondeur de l’impact dépendra des déploiements réels qui suivront cette annonce."}

## {h2_context.format(topic=topic.lower())}
Comprendre l’importance de **{title}**, c’est le replacer dans un environnement où :
- les cycles d’innovation sont de plus en plus courts,
- la pression concurrentielle s’intensifie,
- les attentes des utilisateurs deviennent plus exigeantes,
- la question de l’éthique, de la régulation et de la transparence prend de l’ampleur.

{angle_block}

## {h2_analysis}
Plutôt que de se limiter à une lecture superficielle, il est utile d’identifier :
- ce que cette actualité change vraiment,
- ce qui relève surtout de la communication,
- ce qui pourrait annoncer une transformation plus profonde.

Cette approche permet de distinguer l’effet d’annonce des tendances solides.

## {h2_impacts.format(topic=topic.lower())}
En pratique, les impacts possibles sont multiples :
- stimulation de la concurrence sur des fonctionnalités similaires,
- intensification des efforts R&D,
- multiplication de partenariats technologiques ou industriels,
- évolution des attentes des clients vis-à-vis des solutions {topic}.

## {h2_market}
Les marchés réagissent généralement avec un mélange d’enthousiasme et de prudence.  
Cette annonce peut :
- rassurer certains investisseurs,
- pousser d’autres à attendre des preuves concrètes,
- redéfinir la perception de certains acteurs.

## {h2_conclusion}
L’annonce **{title}** illustre une tendance claire : {topic} n’est plus un sujet marginal ou expérimental.  
C’est désormais un terrain sur lequel se joue une partie importante de la compétitivité future.  
Suivre ce type d’actualité de près est donc essentiel pour anticiper les évolutions à venir.

## 🔗 Pour aller plus loin
Source d’origine : {source}
"""
    else:
        # Modèle “prospective & futur”
        body = f"""
# {final_title}

## Une annonce tournée vers l’avenir
{intro}

Cette actualité s’inscrit dans une trajectoire où {topic.lower()} devient un levier central de transformation.  
Qu’il s’agisse de performance, de productivité, d’expérience utilisateur ou de nouveaux modèles économiques, **{title}** vient renforcer une dynamique déjà bien engagée.

## {h2_points}
- Une confirmation que {topic.lower()} entre dans une nouvelle phase de maturité
- Un signal adressé aux concurrents, partenaires et institutions
- Une opportunité pour repenser les stratégies à moyen terme
- Un indicateur de la direction que prend l’écosystème tech

## Que dit réellement l’annonce ?
{desc or "L’annonce reste partiellement générale, mais les orientations qu’elle laisse entrevoir sont cohérentes avec l’évolution globale du secteur."}

## {h2_context.format(topic=topic.lower())}
Le contexte actuel est marqué par :
- une intensification de la recherche autour de {topic.lower()},
- une volonté de rendre ces technologies plus accessibles,
- des débats autour de l’éthique, de l’impact social et environnemental,
- une compétition entre régions du monde pour attirer talents et investissements.

{angle_block}

## {h2_analysis}
Cette annonce peut être interprétée comme :
- une tentative de consolider une position dominante,
- une réponse à des mouvements concurrents récents,
- un moyen de préparer le terrain à d’autres annonces futures.

Au-delà du discours officiel, elle montre que la bataille pour le leadership sur {topic.lower()} est loin d’être terminée.

## {h2_impacts.format(topic=topic.lower())}
Les impacts potentiels incluent :
- un élargissement du nombre d’acteurs intéressés par {topic.lower()},
- de nouvelles expérimentations dans plusieurs secteurs d’activité,
- une accélération des projets pilotes et des déploiements.

## {h2_market}
Pour les entreprises, cette actualité est l’occasion de :
- revoir leur feuille de route stratégique,
- valider ou ajuster leurs choix technologiques,
- identifier de nouveaux partenaires.

Pour les talents et professionnels du secteur, elle confirme que les compétences liées à {topic.lower()} resteront très demandées.

## {h2_conclusion}
En définitive, **{title}** doit être compris comme un jalon supplémentaire dans la montée en puissance de {topic.lower()}.  
Ce n’est ni un point de départ, ni une fin en soi, mais une étape dans un mouvement plus large qui façonne déjà le paysage technologique de 2026 et au-delà.

## 🔗 Source
{source}
"""

    # Bloc FAQ + mots-clés SEO (ajouté à tous les templates)
    faq_block = f"""
## ❓ FAQ — Questions fréquentes

### Pourquoi cette actualité autour de {topic.lower()} est-elle importante ?
Parce qu’elle éclaire la direction que prend le marché et les priorités des grands acteurs technologiques.

### Est-ce une simple annonce marketing ou une vraie rupture ?
Comme souvent, la réalité se situe entre les deux. L’analyse détaillée permet de distinguer l’effet de communication des transformations durables.

### Quel impact d’ici 2026 ?
Les effets les plus visibles devraient se matérialiser dans les prochaines années, au travers de nouveaux produits, services et usages.

### Cette annonce concerne-t-elle uniquement les grandes entreprises ?
Non, les PME, start-up et indépendants sont également concernés, notamment via les outils, plateformes et services qui seront mis à leur disposition.

### Comment suivre efficacement ce type d’évolution ?
En combinant veille technologique, compréhension des enjeux business et réflexion stratégique sur son propre positionnement.

## 🏷️ Mots-clés RankMath
{main_kw}, {main_kw} 2026, actualité {main_kw}, innovation {main_kw}, tendances tech 2026, analyse technologique, news {main_kw}
"""

    full_md = f"""---
title: "{final_title}"
date: {datetime.now().strftime('%Y-%m-%d')}
meta_description: "{title} — analyse complète, enjeux, impacts et perspectives 2026 dans le domaine {topic}."
tags: [{main_kw}, tech, ia, actualite, 2026]
---

{body}

{faq_block}
"""

    safe_title = slugify(final_title)
    filename = f"{OUTPUT_DIR}/{safe_title}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_md)

    print(f"✔️ Article généré (template {template_id}) :", filename)


# ===========================
# MAIN
# ===========================

def main():
    all_items = []

    for topic, query in QUERIES:
        feed = fetch_feed(topic, query)
        all_items.extend(feed)

    # On garde les 5 plus récentes
    all_items = sorted(all_items, key=lambda x: x["date"], reverse=True)[:5]

    for item in all_items:
        generate_article(item)


if __name__ == "__main__":
    main()
