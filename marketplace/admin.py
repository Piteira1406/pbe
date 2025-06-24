from django.contrib import admin
from .models import Product, Order, OrderItem, SupplierProfile


#ProductAdmin
# Custom admin class for Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'supplier')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            return qs.filter(supplier__email=request.user)
        except:
            return qs.none()

admin.site.register(Product, ProductAdmin)

# Order item so para ver os produtos associados a cada fornecedor
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'order')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            return qs.filter(product__supplier__email=request.user)
        except:
            return qs.none()

admin.site.register(OrderItem, OrderItemAdmin)

#Order associadas a produtos do fornecedor
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            return qs.filter(items__product__supplier__email=request.user).distinct()
        except:
            return qs.none()

admin.site.register(Order, OrderAdmin)
