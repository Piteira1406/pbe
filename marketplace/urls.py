from django.urls import path
from . import views

urlpatterns = [
    path('register/cliente/', views.register_cliente, name='register_cliente'),
    path('register/fornecedor/', views.register_fornecedor, name='register_fornecedor'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('encomendas/fornecedor/', views.encomendas_fornecedor, name='encomendas_fornecedor'),
    path('estatisticas/fornecedor/', views.estatisticas_fornecedor, name='estatisticas_fornecedor'),
    path('encomendas/', views.encomendas_cliente, name='encomendas_cliente'),
    path('encomendas/<int:id>/', views.detalhe_encomenda_cliente, name='detalhe_encomenda_cliente'),
    path('encomendas/criar/', views.criar_encomenda, name='criar_encomenda'),

]