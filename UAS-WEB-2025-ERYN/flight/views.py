from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SearchForm, BookingForm
from . import amadeus_client
from .models import Booking, FlightOffer
from django.http import JsonResponse
from amadeus import Client, ResponseError
from datetime import datetime
from decimal import Decimal, InvalidOperation

amadeus = Client(
    client_id='kTKwqYMbRvGICwAMPDXAKVWN5NaYGpVv',
    client_secret='epQl9tAOWOOTiz4w'
)

def index(request):
    form = SearchForm(request.GET or None)
    return render(request, 'flights/search.html', {'form': form})


def results(request):
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            origin = form.cleaned_data['origin']
            destination = form.cleaned_data['destination']
            depart_date = form.cleaned_data['depart_date']
            return_date = form.cleaned_data.get('return_date')
            offers = amadeus_client.search_flights(origin, destination, depart_date, return_date)
            return render(request, 'flights/results.html', {'offers': offers, 'form': form})
    return redirect('index')


def book(request, offer_id):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            flight_id = request.POST.get('flight_id')
            airline = request.POST.get('airline')
            departure = request.POST.get('departure')
            arrival = request.POST.get('arrival')
            depart_date = request.POST.get('depart_date')
            return_date = request.POST.get('return_date')
            price = request.POST.get('price')

            flight_offer, created = FlightOffer.objects.get_or_create(
                flight_id=flight_id,
                defaults={
                    'airline': airline,
                    'departure': departure,
                    'arrival': arrival,
                    'depart_date': depart_date,
                    'return_date': return_date if return_date else None,
                    'price': price.replace('USD ', '') if price else 0,
                }
            )

            parsed_depart = None
            parsed_return = None
            if depart_date:
                try:
                    parsed_depart = datetime.fromisoformat(depart_date).date()
                except Exception:
                    parsed_depart = depart_date
            if return_date:
                try:
                    parsed_return = datetime.fromisoformat(return_date).date()
                except Exception:
                    parsed_return = return_date

            flight_offer.airline = airline
            flight_offer.departure = departure
            flight_offer.arrival = arrival
            if parsed_depart is not None:
                flight_offer.depart_date = parsed_depart
            flight_offer.return_date = parsed_return if parsed_return else None
            if price:
                price_clean = price.replace('USD ', '').replace('$', '').strip()
                try:
                    flight_offer.price = Decimal(price_clean)
                except (InvalidOperation, ValueError):
                    pass
            flight_offer.save()

            booking = Booking.objects.create(
                flight_offer=flight_offer,
                passenger_name=form.cleaned_data['passenger_name'],
                passport_number=form.cleaned_data['passport_number'],
            )
            return render(request, 'flights/booking_success.html', {'booking': booking})
    else:
        initial = {
            'passenger_name': '',
            'passport_number': '',
        }
        form = BookingForm(initial=initial)
        offer = {
            'id': offer_id,
            'airline': request.GET.get('airline', ''),
            'departure': request.GET.get('departure', ''),
            'arrival': request.GET.get('arrival', ''),
            'depart_date': request.GET.get('depart_date', ''),
            'return_date': request.GET.get('return_date', ''),
            'price': request.GET.get('price', ''),
        }
        return render(request, 'flights/booking.html', {'form': form, 'offer': offer})
