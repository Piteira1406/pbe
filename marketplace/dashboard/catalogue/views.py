from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from ...forms import ClienteRegisterForm, FornecedorRegisterForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
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
    
class ClienteRegisterView(FormView):
    template_name = 'registo_cliente.html'
    form_class = ClienteRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        ClienteProfile.objects.create(
            user=user,
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address']
        )
        return super().form_valid(form)


class FornecedorRegisterView(FormView):
    template_name = 'registo_fornecedor.html'
    form_class = FornecedorRegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        SupplierProfile.objects.create(
            user=user,
            phone=form.cleaned_data['phone'],
            supplier_name=form.cleaned_data['supplier_name']
        )
        return super().form_valid(form)