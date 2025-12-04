# Django Flight Booking (Amadeus integration)

Simple Django app for searching and booking flights using the Amadeus API (sandbox). If Amadeus credentials are not provided the app will fall back to a mock response for development.

Prerequisites
- Python 3.10+ (recommended)
- Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Setup
1. Copy `.env.example` to `.env` and fill in your Amadeus `AMADEUS_CLIENT_ID` and `AMADEUS_CLIENT_SECRET`. If you want to use mock results, leave them empty.
2. Run migrations:

```powershell
python manage.py migrate
```

3. Run development server:

```powershell
python manage.py runserver
```

4. Open `http://127.0.0.1:8000/` to access the `Search Flight` page.

Notes
- The project uses the Amadeus test (sandbox) endpoints. Generate test credentials at https://developers.amadeus.com/ and set them in `.env`.
- This scaffold focuses on the core flows: Search -> Flight Results -> Booking.
