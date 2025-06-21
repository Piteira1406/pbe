from django.urls import path, include
from . import views

urlpatterns = [
    path('register/cliente/', views.register_cliente, name='register_cliente'),
    path('register/fornecedor/', views.register_fornecedor, name='register_fornecedor'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('produtos/', views.ProductListCreateAPIView.as_view(), name='product-list'),
    path('produtos/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('categorias/', views.CategoryListAPIView.as_view(), name='category-list'),
]