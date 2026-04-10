from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

from shop.models import Product, Review, Category, Order, OrderItem, Payment, Address

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo data for Amplify"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Clearing old demo data..."))

       
        Review.objects.all().delete()
        OrderItem.objects.all().delete()
        Payment.objects.all().delete()
        Order.objects.all().delete()
        Address.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        
        User.objects.filter(username__in=[
            "admin1",
            "seller1", "seller2", "seller3",
            "buyer1", "buyer2", "buyer3", "buyer4", "buyer5", "buyer6"
        ]).delete()

        self.stdout.write(self.style.SUCCESS("Creating users..."))

        admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="wriug-7qo$ab-9mqwoy",
            role="admin",
        )

        sellers = []
        for i in range(1, 4):
            seller = User.objects.create_user(
                username=f"seller{i}",
                email=f"seller{i}@example.com",
                password="wriug-7qo$ab-9mqwoy",
                role="seller",
            )
            sellers.append(seller)

        buyers = []
        for i in range(1, 7):
            buyer = User.objects.create_user(
                username=f"buyer{i}",
                email=f"buyer{i}@example.com",
                password="wriug-7qo$ab-9mqwoy",
                role="buyer",
            )
            buyers.append(buyer)

        self.stdout.write(self.style.SUCCESS("Creating categories..."))

        category_names = [
            "Record",
            "Record Player",
            "Amp",
            "Tuner",
            "Headphone",
            "CD",
            "Cleaning Kit",
        ]

        categories = {}
        for name in category_names:
            categories[name] = Category.objects.create(name=name)

        self.stdout.write(self.style.SUCCESS("Creating buyer addresses..."))

        for buyer in buyers:
            Address.objects.create(
                user=buyer,
                full_name=f"{buyer.username.title()} Example",
                street="123 Demo Street",
                city="City",
                state="MS",
                zipcode="39759",
                country="US",
                is_default=True,
            )

        self.stdout.write(self.style.SUCCESS("Creating products..."))

      
        product_data = [
            ("Fleetwood Mac – Rumours", "Record", Decimal("29.99")),
            ("Abbey Road", "Record", Decimal("27.99")),
            ("Dark Side of the Moon", "Record", Decimal("31.99")),
            ("Audio-Technica AT-LP60X", "Record Player", Decimal("149.99")),
            ("Victrola Vintage 3-Speed", "Record Player", Decimal("89.99")),
            ("Sony Stereo Receiver", "Amp", Decimal("219.99")),
            ("Yamaha Natural Sound Tuner", "Tuner", Decimal("129.99")),
            ("Sony WH-1000XM4", "Headphone", Decimal("279.99")),
            ("Bose QuietComfort", "Headphone", Decimal("249.99")),
            ("Greatest Hits Collection", "CD", Decimal("14.99")),
            ("Classic Rock Essentials", "CD", Decimal("12.99")),
            ("Vinyl Cleaning Brush", "Cleaning Kit", Decimal("18.99")),
            ("Turntable Care Set", "Cleaning Kit", Decimal("24.99")),
            ("Speaker Cable Pack", "Amp", Decimal("16.99")),
            ("Portable Record Case", "Record", Decimal("39.99")),
            ("Studio Monitor Headphones", "Headphone", Decimal("89.99")),
            ("Hi-Fi Receiver", "Amp", Decimal("199.99")),
            ("Deluxe Turntable Mat", "Record Player", Decimal("22.99")),
        ]

        descriptions = [
            "Great condition and perfect for everyday listening.",
            "A solid pick for beginners and longtime collectors alike.",
            "Reliable sound quality with a clean, classic look.",
            "A popular item with warm sound and easy setup.",
            "Good value and a nice addition to any music setup.",
        ]

        products = []
        for idx, (name, category_name, price) in enumerate(product_data, start=1):
            seller = random.choice(sellers)
            product = Product.objects.create(
                seller=seller,
                category=categories[category_name],
                name=name,
                description=random.choice(descriptions),
                price=price,
                stock=random.randint(3, 20),
                is_active=True,
                is_approved=True,
                approval_status="Approved",
            )
            products.append(product)

        self.stdout.write(self.style.SUCCESS("Creating reviews/comments..."))

        review_comments = [
            "Really happy with this purchase.",
            "Arrived fast and sounds great.",
            "Exactly what I was looking for.",
            "Works well and looks even better in person.",
            "Good quality for the price.",
            "Would buy from this seller again.",
            "Packaging was great and item matched the description.",
            "Very solid product so far.",
            "This ended up being one of my favorite purchases.",
            "Nice sound quality and easy to use.",
        ]

        for product in products:
            reviewers = random.sample(buyers, k=random.randint(2, min(4, len(buyers))))
            for buyer in reviewers:
                Review.objects.create(
                    product=product,
                    user=buyer,
                    rating=random.randint(3, 5),
                    comment=random.choice(review_comments),
                )

        self.stdout.write(self.style.SUCCESS("Creating a few past orders..."))

        for buyer in buyers[:4]:
            chosen_products = random.sample(products, k=2)
            address = Address.objects.filter(user=buyer, is_default=True).first()

            subtotal = sum(p.price for p in chosen_products)
            tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
            shipping = Decimal("6.99")
            total = subtotal + tax + shipping

            order = Order.objects.create(
                buyer=buyer,
                shipping_address=address,
                total_amount=total,
                status="Delivered",
                created_at=timezone.now(),
            )

            for p in chosen_products:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=1,
                    price_when_ordered=p.price,
                    seller=p.seller,
                )

            Payment.objects.create(
                order=order,
                payment_method="Card",
                payment_status="Completed",
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(self.style.SUCCESS("Demo accounts password: wriug-7qo$ab-9mqwoy"))