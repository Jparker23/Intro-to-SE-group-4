from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from accounts.models import User
from .models import (Review, Product, Notification, Category, Cart, CartItem,Address, Order, OrderItem, Payment, ReturnRequest,AdminLog, Fee)


# --- Custom Actions ---

def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True) if hasattr(User, 'is_approved') else None
    for user in queryset:
        AdminLog.objects.create(
            admin=request.user,
            action_type="Approve User",
            target_type="User",
            target_id=user.id,
        )
approve_users.short_description = "Approve selected users"


def deny_users(modeladmin, request, queryset):
    for user in queryset:
        AdminLog.objects.create(
            admin=request.user,
            action_type="Deny User",
            target_type="User",
            target_id=user.id,
        )
deny_users.short_description = "Deny selected users"


def approve_products(modeladmin, request, queryset):
    queryset.update(is_approved=True, is_active=True, approval_status="Approved")
    for product in queryset:
        AdminLog.objects.create(
            admin=request.user,
            action_type="Approve Product",
            target_type="Product",
            target_id=product.id,
        )
approve_products.short_description = "Approve selected products"


def deny_products(modeladmin, request, queryset):
    queryset.update(is_approved=False, is_active=False, approval_status="Rejected")
    for product in queryset:
        AdminLog.objects.create(
            admin=request.user,
            action_type="Deny Product",
            target_type="Product",
            target_id=product.id,
        )
deny_products.short_description = "Deny selected products"


def approve_returns(modeladmin, request, queryset):
    with transaction.atomic():
        for return_request in queryset.select_related("order_item__order"):
            return_request.status = "Approved"
            return_request.save(update_fields=["status"])

            order_item = return_request.order_item
            order_item.status = "Returned"
            order_item.save(update_fields=["status"])

            Payment.objects.filter(
                order=order_item.order,
                payment_status="Completed"
            ).update(payment_status="Refunded")

            AdminLog.objects.create(
                admin=request.user,
                action_type="Approve Return",
                target_type="ReturnRequest",
                target_id=return_request.id,
            )
approve_returns.short_description = "Approve selected returns"


def deny_returns(modeladmin, request, queryset):
    with transaction.atomic():
        for return_request in queryset:
            return_request.status = "Denied"
            return_request.save(update_fields=["status"])

            AdminLog.objects.create(
                admin=request.user,
                action_type="Deny Return",
                target_type="ReturnRequest",
                target_id=return_request.id,
            )
deny_returns.short_description = "Deny selected returns"


# --- Inlines ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'seller', 'quantity', 'price_at_purchase', 'status')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity')


# --- User Admin ---

class UserAccountAdmin(UserAdmin):
    actions = [approve_users, deny_users]
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
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

admin.site.register(User, UserAccountAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ReturnRequest, ReturnRequestAdmin)
admin.site.register(AdminLog, AdminLogAdmin)
admin.site.register(Fee, FeeAdmin)


# --- lets admins see reviews on prducts, so then they can manage reviews ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "buyer", "rating", "is_hidden", "created_at")
    list_filter = ("rating", "is_hidden", "created_at")
    search_fields = ("product__name", "buyer__username", "comment")



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("seller", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("seller__username", "message")