import os
import requests
import re

# Caricamento credenziali dai Secrets di GitHub
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def interpreta_messaggio():
    """Legge l'ultimo messaggio su Telegram per capire durata e mese"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    mesi_ita = {
        "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
        "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
        "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"
    }
    
    try:
        res = requests.get(url).json()
        if res["result"]:
            # Filtra solo i messaggi di testo
            messaggi = [m for m in res["result"] if "message" in m and "text" in m["message"]]
            if messaggi:
                testo = messaggi[-1]["message"]["text"].lower()
                print(f"Ultimo messaggio ricevuto: {testo}")
                
                # 1. Estrazione giorni (cerca numeri nel testo)
                numeri = re.findall(r'\d+', testo)
                durata = int(numeri[0]) if numeri else 7
                
                # 2. Estrazione mese
                mese_scelto = "06" # Default: Giugno
                for nome, numero in mesi_ita.items():
                    if nome in testo:
                        mese_scelto = numero
                        break
                
                return durata, mese_scelto
    except Exception as e:
        print(f"Errore nella lettura di Telegram: {e}")
    
    return 7, "06" # Fallback se la chat è vuota

def cerca_voli():
    durata, mese = interpreta_messaggio()
    anno = "2026"
    data_partenza_base = f"{anno}-{mese}-01"
    
    print(f"Ricerca avviata: {durata} giorni nel mese {mese}/{anno}")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": "MIL", # Malpensa, Linate, Bergamo
        "arrival_id": "FUE",     # Fuerteventura
        "outbound_date": data_partenza_base,
        "currency": "EUR",
        "hl": "it",
        "api_key": SERPAPI_KEY,
        "type": "1" # Modalità 'Migliori voli'
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            print(f"Errore API: {data['error']}")
            return

        offerte = data.get('best_flights', [])
        if not offerte:
            invia_telegram(f"🧐 Nessun volo 'Best' trovato per {durata} giorni a {mese}/{anno}. Prova a cambiare mese!")
            return

        # Invio delle migliori 3 opzioni
        for volo in offerte[:3]:
            prezzo = volo['price']
            t = volo['flights']
            # Estrae date pulite
            d_andata = t[0]['departure_airport']['time']
            d_ritorno = t[-1]['departure_airport']['time']
            compagnia = t[0]['airline']

            msg = (
                f"✈️ **PROPOSTA TROVATA**\n\n"
                f"💰 Prezzo: {prezzo}€ (A/R)\n"
                f"🏢 Compagnia: {compagnia}\n"
                f"📅 Andata: {d_andata}\n"
                f"📅 Ritorno: {d_ritorno}\n\n"
                f"🔗 [Prenota su Google Flights](https://www.google.com/travel/flights)"
            )
            invia_telegram(msg)

    except Exception as e:
        print(f"Errore durante la ricerca: {e}")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_voli()