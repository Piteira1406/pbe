from django.contrib import admin
from ..marketplace.models import ( ClienteProfile, SupplierProfile, ProductCategory, Product, Order, OrderItem )

#-------------------------
# Cliente
#-------------------------

@admin.register(ClienteProfile)
class ClienteProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone')
    search_fields = ('email__username', 'phone')

#-------------------------
# Supplier
#-------------------------

@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'supplier_name')
    search_fields = ('email__username', 'supplier_name')

#-------------------------
# Product Category
#-------------------------

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'description')
    search_fields = ('category_name',)

#-------------------------
# Product
#-------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity', 'category', 'supplier', 'sell_unity')
    search_fields = ('name', 'category__category_name', 'supplier__supplier_name')
    list_filter = ('category', 'supplier')
    autocomplete = ['category', 'supplier']

#-------------------------
# ItemOrder Inline
#-------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

#-------------------------
# Order
#-------------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'created_at', 'updated_at')
    search_fields = ('cliente__email__username',)
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

    def cliente(self, obj):
        return obj.cliente.email.get_username() if obj.cliente else 'N/A'
    cliente.short_description = 'Cliente'