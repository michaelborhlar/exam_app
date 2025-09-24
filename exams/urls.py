from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('upload_docx/', views.upload_docx, name='upload_docx'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),

]
 