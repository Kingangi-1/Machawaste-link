from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('waste/post/', views.post_waste, name='post_waste'),
    path('waste/', views.waste_list, name='waste_list'),
    path('waste/<int:pk>/', views.waste_detail, name='waste_detail'),
    path('match/<int:pk>/<str:action>/', views.manage_match, name='manage_match'),
]