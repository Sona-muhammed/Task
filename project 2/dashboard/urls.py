from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/update/<int:student_id>/', views.update_student, name='update_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/progress/', views.progress_sheet_list, name='progress_sheet_list'),
    path('students/<int:student_id>/progress/add/', views.add_progress_sheet, name='add_progress_sheet'),
    path('progress/update/<int:progress_sheet_id>/', views.update_progress_sheet, name='update_progress_sheet'),
    path('progress/delete/<int:progress_sheet_id>/', views.delete_progress_sheet, name='delete_progress_sheet'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/update/<int:subject_id>/', views.update_subject, name='update_subject'),
    path('subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('progress/bulk/', views.bulk_progress_sheet_entry, name='bulk_progress_sheet_entry'),
    path('ranking/', views.student_ranking, name='student_ranking'),
]