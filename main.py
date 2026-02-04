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
        print("Interrogando Google Flights via SerpApi...")
        response = requests.get(url, params=params)
        data = response.json()
        
        # Prendiamo i "Migliori voli" (Best Flights)
        voli = data.get('best_flights', [])
        
        if not voli:
            # Se non ci sono 'best', proviamo gli 'altri' voli economici
            voli = data.get('other_flights', [])

        if not voli:
            print("Nessun volo trovato.")
            return

        # Mandiamo solo i primi 2 risultati (i più economici e veloci)
        for volo in voli[:2]:
            prezzo = volo['price']
            tratte = volo['flights']
            
            # Info volo andata
            partenza_nome = tratte[0]['departure_airport']['name']
            aereo_codice = tratte[0]['departure_airport']['id']
            compagnia = tratte[0]['airline']
            
            msg = (
                f"✈️ **GOOGLE FLIGHTS: MIGLIOR PREZZO**\n\n"
                f"💰 Prezzo Totale: {prezzo}€\n"
                f"🛫 Da: {partenza_nome} ({aereo_codice})\n"
                f"🏢 Compagnia: {compagnia}\n"
                f"📅 Andata/Ritorno trovati per le date selezionate.\n\n"
                f"🔗 [Vedi su Google Flights](https://www.google.com/travel/flights?q=Flights%20to%20FUE%20from%20MIL)"
            )
            invia_telegram(msg)

    except Exception as e:
        print(f"Errore: {e}")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_offerte_smart()