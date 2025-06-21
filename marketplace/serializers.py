from rest_framework import serializers
from .models import ClienteProfile, SupplierProfile, ProductCategory, Product, Order, OrderItem
from django.contrib.auth.models import User

# User básico (para exibir info limitada)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# Cliente
class ClienteProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='email', read_only=True)

    class Meta:
        model = ClienteProfile
        fields = ['id', 'user', 'phone', 'address']

# Fornecedor
class SupplierProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='email', read_only=True)

    class Meta:
        model = SupplierProfile
        fields = ['id', 'user', 'phone', 'supplier_name']

# Categoria
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'category_name', 'description']

# Produto
class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    supplier = SupplierProfileSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'image', 'price',
            'sell_unity', 'stock_quantity', 'category', 'supplier'
        ]

# Item de Encomenda
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_per_unit']

# Encomenda
class OrderSerializer(serializers.ModelSerializer):
    customer = ClienteProfileSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'status', 'total_amount', 'items']
