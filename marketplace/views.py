from django.shortcuts import render
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import User, ClienteProfile, SupplierProfile, Product, ProductCategory, Order, OrderItem
from .serializers import OrderSerializer
from django.db import transaction
from .models import ClienteProfile, SupplierProfile, OrderItem, Product, Order
from .serializers import ClienteProfileSerializer, SupplierProfileSerializer, UserSerializer, OrderItemSerializer, OrderSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    Product, ProductCategory,
    ClienteProfile, SupplierProfile
)
from .serializers import (
    ProductSerializer, ProductCategorySerializer,
    ClienteProfileSerializer, SupplierProfileSerializer, UserSerializer
)

# ----------------------------
# PRODUCT LIST + CREATE VIEW
# ----------------------------
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'supplier']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        try:
            supplier = self.request.user.supplierprofile
            serializer.save(supplier=supplier)
        except Exception as e:
            raise PermissionDenied(f"Only Suppliers can Create Products. Error: {str(e)}")

# ----------------------------
# GET TOKEN JWT FOR USER
# ----------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ----------------------------
# REGISTO DE CLIENTE
# ----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_cliente(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Utilizador já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
    ClienteProfile.objects.create(email=user, phone=data['phone'], address=data['address'])
    return Response({'success': 'Cliente registado com sucesso'}, status=status.HTTP_201_CREATED)

# ----------------------------
# REGISTO DE FORNECEDOR
# ----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_fornecedor(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Utilizador já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
    SupplierProfile.objects.create(email=user, phone=data['phone'], supplier_name=data['supplier_name'])
    return Response({'success': 'Fornecedor registado com sucesso'}, status=status.HTTP_201_CREATED)

# ----------------------------
# LOGIN COM JWT TOKEN
# ----------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    print("Login view ativada")  
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

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


    return Response({
        "user": UserSerializer(user).data,
        "tokens": {
            "access": access_token,
            "refresh": refresh_token
        }
    }, status=status.HTTP_200_OK)

# ----------------------------
# PERFIL DE UTILIZADOR AUTENTICADO
# ----------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    try:
        if hasattr(user, 'clienteprofile'):
            profile = ClienteProfileSerializer(user.clienteprofile).data
        elif hasattr(user, 'supplierprofile'):
            profile = SupplierProfileSerializer(user.supplierprofile).data
        else:
            profile = UserSerializer(user).data

        return Response({'user': profile})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------
# PRODUCT DETAIL VIEW
# ----------------------------
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

# ----------------------------
# CATEGORIA LISTAGEM
# ----------------------------
class CategoryListAPIView(generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]

# ----------------------------
# CATEGORIA DETALHE (GET/PUT/DELETE)
# ----------------------------
class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
# ----------------------------
# ORDERS
# ----------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    user = request.user

    if not hasattr(user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem fazer encomendas.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    items = data.get('items', [])

    if not items:
        return Response({'error': 'Nenhum produto fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            total_amount = 0
            order = Order.objects.create(customer=user.clienteprofile, total_amount=0)

            for item in items:
                product_id = item.get('product_id')
                quantity = int(item.get('quantity', 1))

                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise Exception(f"Produto com ID {product_id} não existe.")

                if product.stock_quantity < quantity:
                    raise Exception(f"Stock insuficiente para {product.name}")

                # Subtrai stock
                product.stock_quantity -= quantity
                product.save()

                subtotal = product.price * quantity
                total_amount += subtotal

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_per_unit=product.price
                )

            order.total_amount = total_amount
            order.save()

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# GET /api/encomendas/fornecedor/
# Esta view retorna as encomendas feitas a um fornecedor específico.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encomendas_fornecedor(request):
    user = request.user

    if not hasattr(user, 'supplierprofile'):
        return Response({'error': 'Apenas fornecedores podem ver estas encomendas.'}, status=403)

    fornecedor = user.supplierprofile

    # Filtrar OrderItems cujos produtos pertencem ao fornecedor
    items = OrderItem.objects.filter(product__supplier=fornecedor).select_related('order', 'product')

    serializer = OrderItemSerializer(items, many=True)
    return Response(serializer.data)

#Get /api/estatisticas/fornecedor/

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estatisticas_fornecedor(request):
    user = request.user

    if not hasattr(user, 'supplierprofile'):
        return Response({'error': 'Apenas fornecedores têm acesso às estatísticas.'}, status=403)

    fornecedor = user.supplierprofile

    produtos = Product.objects.filter(supplier=fornecedor)
    items = OrderItem.objects.filter(product__in=produtos)

    total_faturado = items.aggregate(total=Sum('price_per_unit'))['total'] or 0
    total_produtos_vendidos = items.aggregate(qtd=Sum('quantity'))['qtd'] or 0
    total_encomendas = items.values('order').distinct().count()

    return Response({
        'total_faturado': total_faturado,
        'total_produtos_vendidos': total_produtos_vendidos,
        'total_encomendas': total_encomendas,
    })
  
 # GET /api/encomendas/cliente/   
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encomendas_cliente(request):
    user = request.user

    if not hasattr(user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem ver as suas encomendas.'}, status=403)

    cliente = user.clienteprofile
    encomendas = Order.objects.filter(customer=cliente).prefetch_related('items__product')
    serializer = OrderSerializer(encomendas, many=True)

    return Response(serializer.data)

# GET /api/encomendas/cliente/<id>/
# Esta view retorna os detalhes de uma encomenda específica de um cliente.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalhe_encomenda_cliente(request, id):
    user = request.user

    if not hasattr(user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem ver encomendas.'}, status=403)

    try:
        encomenda = Order.objects.get(id=id, customer=user.clienteprofile)
    except Order.DoesNotExist:
        return Response({'error': 'Encomenda não encontrada ou não pertence a este utilizador.'}, status=404)

    serializer = OrderSerializer(encomenda)
    return Response(serializer.data)

# POST /api/encomendas/
# Esta view permite que um cliente crie uma nova encomenda com base nos itens do carrinho
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_encomenda(request):
    user = request.user

    if not hasattr(user, 'clienteprofile'):
        return Response({'error': 'Apenas clientes podem criar encomendas.'}, status=403)

    data = request.data
    items_data = data.get('items', [])

    if not items_data:
        return Response({'error': 'Carrinho vazio.'}, status=400)

    total = Decimal('0.00')
    order_items = []

    for item in items_data:
        try:
            product = Product.objects.get(id=item['product_id'])
            quantity = int(item['quantity'])

            if quantity <= 0:
                return Response({'error': f'Quantidade inválida para o produto ID {item["product_id"]}.'}, status=400)

            price_unit = product.price
            total += price_unit * quantity

            order_items.append({
                'product': product,
                'quantity': quantity,
                'price_per_unit': price_unit
            })

        except Product.DoesNotExist:
            return Response({'error': f'Produto ID {item["product_id"]} não encontrado.'}, status=404)

    # Criar encomenda
    order = Order.objects.create(customer=user.clienteprofile, total_amount=total)

    # Criar os OrderItem associados
    for item in order_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price_per_unit=item['price_per_unit']
        )

    return Response({'success': 'Encomenda criada com sucesso.', 'order_id': order.id}, status=201)
