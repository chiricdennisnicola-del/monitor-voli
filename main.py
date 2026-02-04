import requests
import os

# --- CONFIGURAZIONI ---
# Questi valori verranno presi in automatico da GitHub per sicurezza
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

AEROPORTI_MILANO = ["BGY", "MXP"]
DESTINAZIONE = "FUE"
BUDGET_MAX = 150  # Avvisami se il totale A/R è sotto i 150€

def cerca_voli():
    for origine in AEROPORTI_MILANO:
        url = "https://www.ryanair.com/api/farfinder/v4/roundTripFares"
        params = {
            "departureAirportIataCode": origine,
            "arrivalAirportIataCode": DESTINAZIONE,
            "outboundDepartureDateFrom": "2026-03-01",
            "outboundDepartureDateTo": "2026-07-01",
            "inboundDepartureDateFrom": "2026-03-01",
            "inboundDepartureDateTo": "2026-07-01",
            "durationMinimumDays": 4,
            "durationMaximumDays": 10,
            "language": "it",
            "market": "it-it"
        }
        
        try:
            res = requests.get(url, params=params)
            offerte = res.json().get('fares', [])
            
            for f in offerte:
                p_andata = f['outbound']['price']['value']
                p_ritorno = f['inbound']['price']['value']
                totale = p_andata + p_ritorno
                
                if totale <= BUDGET_MAX:
                    msg = (
                        f"✈️ **OFFERTA TROVATA!**\n\n"
                        f"💰 Prezzo Totale: {totale}€\n"
                        f"🛫 Da: {f['outbound']['departureAirport']['name']} ({origine})\n"
                        f"📅 Andata: {f['outbound']['departureDate'][:10]}\n"
                        f"📅 Ritorno: {f['inbound']['departureDate'][:10]}\n"
                        f"🔗 [Prenota su Ryanair](https://www.ryanair.com/it/it/)"
                    )
                    invia_telegram(msg)
        except Exception as e:
            print(f"Errore con {origine}: {e}")

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": messaggio, "parse_mode": "Markdown"})

if __name__ == "__main__":
    cerca_voli()