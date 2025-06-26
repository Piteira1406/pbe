from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#--------------------------------
# CLIENTE PROFILE.
#--------------------------------
class ClienteProfile(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=False, null=False)
    address = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return f"{self.email.get_username}'s Profile"


#--------------------------------
# SUPPLIER PROFILE.
#--------------------------------

class SupplierProfile(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=False, null=False)
    supplier_name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    
    def __str__(self):
        return f"{self.supplier_name}'s Profile"
    
#--------------------------------
# ADMINISTRADOR PROFILE.
#--------------------------------
class AdministradorProfile(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15, blank=False, null=False)

    def __str__(self):
        return f"Admin {self.email.username}"

#--------------------------------
# PRODUCT CATEGORIES
#--------------------------------

class ProductCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.category_name
    
#--------------------------------
# PRODUCTS
#--------------------------------

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    sell_unity = models.CharField(max_length=50, choices=[('kg', 'Kilogram'),('g', 'Gram'),('l', 'Liter'),('ml', 'Milliliter'),('pcs', 'Pieces')], default='pcs')
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=False, blank=False)
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
#--------------------------------
# ORDERS
#--------------------------------

class Order(models.Model):
    customer = models.ForeignKey(ClienteProfile, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return f"Order {self.id} by {self.customer.email.get_username()}"
    

#--------------------------------
# ORDER ITEMS
#--------------------------------

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    

#--------------------------------
# ADMINISTRADOR PROFILE.
#--------------------------------
class AdministradorProfile(models.Model):
    email = models.OneToOneField(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15, blank=False, null=False)

    def __str__(self):
        return f"Admin {self.email.username}"
