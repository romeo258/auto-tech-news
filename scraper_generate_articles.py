import requests
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from dateutil import parser as date_parser
from datetime import datetime
import os
import re
import random
from wp_publish import publish_article


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
# CONFIG SCRAPER – THÈMES ÉLARGIS
# ===========================

QUERIES = [
    ("Intelligence artificielle", "intelligence artificielle actualités 2026"),
    ("Smartphones", "nouveau smartphone test fiche technique 2026"),
    ("Apple et Google", "nouveautés produits Apple Google 2026"),
    ("Voitures électriques", "nouvelle voiture électrique 2026 autonomie batterie"),
    ("DevOps et Cloud", "nouveautés devops cloud plateforme kubernetes"),
    ("Frameworks web", "nouvelle version Angular React Vue 2026"),
    ("Frameworks mobiles", "nouvelle version Flutter React Native 2026"),
    ("Salaires IA", "salaire ingénieur IA Google Meta NVIDIA 2026"),
    ("Guerre des géants tech", "concurrence géants de la tech Google Apple Microsoft Amazon Meta"),
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=fr&gl=FR&ceid=FR:fr"

OUTPUT_DIR = "articles_generated"


# ===========================
# CLEAN DU DOSSIER AVANT CHAQUE RUN
# ===========================

def clean_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, name)
        if os.path.isfile(path):
            os.remove(path)


# ===========================
# RÉCUPÉRATION DES NEWS
# ===========================

def fetch_feed(topic, query):
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
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
            "title": title.strip(),
            "desc": (desc or "").strip(),
            "date": pub_date,
            "link": link.strip()
        })

    return items


# ===========================
# BLOCS COMMUNS (FAQ, MOTS-CLÉS)
# ===========================

def build_faq_html(topic, main_kw):
    topic_lower = topic.lower()
    return f"""
<h2>FAQ – Questions fréquentes sur {topic_lower}</h2>

<h3>Pourquoi cette actualité sur {topic_lower} est-elle importante&nbsp;?</h3>
<p>Parce qu’elle éclaire la direction que prend le marché et les priorités stratégiques des grands acteurs technologiques.</p>

<h3>Est-ce une simple annonce marketing ou une vraie rupture&nbsp;?</h3>
<p>Comme souvent, la réalité se situe entre les deux. L’analyse permet de distinguer l’effet de communication des transformations profondes et durables.</p>

<h3>Quel impact concret d’ici 2026&nbsp;?</h3>
<p>Les impacts se matérialiseront par de nouveaux produits, services, outils ou modèles économiques, avec une concurrence accrue autour de {topic_lower}.</p>

<h3>Qui est concerné par cette évolution&nbsp;?</h3>
<p>Les grandes entreprises, les start-ups, mais aussi les développeurs, les ingénieurs, les équipes DevOps, les acteurs du cloud et, au final, les utilisateurs finaux.</p>

<h3>Comment suivre efficacement ce type de tendance&nbsp;?</h3>
<p>En combinant veille technologique, suivi des annonces officielles, analyse de la concurrence et compréhension fine des besoins du marché.</p>

<div class="article-keywords">
  <strong>Mots-clés stratégiques :</strong>
  <span>{main_kw}</span>,
  <span>{main_kw} 2026</span>,
  <span>actualité {main_kw}</span>,
  <span>innovation {main_kw}</span>,
  <span>tendances tech 2026</span>,
  <span>analyse technologique</span>,
  <span>veille technologique</span>
</div>
"""


# ===========================
# GÉNÉRATION D'UN ARTICLE HTML – 8 TEMPLATES VARIÉS
# ===========================

def generate_article(data):
    title = data["title"]
    topic = data["topic"]
    source = data["link"]
    desc = data["desc"] or ""
    main_kw = topic.lower()

    # Variations de titres SEO forts
    title_patterns = [
        f"{title} : analyse complète et impact sur {topic} en 2026",
        f"{title} : ce que cela change pour le marché {topic} en 2026",
        f"{title} : décryptage stratégique pour le secteur {topic}",
        f"{title} : pourquoi cette annonce va compter dans {topic}",
        f"{title} : enjeux, risques et opportunités dans l’écosystème {topic}",
    ]
    final_title = random.choice(title_patterns)

    # Intros variées
    intro_patterns = [
        f"L’actualité autour de <strong>{title}</strong> s’est rapidement imposée dans le paysage tech. Elle touche directement au domaine de <strong>{topic}</strong> et s’inscrit dans une dynamique où les annonces se succèdent à un rythme soutenu. Cet article propose une analyse structurée pour comprendre ce qui se joue réellement derrière cette nouvelle.",
        f"Chaque semaine, de nouvelles annonces transforment le secteur de <strong>{topic}</strong>. Parmi elles, <strong>{title}</strong> retient particulièrement l’attention des professionnels, des investisseurs et des passionnés de technologie. Voici un décryptage complet et accessible, orienté résultats concrets et vision 2026.",
        f"Le domaine de <strong>{topic}</strong> est au cœur d’une compétition intense entre les géants de la tech, les constructeurs, les fournisseurs de cloud et les acteurs de l’IA. L’annonce <strong>{title}</strong> en est une nouvelle illustration. Pour éviter de rester à la surface de l’information, nous proposons ici une analyse détaillée, claire et directement exploitable.",
        f"Dans un contexte où {topic.lower()} est devenu un enjeu stratégique majeur, l’annonce intitulée <strong>{title}</strong> mérite d’être examinée en profondeur. Plutôt que de se limiter aux titres, cet article revient sur les faits, le contexte, les impacts et les perspectives.",
    ]
    intro_html = random.choice(intro_patterns)

    # Variations de H2
    h2_points = random.choice([
        "Les points clés à retenir",
        "Ce qu’il faut retenir en priorité",
        "Les éléments essentiels de cette annonce",
        "Les faits marquants à connaître"
    ])

    h2_context = random.choice([
        "Remettre cette actualité dans le contexte du marché",
        "Contexte : où en est vraiment le secteur",
        "Un secteur en pleine mutation",
        "Pourquoi cette annonce arrive à un moment clé"
    ])

    h2_analysis = random.choice([
        "Analyse stratégique et technique",
        "Ce que révèle vraiment cette annonce",
        "Lecture analytique au-delà du buzz",
        "Une analyse détaillée pour les décideurs"
    ])

    h2_impacts = random.choice([
        "Impacts concrets pour le secteur",
        "Conséquences possibles à court et moyen terme",
        "Ce que cela change pour les acteurs du marché",
        "Influence sur les stratégies produits et R&amp;D"
    ])

    h2_market = random.choice([
        "Réactions possibles du marché",
        "Enjeux business et positionnement concurrentiel",
        "Opportunités et risques à surveiller",
        "Comment les acteurs peuvent se repositionner"
    ])

    h2_conclusion = random.choice([
        "Conclusion : une actualité à suivre de près",
        "En résumé : pourquoi cette annonce est importante",
        "Synthèse et perspectives pour 2026",
        "Ce qu’il faut garder en tête pour la suite"
    ])

    angle_sentences = [
        f"Pour les entreprises déjà engagées dans {topic.lower()}, cette annonce peut servir de déclencheur pour accélérer certains projets.",
        f"Pour les équipes produits, marketing ou R&amp;D, elle offre un signal fort sur les priorités du marché et les attentes des utilisateurs.",
        f"Pour les profils techniques (développeurs, ingénieurs, DevOps, spécialistes cloud), cette évolution se traduira souvent par de nouveaux outils, de nouvelles pratiques et de nouvelles compétences à maîtriser.",
        f"Pour les investisseurs et décideurs, elle fournit un indicateur supplémentaire sur les domaines dans lesquels il est stratégique d’allouer du budget dès maintenant."
    ]
    angle_block = " ".join(random.sample(angle_sentences, k=2))

    # =====================
    # 8 TEMPLATES DIFFÉRENTS
    # =====================

    template_id = random.randint(1, 8)

    # Contenu résumé (on reformule légèrement)
    resume_html = (
        f"<p>{desc}</p>" if desc else
        "<p>Les détails exacts de l’annonce peuvent varier selon les sources, "
        "mais l’information met clairement en lumière une évolution importante pour le secteur.</p>"
    )

    if template_id == 1:
        # Modèle analytique "classique"
        body = f"""
<h1>{final_title}</h1>

<h2>Introduction</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une actualité structurante pour le secteur de {topic.lower()}.</li>
  <li>Un signal envoyé aux concurrents, partenaires et clients.</li>
  <li>Des enjeux technologiques, économiques et parfois réglementaires.</li>
  <li>Un indicateur précieux pour anticiper les tendances 2026.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Le secteur de {topic.lower()} évolue très rapidement. Entre innovations matérielles, mises à jour logicielles,
évolutions des frameworks, essor des voitures électriques, nouvelles offres cloud et guerre des géants de la tech,
chaque annonce comme <strong>{title}</strong> doit être lue dans un contexte global.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Au-delà du communiqué officiel, cette actualité confirme plusieurs tendances&nbsp;: une accélération de l’innovation,
une compétition accrue entre géants de la tech, et une pression croissante sur les acteurs qui ne suivent pas le rythme.
Pour les ingénieurs, développeurs et équipes DevOps, cela se traduit par des outils, des pratiques et des exigences
qui évoluent en permanence.
</p>

<h2>{h2_impacts}</h2>
<p>
À court terme, cette annonce peut influencer les roadmaps produits, les arbitrages budgétaires ou les choix technologiques
au sein des entreprises. À moyen terme, elle s’inscrit dans une trajectoire où le marché valorise davantage
les solutions performantes, fiables, sécurisées et alignées avec les attentes des utilisateurs.
</p>

<h2>{h2_market}</h2>
<p>
Sur le plan concurrentiel, ce type d’information incite les autres acteurs à réagir&nbsp;: lancer une fonctionnalité
équivalente, revoir leur stratégie de communication, ou accélérer le lancement d’une nouvelle version de produit
(smartphone, framework, service cloud, modèle d’IA, etc.).
</p>

<h2>{h2_conclusion}</h2>
<p>
En résumé, <strong>{title}</strong> n’est pas une actualité isolée. Elle fait partie d’un mouvement de fond
où {topic.lower()} devient un levier majeur de différenciation. Les acteurs qui anticipent et exploitent ce genre
d’information prennent une longueur d’avance dans un marché très concurrentiel.
</p>
"""
    elif template_id == 2:
        # Modèle plus "journalistique / récit"
        body = f"""
<h1>{final_title}</h1>

<h2>Une nouvelle étape dans la course à l’innovation</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>{topic} reste au cœur des priorités des géants de la tech.</li>
  <li>Les annonces se multiplient autour des smartphones, de l’IA, du cloud et des voitures électriques.</li>
  <li>Les équipes techniques doivent suivre un rythme de mise à jour de plus en plus soutenu.</li>
  <li>Les salaires et la compétition pour les talents reflètent cette tension.</li>
</ul>

<h2>Ce que l’on sait concrètement</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Depuis plusieurs années, le secteur de {topic.lower()} est engagé dans une transformation profonde. 
Qu’il s’agisse de nouvelles puces pour smartphones, de frameworks web et mobiles mis à jour,
de services cloud managés ou de modèles d’IA entraînés à grande échelle, chaque annonce contribue
à redessiner les équilibres du marché.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Cette annonce doit être comprise comme un nouveau jalon dans la bataille que se livrent Apple, Google,
Microsoft, Amazon, Meta, NVIDIA, mais aussi de nombreux constructeurs et fournisseurs de services.
Elle permet de mesurer leurs priorités actuelles&nbsp;: performance, intégration, expérience utilisateur,
et captation de valeur via des écosystèmes fermés ou fortement intégrés.
</p>

<h2>{h2_impacts}</h2>
<p>
Pour les entreprises clientes, cela signifie souvent davantage d’options technologiques, mais aussi des choix
plus complexes à faire. Pour les profils techniques, c’est la confirmation que la veille et l’auto-formation
restent indispensables pour rester à jour.
</p>

<h2>{h2_market}</h2>
<p>
Côté marché, ce type d’actualité peut influencer la perception des marques, la confiance des investisseurs
et l’attractivité de certains postes (par exemple les salaires des ingénieurs IA chez Google, Meta ou NVIDIA).
</p>

<h2>{h2_conclusion}</h2>
<p>
Au final, <strong>{title}</strong> s’inscrit dans une course globale à l’innovation. Pour rester compétitifs,
les acteurs doivent non seulement suivre ces annonces, mais surtout en tirer des décisions concrètes
en termes de stratégie, de recrutement, de produit et de technologie.
</p>
"""
    elif template_id == 3:
        # Modèle "prospective"
        body = f"""
<h1>{final_title}</h1>

<h2>Une annonce tournée vers l’avenir</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une confirmation de la place centrale de {topic.lower()} dans les stratégies tech.</li>
  <li>Des signaux utiles pour anticiper les priorités à l’horizon 2026.</li>
  <li>Un impact potentiel sur les roadmaps produits et frameworks.</li>
  <li>Des implications possibles pour les salaires et les compétences recherchées.</li>
</ul>

<h2>Que dit réellement l’annonce&nbsp;?</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Le contexte actuel est marqué par la montée en puissance de l’IA, la généralisation des architectures cloud,
l’industrialisation du DevOps, la multiplication des modèles de smartphones, et une concurrence féroce
dans les voitures électriques. L’annonce <strong>{title}</strong> se situe à l’intersection de plusieurs de ces dynamiques.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Elle peut être perçue comme une tentative de prendre l’avantage, de rattraper un retard ou de consolider 
une position dominante. Dans tous les cas, elle indique que le jeu reste ouvert et que les grands acteurs
testent en permanence de nouveaux positionnements.
</p>

<h2>{h2_impacts}</h2>
<p>
Pour les équipes techniques et métiers, cette actualité peut justifier l’ouverture de nouveaux chantiers,
la révision de certains arbitrages ou la priorisation de nouvelles fonctionnalités. Pour les utilisateurs finaux,
elle se traduira, à terme, par des services plus nombreux, plus personnalisés ou plus performants.
</p>

<h2>{h2_market}</h2>
<p>
Les marchés réagissent souvent de façon rapide à ce type d’information, mais la vraie question est celle
de la capacité des acteurs à transformer l’annonce en résultats concrets. C’est ce qui fera la différence d’ici 2026.
</p>

<h2>{h2_conclusion}</h2>
<p>
En définitive, <strong>{title}</strong> doit être lu comme un signal parmi d’autres dans une tendance lourde.
Ceux qui sauront interpréter correctement ces signaux et ajuster leur stratégie auront un avantage compétitif durable.
</p>
"""
    elif template_id == 4:
        # Modèle "focus salaires / marché de l'emploi"
        body = f"""
<h1>{final_title}</h1>

<h2>Une actualité qui en dit long sur le marché de l’emploi tech</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une demande toujours forte sur les profils {topic.lower()} et connexes.</li>
  <li>Des salaires tirés vers le haut par la compétition entre géants de la tech.</li>
  <li>Une pression accrue sur les compétences en IA, cloud, DevOps et frameworks modernes.</li>
  <li>Des écarts de rémunération importants selon les pays et les entreprises.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Les salaires des ingénieurs IA chez Google, Meta, NVIDIA ou d’autres géants illustrent un mouvement global&nbsp;:
les profils capables de combiner compétences techniques pointues et compréhension business sont très recherchés.
Cette actualité s’inscrit dans cette dynamique de tension sur le marché des talents.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Pour les candidats, cette situation offre des opportunités, mais impose aussi un haut niveau d’exigence.
Pour les entreprises, elle implique de repenser les politiques de rémunération, de formation et de fidélisation.
</p>

<h2>{h2_impacts}</h2>
<p>
À court terme, cela peut accentuer la pénurie sur certains profils. À moyen terme, les entreprises qui n’investissent
pas suffisamment dans les compétences IA, cloud, DevOps ou mobile risquent d’être en difficulté face à la concurrence.
</p>

<h2>{h2_market}</h2>
<p>
Le marché reflète déjà ces tensions à travers les offres d’emploi, les enquêtes de rémunération et les stratégies
très agressives de certains acteurs pour attirer et retenir les talents clés.
</p>

<h2>{h2_conclusion}</h2>
<p>
Cette actualité ne concerne pas uniquement quelques ingénieurs très bien payés&nbsp;: elle révèle
une transformation profonde du marché du travail tech. Comprendre ces signaux permet de mieux orienter
ses choix de carrière, de formation et de spécialisation.
</p>
"""
    elif template_id == 5:
        # Modèle "smartphones / produits"
        body = f"""
<h1>{final_title}</h1>

<h2>Un nouveau produit au cœur de la stratégie des constructeurs</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Un nouvel appareil qui s’inscrit dans une gamme déjà très compétitive.</li>
  <li>Un positionnement qui joue sur la puissance, l’autonomie, la photo ou l’IA embarquée.</li>
  <li>Un écosystème logiciel et matériel de plus en plus verrouillé.</li>
  <li>Une concurrence frontale entre Apple, Google, Samsung et d’autres acteurs.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Les lancements de nouveaux smartphones ou produits high-tech s’enchaînent à un rythme de plus en plus soutenu.
L’annonce <strong>{title}</strong> s’inscrit dans cette logique, mais avec des spécificités qui peuvent impacter
le marché (prix, fonctionnalités, intégration à l’écosystème, innovation réelle ou perçue).
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
La question centrale est de savoir si ce produit apporte une vraie différenciation ou s’il s’agit surtout
d’un rafraîchissement incrémental. Dans un marché saturé, la capacité à proposer une expérience utilisateur
clairement supérieure devient un facteur critique.
</p>

<h2>{h2_impacts}</h2>
<p>
Du côté des utilisateurs, ce type de lancement peut générer un renouvellement anticipé, un changement de marque,
ou au contraire une attitude d’attente si la proposition de valeur n’est pas jugée suffisante.
</p>

<h2>{h2_market}</h2>
<p>
Pour les concurrents, ce lancement peut entraîner des ajustements de prix, des campagnes marketing ciblées
ou l’accélération d’un futur lancement pour rester dans la course.
</p>

<h2>{h2_conclusion}</h2>
<p>
Au-delà de l’effet d’annonce, l’impact réel de <strong>{title}</strong> dépendra de l’accueil des utilisateurs
et des tests indépendants. C’est ce qui permettra de dire si ce produit marque réellement une rupture
ou s’il reste une évolution parmi d’autres.
</p>
"""
    elif template_id == 6:
        # Modèle "frameworks / dev / cloud"
        body = f"""
<h1>{final_title}</h1>

<h2>Une mise à jour qui concerne directement les développeurs</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une nouvelle version de framework, librairie ou plateforme cloud.</li>
  <li>Des fonctionnalités qui peuvent simplifier le travail au quotidien.</li>
  <li>Des changements parfois incompatibles avec les versions précédentes.</li>
  <li>Une nécessité de planifier les migrations avec rigueur.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Entre les nouvelles versions d’Angular, React, Vue, Flutter ou les évolutions majeures des services cloud,
les équipes de développement doivent arbitrer en permanence entre stabilité et adoption des nouveautés.
L’annonce <strong>{title}</strong> vient s’ajouter à cette liste de décisions techniques stratégiques.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
L’enjeu n’est pas seulement fonctionnel. Il touche aussi à la maintenabilité, à la performance, à la sécurité,
au coût d’hébergement, et à l’attractivité du stack technologique pour recruter des talents.
</p>

<h2>{h2_impacts}</h2>
<p>
Adopter trop vite une nouvelle version peut exposer à des bugs ou à l’absence de certaines dépendances.
Adopter trop tard peut compliquer les migrations, réduire la compatibilité et diminuer la compétitivité.
Tout l’enjeu est de trouver le bon timing.
</p>

<h2>{h2_market}</h2>
<p>
Les choix de frameworks et de plateformes sont de plus en plus scrutés par les clients, les développeurs
et les partenaires. Ils influencent la perception de modernité, de fiabilité et de scalabilité des solutions.
</p>

<h2>{h2_conclusion}</h2>
<p>
Pour rester compétitives, les équipes doivent mettre en place une veille structurée, tester les nouveautés
dans des environnements contrôlés et planifier leurs migrations avec méthode. L’annonce <strong>{title}</strong>
est une pièce de plus dans ce puzzle technique et stratégique.
</p>
"""
    elif template_id == 7:
        # Modèle "voitures électriques / industrie"
        body = f"""
<h1>{final_title}</h1>

<h2>Une annonce qui confirme la montée en puissance des véhicules électriques</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une offre de plus en plus riche en modèles et en gammes.</li>
  <li>Des enjeux autour de l’autonomie, de la recharge et du coût total de possession.</li>
  <li>Une pression forte sur les constructeurs historiques.</li>
  <li>Des liens étroits avec les avancées en IA, batterie et cloud.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Le marché des véhicules électriques se structure rapidement, entre innovations technologiques, contraintes
réglementaires et attentes des consommateurs. L’annonce <strong>{title}</strong> vient s’inscrire dans une compétition
intense où chaque constructeur tente de se différencier.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Au-delà de la fiche technique, l’enjeu est de comprendre le positionnement de ce nouveau modèle ou de cette
nouvelle technologie dans l’écosystème global. Autonomie, recharge, software, mises à jour OTA, services connectés,
expérience utilisateur&nbsp;: tout compte.
</p>

<h2>{h2_impacts}</h2>
<p>
Pour les consommateurs, cela signifie davantage de choix et potentiellement une amélioration du rapport qualité-prix.
Pour les constructeurs, cela implique des investissements lourds et des arbitrages industriels complexes.
</p>

<h2>{h2_market}</h2>
<p>
Les annonces successives des constructeurs montrent que le marché entre dans une phase de consolidation
où seules les offres les plus convaincantes sur l’ensemble du cycle de vie auront une place durable.
</p>

<h2>{h2_conclusion}</h2>
<p>
Cette actualité illustre une tendance lourde&nbsp;: l’électrification du parc automobile ne fait que commencer
et va s’accélérer. Les acteurs qui maîtriseront à la fois la technologie, l’industrialisation et les services associés
seront les grands gagnants de cette transition.
</p>
"""
    else:
        # Modèle "guerre des géants de la tech"
        body = f"""
<h1>{final_title}</h1>

<h2>Une nouvelle manche dans la guerre des géants de la tech</h2>
<p>{intro_html}</p>

<h2>{h2_points}</h2>
<ul>
  <li>Une lutte d’influence entre acteurs comme Google, Apple, Microsoft, Amazon, Meta ou NVIDIA.</li>
  <li>Des annonces coordonnées autour de l’IA, du cloud, des smartphones, des services et de la pub en ligne.</li>
  <li>Des enjeux de souveraineté numérique et de régulation.</li>
  <li>Une compétition pour attirer les meilleurs ingénieurs et chercheurs.</li>
</ul>

<h2>Résumé de l’annonce</h2>
{resume_html}

<h2>{h2_context}</h2>
<p>
Depuis plusieurs années, les grandes entreprises technologiques structurent une grande partie de l’innovation mondiale.
Chaque annonce comme <strong>{title}</strong> doit être lue à l’aune de cette compétition globale, où chaque avancée
ou partenariat peut faire bouger les lignes.
</p>
<p>{angle_block}</p>

<h2>{h2_analysis}</h2>
<p>
Cette actualité montre que la bataille ne se joue pas uniquement sur un produit isolé, mais sur des écosystèmes complets&nbsp;:
terminaux, OS, cloud, IA, services, publicité, contenu, données. Les acteurs qui parviennent à tout intégrer
gagnent en puissance et en capacité de verrouillage.
</p>

<h2>{h2_impacts}</h2>
<p>
Pour les utilisateurs, cela peut se traduire par des expériences plus fluides, mais aussi par une dépendance
plus forte à certains écosystèmes fermés. Pour les régulateurs, ces announcements posent des questions
sur la concurrence, la transparence et l’utilisation des données.
</p>

<h2>{h2_market}</h2>
<p>
Les réactions des marchés financiers, des analystes et des concurrents permettent souvent de mesurer
la portée réelle de ce type d’annonce. C’est un indicateur précieux pour anticiper les prochains mouvements.
</p>

<h2>{h2_conclusion}</h2>
<p>
L’annonce <strong>{title}</strong> est une pièce supplémentaire sur l’échiquier de la tech mondiale. 
La suivre, l’analyser et la replacer dans un ensemble plus vaste est indispensable pour comprendre 
où va réellement le secteur dans les prochaines années.
</p>
"""

    # Ajout bloc FAQ + mots-clés
    faq_html = build_faq_html(topic, main_kw)

    # Ajout de la source (lien unique, utile, en nouvel onglet)
    source_html = ""
    if source:
        source_html = f"""
<h2>Source principale de l’information</h2>
<p>
  <a href="{source}" target="_blank" rel="noopener nofollow">
    Consulter la source d’origine (article complet)
  </a>
</p>
"""

    full_html = f"""
{body}
{source_html}
{faq_html}
"""

    safe_title = slugify(final_title)
    filename = os.path.join(OUTPUT_DIR, f"{safe_title}.html")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✔️ Article généré (template {template_id}) :", filename)

# Envoi vers WordPress
publish_article(final_title, full_html)

# ===========================
# MAIN
# ===========================

def main():
    clean_output_dir()

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
