from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import SearchForm, BookingForm
from . import amadeus_client
from .models import Booking


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
    # In a full app we'd fetch offer details from API or session. For now we accept offer_id and details via GET.
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # extract minimal info from POST hidden fields
            flight_id = request.POST.get('flight_id')
            airline = request.POST.get('airline')
            departure = request.POST.get('departure')
            arrival = request.POST.get('arrival')
            depart_date = request.POST.get('depart_date')
            return_date = request.POST.get('return_date')
            price = request.POST.get('price')

            booking = Booking.objects.create(
                flight_id=flight_id,
                airline=airline,
                departure=departure,
                arrival=arrival,
                depart_date=depart_date,
                return_date=return_date,
                price=price or '',
                passenger_name=form.cleaned_data['passenger_name'],
                passport_number=form.cleaned_data['passport_number'],
            )
            return render(request, 'flights/booking_success.html', {'booking': booking})
    else:
        # GET: show form prefilled with offer information passed as query params
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