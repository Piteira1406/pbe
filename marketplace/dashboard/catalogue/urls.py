from django.urls import path
from .views import (
    FornecedorProductListView,
    FornecedorProductCreateView,
    FornecedorProductUpdateView,
    FornecedorProductDeleteView
)

app_name = 'dashboard'

urlpatterns = [
    path('fornecedor/produtos/', FornecedorProductListView.as_view(), name='fornecedor_produtos'),
    path('fornecedor/produtos/adicionar/', FornecedorProductCreateView.as_view(), name='fornecedor_produto_adicionar'),
    path('fornecedor/produtos/<int:pk>/editar/', FornecedorProductUpdateView.as_view(), name='fornecedor_produto_editar'),
    path('fornecedor/produtos/<int:pk>/remover/', FornecedorProductDeleteView.as_view(), name='fornecedor_produto_remover'),
]
