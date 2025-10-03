from django.contrib import admin
from .models import ProfileStudent, Company, JobPosting, InternshipConfirmation, MonthlyReport, SupervisorEvaluation, Certificate, FinalReport

admin.site.register(ProfileStudent)
admin.site.register(Company)
admin.site.register(JobPosting)
admin.site.register(InternshipConfirmation)
admin.site.register(MonthlyReport)
admin.site.register(SupervisorEvaluation)
admin.site.register(Certificate)
admin.site.register(FinalReport)