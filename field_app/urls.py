# field_app/urls.py - REKEBISHWA
from django.views.generic import RedirectView
from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # CORE PAGES
    # =========================
    path('', RedirectView.as_view(url='dashboard/')),  # Redirect root to dashboard
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # =========================
    # SCHOOL SELECTION
    # =========================
    path('select-region/', views.select_region, name='select_region'),
    path('select-district/<int:region_id>/', views.select_district, name='select_district'),
    path('select-school/<int:district_id>/', views.select_school, name='select_school'),
    
    # =========================
    # SUBJECT SELECTION
    # =========================
    path('select-subjects/<int:school_id>/', views.select_subjects, name='select_subjects'),
    path('apply-subject/<int:subject_id>/<int:school_id>/', views.apply_for_subject, name='apply_for_subject'),
    
    # =========================
    # LOGBOOK
    # =========================
    path('submit-logbook/', views.submit_logbook, name='submit_logbook'),
    path('logbook-history/', views.logbook_history, name='logbook_history'),
    path('logbook/download/<str:period_type>/', views.download_logbook_pdf, name='download_logbook_pdf'),
    # =========================
# LOGBOOK - REKEBISHWA: ADD MISSING URL
# =========================
    path('logbook/download-options/', views.logbook_download_options, name='logbook_download_options'), 
    # =========================
    # ADMIN MANAGEMENT PAGES - USE DIFFERENT PREFIX
    # =========================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('management/approve-application/<int:application_id>/', views.approve_application, name='approve_application'),
    path('management/assign-assessor/', views.assign_assessor, name='assign_assessor'),  # 🔥 SAHIHI SASA
    path('management/bulk-assign-assessors/', views.bulk_assign_assessors, name='bulk_assign_assessors'),
    
    # =========================
    # REGION PINNING
    # =========================
    path('pin-regions/', views.region_pinning_view, name='pin_regions'),
    path('pinning-success/', views.pinning_success_view, name='pinning_success'),
    
    # =========================
    # APPROVAL LETTERS
    # =========================
    path('download-individual-letter/', views.download_individual_letter, name='download_individual_letter'),
    path('download-group-letter/', views.download_group_letter, name='download_group_letter'),
    
    # =========================
    # ASSESSOR PAGES
    # =========================
    path('assessor/login/', views.assessor_login, name='assessor_login'),
    path('assessor/dashboard/', views.assessor_dashboard, name='assessor_dashboard'),
    
    # =========================
    # STUDENT PAGES
    # =========================
    
    path('my-assessors/', views.my_assessors, name='my_assessors'),
    path('profile/create/', views.profile_create, name='profile_create'),
       path('assessor/bulk-assign/', views.bulk_assign_assessors, name='bulk_assign_assessors'),
    path('assessor/bulk-results/', views.bulk_assignment_results, name='bulk_assignment_results'),
    path('assessor/list/', views.assessor_list, name='assessor_list'),
    path('assessor/resend-credentials/', views.resend_credentials, name='resend_credentials'),
    
    # API endpoints
    path('api/assessor/<int:assessor_id>/details/', views.assessor_details_api, name='assessor_details_api'),
    path('api/assessor/<int:assessor_id>/resend-credentials/', views.resend_assessor_credentials_api, name='resend_assessor_credentials_api'),
    path('api/send-test-email/', views.send_test_email_api, name='send_test_email'),

]
