from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    UserAccount, Product, Category, Cart, CartItem,
    Address, Order, OrderItem, Payment, ReturnRequest,
    AdminLog, Fee
)


# --- Custom Actions ---

def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True)
approve_users.short_description = "Approve selected users"

def deny_users(modeladmin, request, queryset):
    queryset.update(is_approved=False)
deny_users.short_description = "Deny selected users"

def approve_products(modeladmin, request, queryset):
    queryset.update(is_approved=True, is_active=True, approval_status="Approved")
approve_products.short_description = "Approve selected products"

def deny_products(modeladmin, request, queryset):
    queryset.update(is_approved=False, is_active=False, approval_status="Rejected")
deny_products.short_description = "Deny selected products"

def approve_returns(modeladmin, request, queryset):
    queryset.update(status='Approved')
approve_returns.short_description = "Approve selected returns"

def deny_returns(modeladmin, request, queryset):
    queryset.update(status='Denied')
deny_returns.short_description = "Deny selected returns"


# --- Inlines ---

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'stock', 'is_approved', 'is_active', 'approval_status')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'seller', 'quantity', 'price_at_purchase', 'status')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity')


# --- UserAccount Admin ---

class UserAccountAdmin(UserAdmin):
    inlines = [ProductInline]
    actions = [approve_users, deny_users]
    list_display = ('username', 'email', 'is_seller', 'is_buyer', 'is_approved', 'is_staff')
    list_filter = ('is_seller', 'is_buyer', 'is_approved', 'is_staff')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_approved', 'is_seller', 'is_buyer')}),
    )


# --- Product Admin ---

class ProductAdmin(admin.ModelAdmin):
    actions = [approve_products, deny_products]
    list_display = ('name', 'seller', 'price', 'stock', 'approval_status', 'is_approved', 'is_active')
    list_filter = ('approval_status', 'is_approved', 'is_active', 'category')
    search_fields = ('name', 'seller__username')


# --- Category Admin ---

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# --- Order Admin ---

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'buyer', 'status', 'subtotal', 'tax', 'fee', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('buyer__username',)


# --- Cart Admin ---

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('buyer',)
    search_fields = ('buyer__username',)


# --- Address Admin ---

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'country', 'is_default')
    search_fields = ('user__username', 'full_name', 'city')


# --- Payment Admin ---

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'payment_method', 'payment_status', 'payment_date')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('user__username', 'cardholder_name')


# --- Return Request Admin ---

class ReturnRequestAdmin(admin.ModelAdmin):
    actions = [approve_returns, deny_returns]
    list_display = ('id', 'buyer', 'order_item', 'status', 'refund_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('buyer__username',)


# --- Admin Log ---

class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action_type', 'target_type', 'target_id', 'timestamp')
    list_filter = ('action_type', 'target_type')
    search_fields = ('admin__username',)


# --- Fee Admin ---

class FeeAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'amount', 'order', 'order_item')
    list_filter = ('fee_type',)


# --- Register All ---

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ReturnRequest, ReturnRequestAdmin)
admin.site.register(AdminLog, AdminLogAdmin)
admin.site.register(Fee, FeeAdmin)