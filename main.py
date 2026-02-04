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
        "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
        "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
        "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
    }
    
    # Prende l'anno e il mese corrente
    oggi = datetime.now()
    anno_corrente = oggi.year
    mese_corrente = oggi.month

    try:
        res = requests.get(url).json()
        if res["result"]:
            messaggi = [m for m in res["result"] if "message" in m and "text" in m["message"]]
            if messaggi:
                testo = messaggi[-1]["message"]["text"].lower()
                numeri = re.findall(r'\d+', testo)
                durata = int(numeri[0]) if numeri else 7
                
                mese_scelto = 6 # Default Giugno
                for nome, numero in mesi_ita.items():
                    if nome in testo:
                        mese_scelto = numero
                        break
                
                # LOGICA ANNO AUTOMATICO:
                # Se il mese scelto è già passato quest'anno, cerca per l'anno prossimo
                if mese_scelto < mese_corrente:
                    anno_ricerca = anno_corrente + 1
                else:
                    anno_ricerca = anno_corrente
                
                return durata, mese_scelto, anno_ricerca
    except:
        pass
    return 7, 6, anno_corrente

def cerca_voli():
    durata, mese, anno = interpreta_messaggio()
    
    # Impostiamo la ricerca per il 10 del mese scelto
    data_andata = datetime(anno, mese, 10)
    data_ritorno = data_andata + timedelta(days=durata)
    
    out_str = data_andata.strftime("%Y-%m-%d")
    ret_str = data_ritorno.strftime("%Y-%m-%d")
    
    print(f"✈️ Ricerca Automatica: {durata} giorni nel periodo {mese}/{anno}")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": "MIL",
        "arrival_id": "FUE",
        "outbound_date": out_str,
        "return_date": ret_str,
        "currency": "EUR",
        "hl": "it",
        "api_key": SERPAPI_KEY,
        "stops": "0" 
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        voli = data.get('best_flights', []) or data.get('other_flights', [])
        
        if not voli:
            invia_telegram(f"⚠️ Nessun volo trovato per {durata} gg a {mese}/{anno}. Prova un altro mese!")
            return

        for volo in voli[:3]:
            prezzo = volo.get('price', 'N/A')
            t = volo['flights']
            
            msg = (
                f"✈️ **OFFERTA {durata} GIORNI ({anno})**\n\n"
                f"💰 Prezzo: {prezzo}€\n"
                f"🏢 Compagnia: {t[0]['airline']}\n"
                f"📅 Partenza: {t[0]['departure_airport']['time']}\n"
                f"📅 Ritorno: {t[-1]['departure_airport']['time']}\n\n"
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