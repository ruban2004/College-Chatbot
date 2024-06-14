from django.urls import path
from . import views

urlpatterns = [
        path('student-list/', views.student_list, name='student_list'),

    path('', views.home, name='home'),
    path('register/', views.register_new_student, name='register_new_student'),
    path('login/', views.login_existing_student, name='login_existing_student'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
