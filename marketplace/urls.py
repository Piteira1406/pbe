from django.urls import path
from . import views

urlpatterns = [
    path('register/cliente/', views.register_cliente, name='register_cliente'),
    path('register/fornecedor/', views.register_fornecedor, name='register_fornecedor'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
]