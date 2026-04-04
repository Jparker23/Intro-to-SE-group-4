from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserAccount, Product, Return


# --- Custom Actions ---

def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True)
approve_users.short_description = "Approve selected users"

def deny_users(modeladmin, request, queryset):
    queryset.update(is_approved=False)
deny_users.short_description = "Deny selected users"

def approve_products(modeladmin, request, queryset):
    queryset.update(is_approved=True, is_active=True)
approve_products.short_description = "Approve selected products"

def deny_products(modeladmin, request, queryset):
    queryset.update(is_approved=False, is_active=False)
deny_products.short_description = "Deny selected products"

def approve_returns(modeladmin, request, queryset):
    queryset.update(status='approved')
approve_returns.short_description = "Approve selected returns"

def deny_returns(modeladmin, request, queryset):
    queryset.update(status='denied')
deny_returns.short_description = "Deny selected returns"


# --- Product Inline ---

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'quantity', 'is_approved', 'is_active')


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
    list_display = ('name', 'seller', 'price', 'quantity', 'is_approved', 'is_active')
    list_filter = ('is_approved', 'is_active')
    search_fields = ('name', 'seller__username')


# --- Return Admin ---

class ReturnAdmin(admin.ModelAdmin):
    actions = [approve_returns, deny_returns]
    list_display = ('buyer', 'product', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('buyer__username', 'product__name')


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Return, ReturnAdmin)

