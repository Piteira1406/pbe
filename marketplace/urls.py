from django.urls import path
from . import views

urlpatterns = [
    # Authentication and Registration
    path('register/cliente/', views.register_cliente, name='register_cliente'),
    path('register/fornecedor/', views.register_fornecedor, name='register_fornecedor'),
    path('register/admin/', views.register_admin, name='register_admin'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),

    # Products and Categories
    path('produtos/', views.ProductListCreateAPIView.as_view(), name='product-list'),
    path('produtos/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('categorias/', views.CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categorias/<int:pk>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
    # Orders (Customer)
    path('encomendas/criar/', views.criar_encomenda, name='criar_encomenda'),
    path('encomendas/cliente/', views.encomendas_cliente, name='encomendas_cliente'),
    path('encomendas/cliente/<int:id>/', views.detalhe_encomenda_cliente, name='detalhe_encomenda_cliente'),

    # Orders (Supplier)
    path('encomendas/fornecedor/', views.encomendas_fornecedor, name='encomendas_fornecedor'),
    path('estatisticas/fornecedor/', views.estatisticas_fornecedor, name='estatisticas_fornecedor'),
]