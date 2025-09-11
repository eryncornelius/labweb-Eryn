
from django.urls import include, path 
from django.contrib import admin

urlpatterns = [
    path('', include('app1.urls')),
    path('admin/', admin.site.urls)
    
    ]