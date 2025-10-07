from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='core/home.html'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('waste/post/', views.post_waste, name='post_waste'),
    path('waste/', views.waste_list, name='waste_list'),
    path('waste/<int:pk>/', views.waste_detail, name='waste_detail'),
    path('match/<int:pk>/<str:action>/', views.manage_match, name='manage_match'),
    path('waste/<int:waste_item_id>/request/', views.request_match, name='request_match'),
    path('credits/', views.user_credits, name='user_credits'),
    path('waste/<int:pk>/complete/', views.manage_match, {'action': 'complete'}, name='complete_waste'),
    path('test-award/<int:waste_id>/', views.test_award_credits, name='test_award'),
]