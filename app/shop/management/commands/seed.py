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

        usernames_to_delete = [
            "admin1",
            "vinylvault",
            "spinmasters",
            "groovegarden",
            "audiowave",
            "needleandgroove",
            "hifihub",
            "soundstack",
            "buyer",
            "buyer1",
        ]
        User.objects.filter(username__in=usernames_to_delete).delete()

        self.stdout.write(self.style.SUCCESS("Creating users..."))

        User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="wriug-7qo$ab-9mqwoy",
            role="admin",
        )

        sellers = []
        seller_data = [
            ("vinylvault", "vinylvault@example.com"),
            ("spinmasters", "spinmasters@example.com"),
            ("groovegarden", "groovegarden@example.com"),
            ("audiowave", "audiowave@example.com"),
            ("needleandgroove", "needleandgroove@example.com"),
            ("hifihub", "hifihub@example.com"),
            ("soundstack", "soundstack@example.com"),
        ]

        for username, email in seller_data:
            seller = User.objects.create_user(
                username=username,
                email=email,
                password="wriug-7qo$ab-9mqwoy",
                role="seller",
            )
            sellers.append(seller)

        buyers = []
        buyer_data = [
            ("buyer", "buyer.buying@example.com", "buyer buying"),
            ("buyer1", "buyer.1@example.com", "buyer 1"),
        ]

        buyer_name_lookup = {}
        for username, email, full_name in buyer_data:
            buyer = User.objects.create_user(
                username=username,
                email=email,
                password="wriug-7qo$ab-9mqwoy",
                role="buyer",
            )
            buyers.append(buyer)
            buyer_name_lookup[buyer.username] = full_name

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

        city_options = [
            ("Chicago", "IL", "60629"),
            ("Los Angeles", "CA", "90011"),
            ("Ketchikan", "AK", "99950"),
            ("New York", "NY", "10001"),
            ("Houston", "TX", "77001"),
            ("San Antonio", "TX", "78201"),
        ]

        for buyer in buyers:
            city, state, zipcode = random.choice(city_options)
            Address.objects.create(
                user=buyer,
                full_name=buyer_name_lookup[buyer.username],
                street=f"{random.randint(100, 999)} Demo Street",
                city=city,
                state=state,
                zipcode=zipcode,
                country="US",
                is_default=True,
            )

        self.stdout.write(self.style.SUCCESS("Creating products..."))

        category_image_map = {
            "Record": "product_photos/record1.jpg",
            "Record Player": "product_photos/recordplayer1.jpg",
            "Amp": "product_photos/amp1.jpg",
            "Tuner": "product_photos/tuner1.jpg",
            "Headphone": "product_photos/headphone1.jpg",
            "CD": "product_photos/cd1.jpg",
            "Cleaning Kit": "product_photos/cleaningkit1.jpg",
        }

        product_data = [
            ("Fleetwood Mac – Rumours", "Record", Decimal("29.99")),
            ("Abbey Road", "Record", Decimal("27.99")),
            ("Dark Side of the Moon", "Record", Decimal("31.99")),
            ("Hotel California", "Record", Decimal("28.99")),
            ("Thriller", "Record", Decimal("30.99")),
            ("Back in Black", "Record", Decimal("26.99")),
            ("Led Zeppelin IV", "Record", Decimal("32.99")),
            ("Born in the U.S.A.", "Record", Decimal("25.99")),
            ("Audio-Technica AT-LP60X", "Record Player", Decimal("149.99")),
            ("Victrola Vintage 3-Speed", "Record Player", Decimal("89.99")),
            ("Sony PS-LX310BT", "Record Player", Decimal("248.99")),
            ("Fluance RT81", "Record Player", Decimal("249.99")),
            ("Deluxe Turntable Mat", "Record Player", Decimal("22.99")),
            ("Sony Stereo Receiver", "Amp", Decimal("219.99")),
            ("Hi-Fi Receiver", "Amp", Decimal("199.99")),
            ("Speaker Cable Pack", "Amp", Decimal("16.99")),
            ("Pioneer Home Audio Receiver", "Amp", Decimal("239.99")),
            ("Compact Stereo Amplifier", "Amp", Decimal("179.99")),
            ("Yamaha Natural Sound Tuner", "Tuner", Decimal("129.99")),
            ("Digital FM/AM Tuner", "Tuner", Decimal("94.99")),
            ("Classic Stereo Tuner", "Tuner", Decimal("109.99")),
            ("Sony WH-1000XM4", "Headphone", Decimal("279.99")),
            ("Bose QuietComfort", "Headphone", Decimal("249.99")),
            ("Studio Monitor Headphones", "Headphone", Decimal("89.99")),
            ("Audio-Technica M50x", "Headphone", Decimal("169.99")),
            ("Wireless Bass Headphones", "Headphone", Decimal("119.99")),
            ("Greatest Hits Collection", "CD", Decimal("14.99")),
            ("Classic Rock Essentials", "CD", Decimal("12.99")),
            ("Jazz Favorites Volume 1", "CD", Decimal("13.99")),
            ("Acoustic Sessions", "CD", Decimal("11.99")),
            ("Vinyl Cleaning Brush", "Cleaning Kit", Decimal("18.99")),
            ("Turntable Care Set", "Cleaning Kit", Decimal("24.99")),
            ("Stylus Cleaning Gel", "Cleaning Kit", Decimal("12.99")),
            ("Record Sleeve Pack", "Cleaning Kit", Decimal("15.99")),
            ("Anti-Static Record Cloth", "Cleaning Kit", Decimal("9.99")),
            ("Portable Record Case", "Record", Decimal("39.99")),
        ]

        descriptions = [
            "Great condition and perfect for everyday listening.",
            "A solid pick for beginners and longtime collectors alike.",
            "Reliable sound quality with a clean, classic look.",
            "A popular item with warm sound and easy setup.",
            "Good value and a nice addition to any music setup.",
            "Well kept and ready to use right out of the box.",
            "A nice choice for anyone building out a home audio setup.",
        ]

        products = []
        for name, category_name, price in product_data:
            seller = random.choice(sellers)
            product = Product.objects.create(
                seller=seller,
                category=categories[category_name],
                name=name,
                description=random.choice(descriptions),
                price=price,
                stock=random.randint(3, 25),
                is_active=True,
                is_approved=True,
                approval_status="Approved",
                photo=category_image_map[category_name],
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
            reviewers = random.sample(buyers, k=random.randint(1, min(2, len(buyers))))
            for buyer in reviewers:
                Review.objects.create(
                    buyer=buyer,
                    product=product,
                    rating=random.randint(4, 5),
                    comment=random.choice(review_comments),
                )

        self.stdout.write(self.style.SUCCESS("Creating a few past orders..."))

        for buyer in buyers:
            chosen_products = random.sample(products, k=random.randint(1, 3))
            address = Address.objects.filter(user=buyer, is_default=True).first()

            subtotal = sum(p.price for p in chosen_products)
            tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
            shipping = Decimal("6.99")
            total = subtotal + tax + shipping

            order = Order.objects.create(
                buyer=buyer,
                shipping_address=address,
                subtotal=subtotal,
                total=total,
                tax_rate=Decimal("0.10"),
                tax=tax,
                fee=shipping,
                status="Delivered",
                created_at=timezone.now(),
            )

            for p in chosen_products:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    seller=p.seller,
                    status="Delivered",
                    quantity=random.randint(1, 2),
                    price_at_purchase=p.price,
                )

            Payment.objects.create(
                user=buyer,
                order=order,
                payment_method="Card",
                payment_status="Completed",
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(self.style.SUCCESS("Demo accounts password: wriug-7qo$ab-9mqwoy"))