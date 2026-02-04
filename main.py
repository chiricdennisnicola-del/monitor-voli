import requests
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def test_ryanair():
    url = "https://www.ryanair.com/api/farfinder/v4/roundTripFares"
    params = {
        "departureAirportIataCode": "BGY",
        "arrivalAirportIataCode": "FUE",
        "outboundDepartureDateFrom": "2026-03-01",
        "outboundDepartureDateTo": "2026-06-01",
        "inboundDepartureDateFrom": "2026-03-01",
        "inboundDepartureDateTo": "2026-06-01",
        "durationMinimumDays": 2,
        "durationMaximumDays": 15,
        "language": "it",
        "market": "it-it"
    }
    
    print("Inviando richiesta a Ryanair...")
    try:
        res = requests.get(url, params=params, timeout=10)
        print(f"Stato risposta: {res.status_code}")
        
        data = res.json()
        offerte = data.get('fares', [])
        
        print(f"Numero di offerte trovate: {len(offerte)}")
        
        if len(offerte) > 0:
            primo = offerte[0]
            prezzo = primo['outbound']['price']['value'] + primo['inbound']['price']['value']
            msg = f"✅ L'API funziona! Trovato volo a {prezzo}€"
            invia_telegram(msg)
        else:
            invia_telegram("❌ L'API risponde ma non trova voli con questi filtri.")
            
    except Exception as e:
        errore_msg = f"🔥 Errore API: {str(e)}"
        print(errore_msg)
        invia_telegram(errore_msg)

def invia_telegram(testo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": testo})

if __name__ == "__main__":
    test_ryanair()