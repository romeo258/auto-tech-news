import base64
import requests
import os

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

API_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/posts"

def publish_article(title, content, status="draft"):
    """
    Envoie un article en brouillon dans WordPress.
    - title : titre de l'article
    - content : contenu HTML
    - status : draft (toujours)
    """

    if not WP_URL or not WP_USER or not WP_APP_PASS:
        print("❌ Erreur : variables WordPress (WP_URL, WP_USER, WP_APP_PASS) manquantes.")
        return False

    # Auth WP en Base64
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode("utf-8")

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": content,
        "status": "draft"  # Toujours brouillon
    }

    try:
        response = requests.post(API_ENDPOINT, json=payload, headers=headers)
    except Exception as e:
        print("❌ Erreur de connexion à WordPress :", str(e))
        return False

    if response.status_code in [200, 201]:
        print(f"✔ Brouillon créé dans WordPress : {title}")
        return True
    else:
        print("❌ Erreur lors de la création du brouillon :")
        print("Code :", response.status_code)
        print("Réponse :", response.text)
        return False
