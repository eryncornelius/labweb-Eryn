from django import forms

class SearchForm(forms.Form):
    origin = forms.CharField(label='Origin (city)', max_length=100)
    destination = forms.CharField(label='Destination (city)', max_length=100)
    depart_date = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    return_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))

class BookingForm(forms.Form):
    passenger_name = forms.CharField(max_length=200)
    passport_number = forms.CharField(max_length=100)