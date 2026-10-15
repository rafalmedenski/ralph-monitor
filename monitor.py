import os
import json
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
URL = "https://www.ralphlauren.eu/pl/en/private-store/21011"
STATE_FILE = "known_products.json"

def send_discord(new_items):
    if not DISCORD_WEBHOOK_URL:
        print("Brak webhooka!")
        return
    
    for item in new_items:
        msg = f"🚨 **NOWY PRODUKT W PRIVATE STORE RALPH LAUREN!** 🚨\n\n"
        msg += f"📦 **{item['title']}**\n"
        msg += f"🔗 [Zobacz produkt]({item['url']})\n"

        payload = {"content": msg}
        requests.post(DISCORD_WEBHOOK_URL, json=payload)

def load_known_products():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except:
                pass
    return set()

def save_known_products(products_set):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(products_set), f, ensure_ascii=False, indent=2)

def main():
    print(f"Sprawdzam stronę: {URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Błąd HTTP: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        seen_links = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/p/' in href or 'product' in href:
                if not href.startswith('http'):
                    href = "https://www.ralphlauren.eu" + href
                
                title = a.get_text(strip=True)
                if not title or len(title) < 3:
                    title = "Produkt Ralph Lauren"

                if href not in seen_links:
                    seen_links.add(href)
                    products.append({"url": href, "title": title[:100]})

        print(f"Znaleziono łącznie linków produktów: {len(products)}")

        known = load_known_products()
        current_urls = {p['url'] for p in products}

        if not known:
            print("Pierwsze uruchomienie – zapisuję bazę aktualnych produktów bez wysyłania powiadomień.")
            save_known_products(current_urls)
            return

        new_urls = current_urls - known
        new_items = [p for p in products if p['url'] in new_urls]

        if new_items:
            print(f"Wykryto {len(new_items)} nowych produktów! Wysyłam powiadomienia...")
            send_discord(new_items)
            known.update(current_urls)
            save_known_products(known)
        else:
            print("Brak nowych produktów.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()
