from django.db import models

# Create your models here.
class Mahasiswa(models.Model):
    nim = models.IntegerField(null=True, blank=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    jurusan = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.firstname} {self.lastname}"