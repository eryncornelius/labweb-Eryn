from django import forms
from django.contrib.auth.models import User
from .models import ProfileStudent, InternshipConfirmation, MonthlyReport, FinalReport
from django.contrib.auth.forms import AuthenticationForm

class UserSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            }

class ProfileStudentForm(forms.ModelForm):
    jenis_kelamin = forms.ChoiceField(
        choices=ProfileStudent._meta.get_field('jenis_kelamin').choices,
        required=True,
        label="Jenis Kelamin"
    )
    class Meta:
        model = ProfileStudent
        exclude = ("user", "date_created",)
        labels = {
            "nim": "NIM",
            "program_studi": "Program Studi",
            "angkatan": "Angkatan",
            "jenis_kelamin": "Jenis Kelamin",
            "wa": "WA",
            "bukti_konsultasi": "Bukti Konsultasi",
            "bukti_sptjm": "Bukti SPTJM",
            "cv": "CV",
            "portofolio": "Portofolio",
        }

class InternshipConfirmationForm(forms.ModelForm):
    class Meta:
        model = InternshipConfirmation
        exclude = ("student","date_confirmed","is_reported")
        labels = {
            "start": "Periode Mulai",
            "end": "Periode Selesai",
            "posisi": "Posisi Magang",
            "company": "Nama Perusahaan",
            "alamat_perusahaan": "Alamat Perusahaan",
            "bidang_usaha": "Bidang Usaha Perusahaan",
            "nama_supervisor": "Nama Supervisor",
            "email_supervisor": "Email Supervisor",
            "wa_supervisor": "WA Supervisor",
            "surat_penerimaan": "Surat Penerimaan Magang",
        }

class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        exclude = ("confirmation", "date_created")
        labels = {
            "month": "Bulan/Minggu Laporan",
            "profil_perusahaan": "Profil Perusahaan",
            "jobdesk": "Jobdesk",
            "suasana": "Suasana Lingkungan Pekerjaan",
            "manfaat_dari_perkuliahan": "Manfaat dari Perkuliahan",
            "kekurangan_pembelajaran": "Kekurangan Pembelajaran",
        }

class MyLoginForm(AuthenticationForm):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(email__iexact=username)
                self.cleaned_data['username'] = user.username 
            except User.DoesNotExist:
                pass
                
        return super().clean()
    
class FinalReportForm(forms.ModelForm):
    class Meta:
        model = FinalReport
        fields = ["file"]
        labels = {
            "file": "Upload Laporan Akhir"
        }
