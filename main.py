import os
import requests
import re
from datetime import datetime, timedelta

SERPAPI_KEY = os.getenv('SERPAPI_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def interpreta_messaggio():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    mesi_ita = {
        "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
        "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
        "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"
    }
    try:
        res = requests.get(url).json()
        if res["result"]:
            messaggi = [m for m in res["result"] if "message" in m and "text" in m["message"]]
            if messaggi:
                testo = messaggi[-1]["message"]["text"].lower()
                numeri = re.findall(r'\d+', testo)
                durata = int(numeri[0]) if numeri else 7
                mese_scelto = "06"
                for nome, numero in mesi_ita.items():
                    if nome in testo:
                        mese_scelto = numero
                        break
                return durata, mese_scelto
    except:
        pass
    return 7, "06"

def cerca_voli():
    durata, mese = interpreta_messaggio()
    anno = 2026
    
    # Calcolo date per l'API
    data_andata = datetime(anno, int(mese), 1)
    data_ritorno = data_andata + timedelta(days=durata)
    
    # Trasformiamo in testo formato YYYY-MM-DD
    out_str = data_andata.strftime("%Y-%m-%d")
    ret_str = data_ritorno.strftime("%Y-%m-%d")
    
    print(f"✈️ Cerco volo di {durata} giorni. Partenza indicativa: {out_str}, Ritorno: {ret_str}")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": "MIL",
        "arrival_id": "FUE",
        "outbound_date": out_str,
        "return_date": ret_str, # AGGIUNTO: ora l'API è contenta
        "currency": "EUR",
        "hl": "it",
        "api_key": SERPAPI_KEY,
        "type": "1"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "error" in data:
            print(f"Errore API: {data['error']}")
            return

        offerte = data.get('best_flights', [])
        if not offerte:
            invia_telegram(f"🧐 Nessun volo 'Best' trovato per {durata} giorni a {mese}/{anno}.")
            return

        for volo in offerte[:3]:
            msg = (
                f"✈️ **OFFERTA {durata} GIORNI**\n\n"
                f"💰 Prezzo: {volo['price']}€\n"
                f"🏢 Compagnia: {volo['flights'][0]['airline']}\n"
                f"📅 Andata: {volo['flights'][0]['departure_airport']['time']}\n"
                f"📅 Ritorno: {volo['flights'][-1]['departure_airport']['time']}\n\n"
                f"🔗 [Link Google Flights](https://www.google.com/travel/flights)"
            )
            invia_telegram(msg)
    except Exception as e:
        print(f"Errore: {e}")

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_voli()