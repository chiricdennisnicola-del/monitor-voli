import os
import requests
from datetime import datetime

SERPAPI_KEY = os.getenv('SERPAPI_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def leggi_range_da_chat():
    """Legge l'ultimo messaggio per impostare il periodo di ricerca"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        res = requests.get(url).json()
        if res["result"]:
            # Prende l'ultimo messaggio di testo inviato al bot
            messaggi = [m for m in res["result"] if "message" in m and "text" in m["message"]]
            if messaggi:
                testo = messaggi[-1]["message"]["text"]
                # Formato atteso: "2026-06-01, 2026-07-31"
                if "," in testo:
                    date = testo.replace(" ", "").split(",")
                    return date[0], date[1]
    except:
        pass
    # Date di default se non scrivi nulla o c'è un errore
    return "2026-03-01", "2026-03-31"

def cerca_voli_smart():
    data_inizio, data_fine = leggi_range_da_chat()
    print(f"🔍 Cerco la migliore combinazione tra {data_inizio} e {data_fine}")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": "MIL",
        "arrival_id": "FUE",
        "outbound_date": data_inizio,
        "return_date": data_fine,
        "currency": "EUR",
        "hl": "it",
        "api_key": SERPAPI_KEY,
        "type": "1" # Modalità ricerca smart/best
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    # Google Flights restituisce i voli più convenienti in questo range
    offerte = data.get('best_flights', [])
    
    if not offerte:
        print("Nessun volo trovato in questo range.")
        return

    # Mandiamo i primi 2 risultati (i più 'smart')
    for volo in offerte[:2]:
        prezzo = volo['price']
        tratta = volo['flights']
        data_a = tratta[0]['departure_airport']['time'].split(' ')[0]
        # Il ritorno è l'ultima tratta del pacchetto
        data_r = tratta[-1]['departure_airport']['time'].split(' ')[0]
        
        msg = (
            f"🎯 **MIGLIOR COMBINAZIONE TROVATA**\n\n"
            f"💰 Prezzo Totale: {prezzo}€\n"
            f"📅 Andata: {data_a}\n"
            f"📅 Ritorno: {data_r}\n"
            f"🛫 Aeroporto: {tratta[0]['departure_airport']['name']}\n"
            f"🔗 [Apri su Google Flights](https://www.google.com/travel/flights)"
        )
        invia_telegram(msg)

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_voli_smart()