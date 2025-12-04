import os
import time
import requests

AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID')
AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')

TOKEN_URL = 'https://test.api.amadeus.com/v1/security/oauth2/token'
FLIGHT_OFFERS_URL = 'https://test.api.amadeus.com/v2/shopping/flight-offers'

_token_cache = {'access_token': None, 'expires_at': 0}


def _get_token():
    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        return None
    now = time.time()
    if _token_cache['access_token'] and _token_cache['expires_at'] > now + 10:
        return _token_cache['access_token']

    resp = requests.post(TOKEN_URL, data={
        'grant_type': 'client_credentials',
        'client_id': AMADEUS_CLIENT_ID,
        'client_secret': AMADEUS_CLIENT_SECRET,
    })
    resp.raise_for_status()
    data = resp.json()
    _token_cache['access_token'] = data['access_token']
    _token_cache['expires_at'] = now + data.get('expires_in', 1800)
    return _token_cache['access_token']


def search_flights(origin, destination, depart_date, return_date=None, adults=1):
    """Return a list of flight offers. If no Amadeus credentials are set, return a mock sample."""
    if not AMADEUS_CLIENT_ID or not AMADEUS_CLIENT_SECRET:
        # Mock sample data for development
        return [
            {
                'id': 'MOCK-1',
                'airline': 'MockAir',
                'departure': origin,
                'arrival': destination,
                'depart_date': str(depart_date),
                'return_date': str(return_date) if return_date else '',
                'price': 'USD 120.00',
                'details': '1 stop · 5h 12m',
            },
            {
                'id': 'MOCK-2',
                'airline': 'Example Airways',
                'departure': origin,
                'arrival': destination,
                'depart_date': str(depart_date),
                'return_date': str(return_date) if return_date else '',
                'price': 'USD 220.00',
                'details': 'Nonstop · 2h 10m',
            },
        ]

    token = _get_token()
    if not token:
        return []

    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': depart_date,
        'adults': adults,
        'max': 10,
    }
    if return_date:
        params['returnDate'] = return_date

    r = requests.get(FLIGHT_OFFERS_URL, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
    offers = []
    # Simplify the Amadeus response into our minimal structure
    for idx, item in enumerate(data.get('data', [])):
        price = item.get('price', {}).get('total', 'N/A')
        offers.append({
            'id': item.get('id', f'R{idx}'),
            'airline': item.get('validatingAirlineCodes', [''])[0],
            'departure': origin,
            'arrival': destination,
            'depart_date': depart_date,
            'return_date': return_date or '',
            'price': f"USD {price}",
            'details': 'See provider',
        })
    return offers
