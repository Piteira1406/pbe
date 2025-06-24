from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from oscar.core.loading import get_model
from marketplace.models import Product
from marketplace.forms import ProductForm

class FornecedorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'dashboard/fornecedor/produtos_list.html'
    context_object_name = 'produtos'

    def get_queryset(self):
        return Product.objects.filter(supplier=self.request.user.supplierprofile)

class FornecedorProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'dashboard/fornecedor/produto_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('dashboard:fornecedor_produtos')

    def form_valid(self, form):
        form.instance.supplier = self.request.user.supplierprofile
        return super().form_valid(form)

class FornecedorProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'dashboard/fornecedor/produto_form.html'
    form_class = ProductForm
    success_url = reverse_lazy('dashboard:fornecedor_produtos')

    def get_queryset(self):
        return Product.objects.filter(supplier=self.request.user.supplierprofile)

class FornecedorProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'dashboard/fornecedor/produto_confirm_delete.html'
    success_url = reverse_lazy('dashboard:fornecedor_produtos')

    def get_queryset(self):
        return Product.objects.filter(supplier=self.request.user.supplierprofile)