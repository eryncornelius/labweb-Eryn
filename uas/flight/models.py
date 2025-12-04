from django.db import models

class FlightOffer(models.Model):
    flight_id = models.CharField(max_length=200, unique=True)
    airline = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    
    depart_date = models.DateField() 
    return_date = models.DateField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return f"{self.airline} - {self.departure} to {self.arrival} ({self.depart_date})"

class Booking(models.Model):
    flight_offer = models.ForeignKey(
        FlightOffer, 
        on_delete=models.CASCADE, 
        related_name='bookings')
    passenger_name = models.CharField(max_length=200)
    passport_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger_name} booked {self.flight_offer.airline} - {self.flight_offer.flight_id}"