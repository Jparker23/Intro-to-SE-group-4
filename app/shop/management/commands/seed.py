from django.core.management.base import BaseCommand
from decimal import Decimal
from pathlib import Path
from django.core.files import File
from shop.models import Product, ReturnRequest, Category, Order, OrderItem, Payment, Address, Payout
from django.utils import timezone
from accounts.models import User
#file to seed the database with premade values

class Command(BaseCommand):
    help = "Seeds the database with initial data for the Product, Category, and User models"
    
    def handle(self, *args, **options):
       #clear only safe data
        ReturnRequest.objects.all().delete()
        Payout.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Address.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        # tracked seed image folder in repo
        seed_photo_dir = Path(__file__).resolve().parents[2] / "seed_photos"

        image_map = {
            "Record": "record1.jpg",
            "Record Player": "recordplayer.jpg",
            "Amp": "amp.jpg",
            "Tuner": "tuner.jpg",
            "Headphone": "headphones.jpg",
            "CD": "testcd.jpg",
            "Cleaning Kit": "cleaning-kit-product-photo.jpg",
        }


        
        # Categories
        record, _ = Category.objects.get_or_create(name="Record")
        record_player, _ = Category.objects.get_or_create(name="Record Player")
        amp, _ = Category.objects.get_or_create(name="Amp")
        tuner, _ = Category.objects.get_or_create(name="Tuner")
        headphone, _ = Category.objects.get_or_create(name="Headphone")
        cd, _ = Category.objects.get_or_create(name="CD")
        cleaning_kit, _ = Category.objects.get_or_create(name="Cleaning Kit")

        # Users
        admin, _ = User.objects.get_or_create(username ="testadmin", defaults={
            "role": "admin",
            "email": "admin@test.com",
            "is_staff": True,
        })
        admin.is_active = True
        admin.is_staff = True
        if hasattr(admin, "is_approved"):
          admin.is_approved = True
        admin.set_password("password123")
        admin.save()
        
        admin1, _ = User.objects.get_or_create(username ="testadmin1", defaults={
            "role": "admin",
            "email": "admin1@test.com",
            "is_staff": True,
        })
        admin.is_active = True
        admin.is_staff = True
        if hasattr(admin, "is_approved"):
          admin.is_approved = True
        admin1.set_password("password123")
        admin1.save()
        
        buyer, _ = User.objects.get_or_create(username="testbuyer", defaults={
            "role": "buyer",
            "email": "buyer@test.com",
        })
        buyer.role = "buyer"
        buyer.is_active = True
        if hasattr(buyer, "is_approved"):
            buyer.is_approved = True
        buyer.set_password("password123")
        buyer.save()
        
        buyer1, _ = User.objects.get_or_create(username="testbuyer1", defaults={
            "role": "buyer",
            "email": "buyer1@test.com",
        })
        buyer1.role = "buyer"
        buyer1.is_active = True
        if hasattr(buyer1, "is_approved"):
            buyer1.is_approved = True
        buyer1.set_password("password123")
        buyer1.save()
        
        seller, _ = User.objects.get_or_create(username="VinylVault", defaults={
        "email": "vinylvault@shop.com",
        })
        seller.role = "seller"
        seller.is_active = True
        if hasattr(seller, "is_approved"):
            seller.is_approved = True
        seller.set_password("password123")
        seller.save()

        seller1, _ = User.objects.get_or_create(username="AudioHaven", defaults={
            "email": "audiohaven@shop.com",
        })
        seller1.role = "seller"
        seller1.is_active = True
        if hasattr(seller1, "is_approved"):
            seller1.is_approved = True
        seller1.set_password("password123")
        seller1.save()
                
        product_defaults = dict(
            is_active=True,
            is_approved=True,
            approval_status="Approved",
            orbit_int=True,
            redirect_int=None,
            deleted_at=None,
        )

        def create_product(name, seller_obj, category_obj, description, price, stock, image_key):
            product = Product.objects.create(
                name=name,
                seller=seller_obj,
                category=category_obj,
                description=description,
                price=price,
                stock=stock,
                **product_defaults
            )

            image_path = seed_photo_dir / image_map[image_key]
            if image_path.exists():
                with open(image_path, "rb") as img_file:
                    product.photo.save(image_path.name, File(img_file), save=True)
            else:
                self.stdout.write(self.style.WARNING(f"Missing image: {image_path}"))

            return product

        record1 = create_product(
            name="Fleetwood Mac – Rumours (Vinyl)",
            seller_obj=seller,
            category_obj=record,
            description="Classic 1977 album featuring 'Dreams' and 'Go Your Own Way'. Pressed on high-quality 180g vinyl for superior sound.",
            price=Decimal("24.99"),
            stock=12,
            image_key="Record",
        )

        create_product(
            name="Audio-Technica AT-LP60X Turntable",
            seller_obj=seller,
            category_obj=record_player,
            description="Fully automatic belt-drive turntable with built-in phono preamp. Perfect for beginners and vinyl enthusiasts alike.",
            price=Decimal("149.99"),
            stock=7,
            image_key="Record Player",
        )

        create_product(
            name="Yamaha Stereo Amplifier A-S301",
            seller_obj=seller1,
            category_obj=amp,
            description="Powerful integrated amplifier delivering clear, dynamic audio. Features optical input and subwoofer output.",
            price=Decimal("349.99"),
            stock=5,
            image_key="Amp",
        )

        create_product(
            name="Sony AM/FM Digital Tuner",
            seller_obj=seller1,
            category_obj=tuner,
            description="Compact digital tuner with preset station memory and excellent signal clarity for home audio systems.",
            price=Decimal("89.99"),
            stock=6,
            image_key="Tuner",
        )

        create_product(
            name="Sony WH-1000XM5 Wireless Headphones",
            seller_obj=seller,
            category_obj=headphone,
            description="Industry-leading noise cancellation with premium sound quality and up to 30 hours of battery life.",
            price=Decimal("399.99"),
            stock=9,
            image_key="Headphone",
        )


        address = Address.objects.create(
            user=buyer,
            full_name="Test Buyer",
            street="123 Test St",
            city="Test City",
            state="MS",
            zipcode="39465",
            country="USA",
        )

        order = Order.objects.create(
            buyer=buyer,
            shipping_address=address,
            subtotal=Decimal("10.99"),
            tax_rate=Decimal("10.00"),
            tax=Decimal("1.10"),
            fee=Decimal("6.99"),
            total=Decimal("19.08"),
            status="Completed",
        )

        OrderItem.objects.create(
            order=order,
            product=record1,
            seller=record1.seller,
            quantity=1,
            price_at_purchase=record1.price,
            status="Completed",
        )

        Payment.objects.create(
            user=buyer,
            order=order,
            payment_method="CreditCard",
            payment_status="Completed",
            is_saved=False,
            is_default=False,
            cardholder_name="Test Buyer",
            card_brand="Visa",
            card_last4="1111",
            exp_month="12",
            exp_year="2028",
        )

        order_item = OrderItem.objects.get(order=order, product=record1)
        Payout.objects.create(
            seller=record1.seller,
            order_item=order_item,
            amount=record1.price,
            status="Paid",
            paid_at=timezone.now(),
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded database."))