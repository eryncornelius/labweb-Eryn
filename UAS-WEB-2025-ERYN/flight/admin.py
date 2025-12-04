from django.contrib import admin
from .models import FlightOffer, Booking

@admin.register(FlightOffer)
class FlightOfferAdmin(admin.ModelAdmin):
    list_display = ('flight_id', 'airline', 'departure', 'arrival', 'depart_date', 'price')
    search_fields = ('flight_id', 'airline', 'departure', 'arrival')
    
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'get_flight_id', 'get_airline', 'get_depart_date', 'get_price', 'created_at')
    
    search_fields = ('passenger_name', 'flight_offer__flight_id', 'flight_offer__airline')
    
    def get_flight_id(self, obj):
        return obj.flight_offer.flight_id
    get_flight_id.short_description = 'Flight ID'

    def get_airline(self, obj):
        return obj.flight_offer.airline
    get_airline.short_description = 'Airline'

    def get_depart_date(self, obj):
        return obj.flight_offer.depart_date
    get_depart_date.short_description = 'Departure Date'
    
    def get_price(self, obj):
        return f"${obj.flight_offer.price:.2f}"
    get_price.short_description = 'Price'