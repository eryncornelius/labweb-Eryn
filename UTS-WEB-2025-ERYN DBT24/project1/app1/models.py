from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))

class ProfileStudent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nim = models.CharField(max_length=20, unique=True)
    program_studi = models.CharField(max_length=100)
    angkatan = models.CharField(max_length=10)
    jenis_kelamin = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=False)
    wa = models.CharField(max_length=20, blank=True)
    bukti_konsultasi = models.FileField(upload_to="documents/konsultasi/", blank=True, null=True)
    bukti_sptjm = models.FileField(upload_to="documents/sptjm/", blank=True, null=True)
    cv = models.FileField(upload_to="documents/cv/", blank=True, null=True)
    portofolio = models.FileField(upload_to="documents/portfolio/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.nim})"


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    bidang_usaha = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"

class InternshipConfirmation(models.Model):
    student = models.ForeignKey(ProfileStudent, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    posisi = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    alamat_perusahaan = models.TextField(blank=True)
    bidang_usaha = models.CharField(max_length=255, blank=True)
    nama_supervisor = models.CharField(max_length=255)
    email_supervisor = models.EmailField()
    wa_supervisor = models.CharField(max_length=50, blank=True)
    surat_penerimaan = models.FileField(upload_to="documents/surat_penerimaan/")
    date_confirmed = models.DateTimeField(auto_now_add=True)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"Konfirmasi {self.student} - {self.company}"

class MonthlyReport(models.Model): 
    confirmation = models.ForeignKey(InternshipConfirmation, on_delete=models.CASCADE) 
    month = models.CharField(max_length=20) 
    profil_perusahaan = models.TextField() 
    jobdesk = models.TextField() 
    suasana = models.TextField() 
    manfaat_dari_perkuliahan = models.TextField() 
    kekurangan_pembelajaran = models.TextField() 
    date_created = models.DateTimeField(auto_now_add=True) 
    
    class Meta: 
        unique_together = ('confirmation', 'month') 
    
class SupervisorEvaluation(models.Model): 
    confirmation = models.ForeignKey(InternshipConfirmation, on_delete=models.CASCADE) 
    supervisor_name = models.CharField(max_length=255) 
    email = models.EmailField() 
    filled = models.BooleanField(default=False) 
    score = models.IntegerField(null=True, blank=True) 
    comments = models.TextField(blank=True) 
    date_filled = models.DateTimeField(null=True, blank=True)

class Certificate(models.Model):
    student = models.ForeignKey(ProfileStudent, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    nilai_konversi = models.CharField(max_length=50, blank=True)
    date_issued = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sertifikat {self.student} - {self.company}"
    
class Confirmation(models.Model):
    student = models.ForeignKey(ProfileStudent, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    
class FinalReport(models.Model):
    confirmation = models.OneToOneField(InternshipConfirmation, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/final_reports/")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laporan Akhir {self.confirmation.student.user.get_full_name()} - {self.confirmation.company}"