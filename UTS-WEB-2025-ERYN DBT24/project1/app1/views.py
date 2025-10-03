from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
import datetime

from .forms import UserSignupForm, ProfileStudentForm, InternshipConfirmationForm, MonthlyReportForm, MyLoginForm, FinalReportForm
from .models import ProfileStudent, JobPosting, InternshipConfirmation, MonthlyReport, Company, Certificate, SupervisorEvaluation, Confirmation, FinalReport
from django.contrib.auth.models import User

def signup(request):
    if request.method == "POST":
        user_form = UserSignupForm(request.POST)
        profile_form = ProfileStudentForm(request.POST, request.FILES)
        
        raw_password = request.POST.get('password')
        user_email = request.POST.get('email')
        
        error = None
        
        if not user_email or not user_email.strip():
            error = "Alamat Email wajib diisi."
        elif not raw_password or not raw_password.strip():
            error = "Password wajib diisi."

        if error:
            return render(request, "signup.html", {
                "user_form": user_form, 
                "profile_form": profile_form,
                "error": error
            })
            
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            
            nim_as_username = profile_form.cleaned_data.get('nim')

            if not nim_as_username:
                return render(request, "signup.html", {
                    "user_form": user_form, 
                    "profile_form": profile_form,
                    "error": "NIM wajib diisi untuk pendaftaran."
                })
            
            if User.objects.filter(username__iexact=nim_as_username).exists():
                return render(request, "signup.html", {
                    "user_form": user_form, 
                    "profile_form": profile_form, 
                    "error": "NIM sudah terdaftar sebagai username. Gunakan NIM lain."
                })
            if User.objects.filter(email__iexact=user_email).exists():
                return render(request, "signup.html", {
                    "user_form": user_form, 
                    "profile_form": profile_form, 
                    "error": "Email sudah terdaftar. Gunakan Email lain."
                })


            user.username = nim_as_username     
            user.email = user_email.strip()
            user.set_password(raw_password)
            
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect("coop:dashboard")
    else:
        user_form = UserSignupForm()
        profile_form = ProfileStudentForm()
    
    return render(request, "signup.html", {"user_form": user_form, "profile_form": profile_form})

from django.contrib.auth.views import LoginView
class MyLoginView(LoginView):
    template_name = "login.html"
    authentication_form = MyLoginForm

@login_required
def dashboard(request):
    profile = ProfileStudent.objects.filter(user=request.user).first()
    
    if profile:
        confirmations = InternshipConfirmation.objects.filter(student=profile).order_by('-date_confirmed')
        
        first_confirmation = confirmations.first()
    else:
        confirmations = []
        first_confirmation = None

    active_conf_id = first_confirmation.id if first_confirmation else 0
    
    context = {
        "profile": profile, 
        "confirmations": confirmations,
        "active_conf_id": active_conf_id, 
    }
    
    return render(request, "dashboard.html", context)

@login_required
def job_list(request):
    jobs = JobPosting.objects.filter(is_active=True).order_by("-date_created")
    return render(request, "job_list.html", {"jobs": jobs})

@login_required
def confirm_internship(request):
    try:
        profile = ProfileStudent.objects.get(user=request.user) 
    except ProfileStudent.DoesNotExist:
        return redirect("coop:signup") 
    
    if request.method == "POST":
        form = InternshipConfirmationForm(request.POST, request.FILES)
        if form.is_valid():
            conf = form.save(commit=False)
            conf.student = profile
            conf.save()
            return redirect("coop:dashboard")
    else:
        form = InternshipConfirmationForm()
        
    return render(request, "internship_confirm.html", {"form": form})

@login_required
def monthly_report_create(request, conf_id):
    student_profile = get_object_or_404(ProfileStudent, user=request.user)

    try:
        confirmation = InternshipConfirmation.objects.get(
            id=conf_id,
            student=student_profile
        )
    except InternshipConfirmation.DoesNotExist:
        
        active_confirmation = InternshipConfirmation.objects.filter(student=student_profile).order_by('-date_confirmed').first()

        if active_confirmation:
            return redirect("coop:monthly_report_add", conf_id=active_confirmation.id)
        else:
            return redirect("coop:confirm_internship")
            
    if request.method == "POST":
        form = MonthlyReportForm(request.POST, request.FILES)
        month = request.POST.get("month")
        
        if MonthlyReport.objects.filter(confirmation=confirmation, month=month).exists():
            return render(request, "monthly_report_form.html", {
                "form": form,
                "confirmation": confirmation,
                "error": "Laporan untuk bulan ini sudah ada."
            })
            
        if form.is_valid():
            report = form.save(commit=False)
            report.confirmation = confirmation
            report.save()
            return redirect("coop:dashboard")
    else:
        form = MonthlyReportForm()

    return render(request, "monthly_report_form.html", {"form": form, "confirmation": confirmation})
def send_reminder(request):
    today = datetime.date.today()
    week = today.strftime("%U")
    messages = []

    students = ProfileStudent.objects.all()
    for s in students:
        confirmation = InternshipConfirmation.objects.filter(student=s).first()

        if not confirmation:
            msg = f"{s.user.get_full_name()} ({s.nim}) belum ada konfirmasi magang"
            messages.append(msg)

            send_mail(
                subject="Reminder Konfirmasi Magang",
                message=f"Halo {s.user.first_name}, jangan lupa lakukan konfirmasi penerimaan magang di sistem COOP. Anda wajib lapor tiap minggu jika melewati batas waktu untuk mendapatkan tempat magang.",
                from_email="noreply@coop.local",
                recipient_list=[s.user.email],
                fail_silently=True,
            )

            send_mail(
                subject="Mahasiswa Belum Konfirmasi Magang",
                message=f"Mahasiswa berikut belum melakukan konfirmasi magang: {s.user.get_full_name()} ({s.nim}).",
                from_email="noreply@coop.local",
                recipient_list=["kaprodi@prastiyamulya.ac.id", "mentor@prastiyamulya.ac.id"],
                fail_silently=True,
            )

        else:
            reported = MonthlyReport.objects.filter(
                confirmation=confirmation,
                month=week
            ).exists()

            if not reported:
                msg = f"{s.user.get_full_name()} ({s.nim}) belum isi laporan minggu ke-{week}"
                messages.append(msg)

                send_mail(
                    subject="Reminder Laporan Kemajuan Mingguan",
                    message=f"Halo {s.user.first_name}, segera isi laporan kemajuan magang (minggu ke-{week}) di sistem COOP.",
                    from_email="noreply@coop.local",
                    recipient_list=[s.user.email],
                    fail_silently=True,
                )

                send_mail(
                    subject="Mahasiswa Belum Lapor Mingguan",
                    message=f"Mahasiswa berikut belum mengisi laporan kemajuan mingguan (minggu ke-{week}): {s.user.get_full_name()} ({s.nim}).",
                    from_email="noreply@coop.local",
                    recipient_list=["kaprodi@kampus.ac.id", "mentor@kampus.ac.id"],
                    fail_silently=True,
                )
            else:
                messages.append(f"{s.user.get_full_name()} ({s.nim}) sudah konfirmasi & lapor minggu ini")

    return HttpResponse("<br>".join(messages))

@login_required
def send_evaluation_email(request, conf_id):
    confirmation = get_object_or_404(InternshipConfirmation, id=conf_id)
    
    evaluation, created = SupervisorEvaluation.objects.get_or_create(
        confirmation=confirmation,
        defaults={
            'supervisor_name': confirmation.nama_supervisor,
            'email': confirmation.email_supervisor,
        }
    )

    evaluation_link = f"https://coop.local/evaluation/{evaluation.id}/fill/"

    messages = []
    
    send_mail(
        subject="Evaluasi Program COOP Mahasiswa",
        message=f"""
Halo Bapak/Ibu {confirmation.nama_supervisor},

Mohon bantuannya untuk mengisi formulir evaluasi magang untuk mahasiswa kami,
{confirmation.student.user.get_full_name()} ({confirmation.student.nim}).

Link Evaluasi: {evaluation_link}

Terima kasih.
Unit COOP.
""",
        from_email="admin@coop.local",
        recipient_list=[confirmation.email_supervisor],
        fail_silently=True,
    )
    messages.append(f"Email evaluasi terkirim ke Supervisor {confirmation.nama_supervisor} ({confirmation.email_supervisor})")
    return HttpResponse("<br>".join(messages))

@login_required
def send_final_evaluation_report(request, conf_id):
    confirmation = get_object_or_404(InternshipConfirmation, id=conf_id)
    
    evaluations = SupervisorEvaluation.objects.filter(confirmation=confirmation)
    
    total_evaluasi = evaluations.count()
    evaluasi_selesai = evaluations.filter(filled=True).count()
    
    if total_evaluasi == 0:
        return HttpResponse("Tidak ada formulir evaluasi yang terdaftar untuk magang ini.")
        
    messages = []

    if evaluasi_selesai < total_evaluasi:
        pesan = f"Belum semua evaluasi Supervisor selesai. Status: {evaluasi_selesai}/{total_evaluasi} selesai."
        messages.append(pesan)
        return HttpResponse("<br>".join(messages))
        
    report_detail = f"Laporan Akhir/UTS Mahasiswa: {confirmation.student.user.get_full_name()} ({confirmation.student.nim})\n"
    report_detail += f"Perusahaan: {confirmation.company}\n\n"
    
    for eval_item in evaluations:
        report_detail += f"Supervisor: {eval_item.supervisor_name} ({eval_item.email})\n"
        report_detail += f"Score: {eval_item.score if eval_item.score is not None else 'N/A'}\n"
        report_detail += f"Komentar: {eval_item.comments if eval_item.comments else '-'}\n---\n"
        
    messages.append("Semua evaluasi selesai.")
    messages.append("Simulasi Download Hasil Evaluasi (Isi Laporan):<pre>" + report_detail + "</pre>")

    kaprodi_mentor_emails = ["kaprodi@kampus.ac.id", "mentor@kampus.ac.id"]
    
    send_mail(
        subject=f"Laporan Akhir/UTS COOP Selesai: {confirmation.student.user.get_full_name()}",
        message=f"""
Halo Kaprodi/Mentor,

Semua Supervisor untuk magang mahasiswa:
{confirmation.student.user.get_full_name()} ({confirmation.student.nim})
di {confirmation.company} telah mengisi evaluasi.

Mohon tinjau hasil evaluasi terlampir (atau dapat diunduh dari web) untuk proses konversi nilai.

Terima kasih.
Unit COOP.

Detail Evaluasi:
---
{report_detail}
""",
        from_email="admin@coop.local",
        recipient_list=kaprodi_mentor_emails,
        fail_silently=True,
    )
    messages.append(f"Laporan akhir terkirim ke email Kaprodi dan Mentor: {', '.join(kaprodi_mentor_emails)}")
    
    return HttpResponse("<br>".join(messages))

def generate_certificate(request, cert_id):
    try:
        cert = Certificate.objects.get(pk=cert_id)
    except Certificate.DoesNotExist:
        return HttpResponse(f"<h1>404 Not Found</h1><p>Sertifikat dengan ID {cert_id} tidak ditemukan. Pastikan data sertifikat sudah dibuat (misalnya dengan ID: {cert_id}).</p>")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="certificate_{cert.student.nim}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width/2, height - 100, "SERTIFIKAT COOP")

    p.setFont("Helvetica", 14)
    p.drawCentredString(width/2, height - 150, "Diberikan kepada:")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, height - 180, cert.student.user.get_full_name())
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, height - 210, f"NIM: {cert.student.nim}")
    p.drawCentredString(width/2, height - 230, f"Program Studi: {cert.student.program_studi}")
    p.drawCentredString(width/2, height - 270, f"Perusahaan: {cert.company.name}")
    p.drawCentredString(width/2, height - 290, f"Periode: {cert.start} s/d {cert.end}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height - 330, f"Konversi Nilai Mata Kuliah COOP: {cert.nilai_konversi}")

    p.showPage()
    p.save()
    return response

@login_required
def upload_final_report(request, conf_id):
    profile = get_object_or_404(ProfileStudent, user=request.user)
    confirmation = get_object_or_404(InternshipConfirmation, id=conf_id, student=profile)

    try:
        report = confirmation.finalreport
    except FinalReport.DoesNotExist:
        report = None

    if request.method == "POST":
        form = FinalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            final_report = form.save(commit=False)
            final_report.confirmation = confirmation
            final_report.save()
            return redirect("coop:dashboard")
    else:
        form = FinalReportForm(instance=report)

    profile = ProfileStudent.objects.filter(user=request.user).first()
    confirmations = InternshipConfirmation.objects.filter(student=profile).order_by('-date_confirmed')
    first_confirmation = confirmations.first() if confirmations else None

    context = {
        "profile": profile,
        "confirmations": confirmations,
        "active_conf_id": first_confirmation.id if first_confirmation else 0,
        "final_report_form": form,
        "report": report,
    }
    return render(request, "dashboard.html", context)