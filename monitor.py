import os
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
URL = "https://www.ralphlauren.eu/pl/en/private-store/21011"

def send_discord(products):
    if not DISCORD_WEBHOOK_URL:
        print("Brak webhooka!")
        return
    
    # Wyślij powiadomienie z podsumowaniem znalezionych produktów
    msg = f"🚨 **RALPH LAUREN PRIVATE STORE - RAPORT** 🚨\n\n"
    msg += f"Znaleziono łącznie **{len(products)}** produktów na stronie:\n"
    for item in products[:10]: # Pokazuje pierwsze 10
        msg += f"📦 [{item['title']}]({item['url']})\n"

    payload = {"content": msg}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

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

        if products:
            print("Wysyłam powiadomienie na Discorda...")
            send_discord(products)
        else:
            print("Brak produktów na stronie.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    main()
