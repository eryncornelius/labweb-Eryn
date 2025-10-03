from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "coop"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.MyLoginView.as_view(), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("jobs/", views.job_list, name="job_list"),
    path("confirm-internship/", views.confirm_internship, name="confirm_internship"),
    path("report/<int:conf_id>/monthly/add/", views.monthly_report_create, name="monthly_report_add"),
    path("reminder/", views.send_reminder, name="reminder"),
    path("evaluation/send/<int:conf_id>/", views.send_evaluation_email, name="send_evaluation"),
    path("certificate/generate/<int:cert_id>/", views.generate_certificate, name="certificate_generate"),
    path("evaluation/final/send/<int:conf_id>/", views.send_final_evaluation_report, name="send_final_evaluation"),
    path("report/<int:conf_id>/final/upload/", views.upload_final_report, name="upload_final_report"),
    ]