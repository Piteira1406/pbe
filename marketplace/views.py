from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import ClienteProfile, SupplierProfile, OrderItem, Product, Order
from .serializers import ClienteProfileSerializer, SupplierProfileSerializer, UserSerializer, AdministradorProfileSerializer, OrderItemSerializer, OrderSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Função auxiliar para gerar token JWT
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# POST /api/register/cliente/
@api_view(['POST'])
@permission_classes([AllowAny])
def register_cliente(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Utilizador já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
    ClienteProfile.objects.create(email=user, phone=data['phone'], address=data['address'])
    return Response({'success': 'Cliente registado com sucesso'}, status=status.HTTP_201_CREATED)

# POST /api/register/fornecedor/
@api_view(['POST'])
@permission_classes([AllowAny])
def register_fornecedor(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Utilizador já existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
    SupplierProfile.objects.create(email=user, phone=data['phone'], supplier_name=data['supplier_name'])
    return Response({'success': 'Fornecedor registado com sucesso'}, status=status.HTTP_201_CREATED)

# POST /api/register/admin/
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
        is_staff=True,     # Ativa acesso ao admin Django
        is_superuser=True  # Marca como administrador global
    )
    AdministradorProfile.objects.create(email=user, telefone=data['telefone'])
    return Response({'success': 'Administrador registado com sucesso'}, status=status.HTTP_201_CREATED)

# POST /api/login/
@api_view(['POST'])
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



