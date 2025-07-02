from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.db.models import Sum
from django.contrib.auth.models import Group
from decimal import Decimal
from oscar.apps.partner.models import Partner
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import ClienteProfile, SupplierProfile, OrderItem, Product, ProductCategory, Order
from .serializers import ClienteProfileSerializer, SupplierProfileSerializer, UserSerializer, OrderItemSerializer, OrderSerializer, ProductSerializer, ProductCategorySerializer, AdministradorProfileSerializer
from .forms import ClienteRegisterForm, FornecedorRegisterForm
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.views import View

# JWT helper
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# POST /api/register/cliente/
@api_view(['POST','GET'])
@permission_classes([AllowAny])
def register_cliente(request):
    if request.method == 'POST':
        form = ClienteRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']

            # Criar o utilizador
            user = User.objects.create_user(username=username, email=email, password=password)
            # Criar o perfil do cliente
            ClienteProfile.objects.create(email=user, phone=phone, address=address)

            
            return redirect('/')  

        else:
            return render(request, 'registo_cliente.html', {'form': form})

    else:
        form = ClienteRegisterForm()

    return render(request, 'registo_cliente.html', {'form': form})
# POST /api/register/fornecedor/
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def register_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorRegisterForm(request.POST)
        if form.is_valid():
            # Extrair dados do formulário
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            phone = form.cleaned_data['phone']
            supplier_name = form.cleaned_data['supplier_name']

            # Criar utilizador normal (sem is_staff)
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Adicionar ao grupo "Fornecedores"
            from django.contrib.auth.models import Group
            grupo, _ = Group.objects.get_or_create(name="Fornecedores")
            from oscar.apps.partner.models import Partner
            
            user.groups.add(grupo)
            user.save()

            # Criar perfil do fornecedor
            SupplierProfile.objects.create(
                email=user,
                phone=phone,
                supplier_name=supplier_name
            )
            
            partner = Partner.objects.create(name=supplier_name)
            partner.users.add(user)
            partner.save()

            return redirect('/')  # Ou redireciona para /login ou /dashboard
        else:
            return render(request, 'registo_fornecedor.html', {'form': form})
    else:
        form = FornecedorRegisterForm()
    return render(request, 'registo_fornecedor.html', {'form': form})


@api_view(['POST'])
@permission_classes([AllowAny])  # Podes mudar para IsAdminUser em produção
def register_admin(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Utilizador já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        is_staff=True,    # Ativa acesso ao admin Django
        is_superuser=True  # Marca como administrador global
    )
    AdministradorProfile.objects.create(email=user, telefone=data['telefone'])
    return Response({'success': 'Administrador registado com sucesso'}, status=status.HTTP_201_CREATED)

# POST /api/login/
@api_view(['POST',])
@permission_classes([AllowAny])
def login_view(request):
    print("Login view ativada")  
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'tokens': tokens
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


# GET /api/profile/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    try:
        if hasattr(user, 'clienteprofile'):
            profile = ClienteProfileSerializer(user.clienteprofile).data
        elif hasattr(user, 'supplierprofile'):
            profile = SupplierProfileSerializer(user.supplierprofile).data
        elif hasattr(user, 'administradorprofile'):
            profile = AdministradorProfileSerializer(user.administradorprofile).data
        else:
            profile = UserSerializer(user).data

        return Response({'user': profile})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# GET /api/encomendas/fornecedor/
# Esta view retorna as encomendas feitas a um fornecedor específico.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encomendas_fornecedor(request):
    if not hasattr(request.user, 'supplierprofile'):
        return Response({'error': 'Apenas fornecedores podem ver estas encomendas.'}, status=403)
    items = OrderItem.objects.filter(product__supplier=request.user.supplierprofile)
    return Response(OrderItemSerializer(items, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estatisticas_fornecedor(request):
    if not hasattr(request.user, 'supplierprofile'):
        return Response({'error': 'Apenas fornecedores têm acesso às estatísticas.'}, status=403)
    produtos = Product.objects.filter(supplier=request.user.supplierprofile)
    items = OrderItem.objects.filter(product__in=produtos)
    return Response({
        'total_faturado': items.aggregate(Sum('price_per_unit'))['price_per_unit__sum'] or 0,
        'total_produtos_vendidos': items.aggregate(Sum('quantity'))['quantity__sum'] or 0,
        'total_encomendas': items.values('order').distinct().count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encomendas_cliente(request):
    if not hasattr(request.user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem ver encomendas.'}, status=403)
    encomendas = Order.objects.filter(customer=request.user.clienteprofile)
    return Response(OrderSerializer(encomendas, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_encomenda_cliente(request, id):
    if not hasattr(request.user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem ver encomendas.'}, status=403)
    try:
        encomenda = Order.objects.get(id=id, customer=request.user.clienteprofile)
        return Response(OrderSerializer(encomenda).data)
    except Order.DoesNotExist:
        return Response({'error': 'Encomenda não encontrada.'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_encomenda(request):
    if not hasattr(request.user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem criar encomendas.'}, status=403)
    data = request.data.get('items', [])
    if not data:
        return Response({'error': 'Carrinho vazio.'}, status=400)

    total, order_items = Decimal('0.00'), []
    for item in data:
        try:
            produto = Product.objects.get(id=item['product_id'])
            quantidade = int(item['quantity'])
            if quantidade <= 0:
                return Response({'error': 'Quantidade inválida.'}, status=400)
            total += produto.price * quantidade
            order_items.append({'product': produto, 'quantity': quantidade, 'price_per_unit': produto.price})
        except Product.DoesNotExist:
            return Response({'error': f'Produto ID {item["product_id"]} não encontrado.'}, status=404)

    encomenda = Order.objects.create(customer=request.user.clienteprofile, total_amount=total)
    for i in order_items:
        OrderItem.objects.create(order=encomenda, **i)

    return Response({'success': 'Encomenda criada.', 'order_id': encomenda.id}, status=201)

# PRODUCT VIEWS
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'supplier', 'stock_quantity']

    def get_permissions(self):
        return [permissions.IsAuthenticated()] if self.request.method == 'POST' else [permissions.AllowAny()]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'supplierprofile'):
            raise PermissionDenied("Apenas fornecedores podem criar produtos.")
        serializer.save(supplier=user.supplierprofile)

class SupplierDashboardView(View):
    def get(self, request):
        if not hasattr(request.user, 'supplierprofile'):
            return redirect('/dashboard')  # ou mostrar erro
        return render(request, 'dashboard/fornecedor.html')
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()] if self.request.method in ['PUT', 'PATCH', 'DELETE'] else [permissions.AllowAny()]

# CATEGORY VIEWS
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]




def atribuir_a_fornecedores(user):
    grupo, criado = Group.objects.get_or_create(name='Fornecedores')
    user.groups.add(grupo)
    user.save()
