import os
import requests

# Configurazioni da GitHub Secrets
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def cerca_offerte_smart():
    url = "https://serpapi.com/search"
    
    # Parametri ottimizzati per trovare il prezzo più basso nel mese
    params = {
        "engine": "google_flights",
        "departure_id": "MIL",    # Cerca MXP, BGY, LIN insieme
        "arrival_id": "FUE",      # Fuerteventura
        "outbound_date": "2026-03-14", # Data indicativa di partenza
        "return_date": "2026-03-21",   # Data indicativa di ritorno
        "currency": "EUR",
        "hl": "it",
        "gl": "it",               # Risultati dal mercato italiano
        "api_key": SERPAPI_KEY,
        "type": "1"               # Forza la ricerca dei voli migliori
    }

    try:
        print(f"Uso la chiave API: {SERPAPI_KEY[:5]}***") # Stampa solo l'inizio per sicurezza
        response = requests.get(url, params=params)
        print(f"Stato Risposta: {response.status_code}")
        
        data = response.json()
        
        # Se c'è un errore nei parametri o nella chiave, SerpApi lo scrive qui:
        if "error" in data:
            print(f"Errore SerpApi: {data['error']}")
            return

    except Exception as e:
        print(f"Errore: {e}")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_offerte_smart()