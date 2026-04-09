from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    pending_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    pending_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to="product_photos/", null=True, blank=True) #reference to a file path

    APPROVAL_STATUS = [("Pending", "Pending"),("Approved", "Approved"),("Rejected", "Rejected"),]
    APPROVAL_STATUS = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")]
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    prod_created_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default="Pending")
    orbit_int = models.BooleanField(default=True)
    redirect_int = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="redirected_from")
    deleted_at = models.DateTimeField(null=True, blank=True)
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
    def __str__(self):
        return f"{self.name} ({self.seller.username})"


class Cart(models.Model):
    buyer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    def __str__(self):
        return f"Cart for {self.buyer.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = ("cart", "product")
    def total(self):
        return self.product.price * self.quantity
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


STATE_CHOICES = [("AL","Alabama"),("AK","Alaska"),("AZ","Arizona"),("AR","Arkansas"),("CA","California"),("CO","Colorado"),("CT","Connecticut"),("DE","Delaware"),("FL","Florida"),("GA","Georgia"),("HI","Hawaii"),("ID","Idaho"),("IL","Illinois"),("IN","Indiana"),("IA","Iowa"),("KS","Kansas"),("KY","Kentucky"),("LA","Louisiana"),("ME","Maine"),("MD","Maryland"),("MA","Massachusetts"),("MI","Michigan"),("MN","Minnesota"),("MS","Mississippi"),("MO","Missouri"),("MT","Montana"),("NE","Nebraska"),("NV","Nevada"),("NH","New Hampshire"),("NJ","New Jersey"),("NM","New Mexico"),("NY","New York"),("NC","North Carolina"),("ND","North Dakota"),("OH","Ohio"),("OK","Oklahoma"),("OR","Oregon"),("PA","Pennsylvania"),("RI","Rhode Island"),("SC","South Carolina"),("SD","South Dakota"),("TN","Tennessee"),("TX","Texas"),("UT","Utah"),("VT","Vermont"),("VA","Virginia"),("WA","Washington"),("WV","West Virginia"),("WI","Wisconsin"),("WY","Wyoming")]


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    def __str__(self):
        return self.full_name


class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [("Processing", "Processing"), ("Shipping", "Shipping"), ("Completed", "Completed"), ("Returned", "Returned")]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Processing")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("10.00"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    def __str__(self):
        return f"Order {self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sold_order_items")
    ITEM_STATUS_CHOICES = [("Processing", "Processing"), ("Shipping", "Shipping"), ("Completed", "Completed"), ("Returned", "Returned")]
    status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default="Processing")
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    METHOD_CHOICES = [("CreditCard", "CreditCard"), ("DebitCard", "DebitCard")]
    STATUS_CHOICES = [("Pending", "Pending"), ("Completed", "Completed"), ("Failed", "Failed"), ("Refunded", "Refunded")]
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    cardholder_name = models.CharField(max_length=255, blank=True)
    card_brand = models.CharField(max_length=30, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.CharField(max_length=2, blank=True)
    exp_year = models.CharField(max_length=4, blank=True)
    is_saved = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        if self.order is not None:
            return f"Payment for Order {self.order.pk} - {self.payment_status}"
        return f"{self.card_brand} ending in {self.card_last4}"
    def clean(self):
        if self.is_default and not self.is_saved:
            raise ValidationError("A payment method must be saved before it can be default.")


class Payout(models.Model):
    STATUS_CHOICES = [("Pending", "Pending"),("Paid", "Paid"),("Refunded", "Refunded"),]
    seller = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="payouts",)
    order_item = models.ForeignKey("OrderItem",on_delete=models.CASCADE,related_name="payouts",)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.seller.username} - ${self.amount} - {self.status}"



class ReturnRequest(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="return_requests")
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    reason = models.TextField(blank=True)
    STATUS_CHOICES = [("Pending", "Pending"), ("Approved", "Approved"), ("Denied", "Denied"), ("Processed", "Processed")]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Return {self.pk} - {self.status}"


class AdminLog(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="admin_logs")
    action_type = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.timestamp} - {self.action_type}"


class Fee(models.Model):
    FEE_TYPE_CHOICES = [("Order", "Order"), ("Shipping", "Shipping"), ("Handling", "Handling"), ("Item", "Item")]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="fees", null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="fees", null=True, blank=True)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    def clean(self):
        if not self.order and not self.order_item:
            raise ValidationError("Fee must be attached to an order or an order item.")



class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_hidden = models.BooleanField(default=False)

    class Meta:
        unique_together = ("product", "buyer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.buyer.username} ({self.rating}/5)"
    

#RSS feed
class Notification(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="notifications")
    order_item = models.ForeignKey("OrderItem", on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
