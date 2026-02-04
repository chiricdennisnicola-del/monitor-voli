import requests
import os

print("--- INIZIO SCRIPT ---")

def test():
    # Proviamo una ricerca super semplice: Bergamo -> Fuerteventura a Marzo
    url = "https://www.ryanair.com/api/farfinder/v4/roundTripFares"
    params = {
        "departureAirportIataCode": "BGY",
        "arrivalAirportIataCode": "FUE",
        "outboundDepartureDateFrom": "2026-03-01",
        "outboundDepartureDateTo": "2026-03-31",
        "inboundDepartureDateFrom": "2026-03-01",
        "inboundDepartureDateTo": "2026-03-31",
        "durationMinimumDays": 3,
        "durationMaximumDays": 15,
        "language": "it",
        "market": "it-it"
    }
    
    print(f"Sto interrogando Ryanair con questi parametri...")
    res = requests.get(url, params=params)
    print(f"Risposta del server: {res.status_code}")
    
    voli = res.json().get('fares', [])
    print(f"Voli trovati: {len(voli)}")
    
    if len(voli) > 0:
        prezzo = voli[0]['outbound']['price']['value'] + voli[0]['inbound']['price']['value']
        print(f"Esempio prezzo trovato: {prezzo}€")

test()
print("--- FINE SCRIPT ---")