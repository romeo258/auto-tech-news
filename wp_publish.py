import base64
import requests
import os

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASS = os.getenv("WP_APP_PASS")

API_ENDPOINT = f"{WP_URL}/wp-json/wp/v2/posts"

def publish_article(title, content, status="draft"):
    auth = f"{WP_USER}:{WP_APP_PASS}"
    token = base64.b64encode(auth.encode())
    headers = {
        "Authorization": f"Basic {token.decode('utf-8')}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": title,
        "content": content,
        "status": "draft"   # FORCÉ EN BROUILLON
    }

    response = requests.post(API_ENDPOINT, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print(f"✔ Brouillon créé dans WordPress : {title}")
    else:
        print("❌ Erreur création brouillon :", response.status_code, response.text)
