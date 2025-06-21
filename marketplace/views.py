from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import ClienteProfile, SupplierProfile
from .serializers import ClienteProfileSerializer, SupplierProfileSerializer, UserSerializer
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

# POST /api/login/
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens
        })
    else:
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
        else:
            profile = UserSerializer(user).data

        return Response({'user': profile})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
