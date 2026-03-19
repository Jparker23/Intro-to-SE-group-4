from django.core.management.base import BaseCommand
from shop.models import Product, Category
from accounts.models import User
#file to seed the database with premade values

class Command(BaseCommand):
    help = "Seeds the database with initial data for the Product, Category, and User models"
    
    def handle(self, *args, **options):
        # Clear existing data
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
        
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
        admin.set_password("password123")
        admin.save()
        
        admin1, _ = User.objects.get_or_create(username ="testadmin1", defaults={
            "role": "admin",
            "email": "admin1@test.com",
            "is_staff": True,
        })
        admin1.set_password("password123")
        admin1.save()
        
        buyer, _ = User.objects.get_or_create(username="testbuyer", defaults={
            "role": "buyer",
            "email": "buyer@test.com",
        })
        buyer.set_password("password123")
        buyer.save()
        
        buyer1, _ = User.objects.get_or_create(username="testbuyer1", defaults={
            "role": "buyer",
            "email": "buyer1@test.com",
        })
        buyer1.set_password("password123")
        buyer1.save()
        
        seller, _ = User.objects.get_or_create(username="testseller", defaults={
            "role": "seller",
            "email": "seller@test.com",
        })
        seller.set_password("password123")
        seller.save()
        
        seller1, _ = User.objects.get_or_create(username="testseller1", defaults={
            "role": "seller",
            "email": "seller1@test.com",
        })
        seller1.set_password("password123")
        seller1.save()
        
        # Products
        Product.objects.get_or_create(
            name="record1", seller= seller,
            defaults={
                "category": record,
                "description": "Autofilled example record product",
                "price": 10.99,
                "stock": 5,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="record player1", seller= seller,
            defaults={
                "category": record_player,
                "description": "Autofilled example record player product",
                "price": 30.99,
                "stock": 8,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="amp1", seller= seller1,
            defaults={
                "category": amp,
                "description": "Autofilled example amp product",
                "price": 35.99,
                "stock": 14,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="tuner1", seller= seller1,
            defaults={
                "category": tuner,
                "description": "Autofilled example tuner product",
                "price": 15.99,
                "stock": 1,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="headphone1", seller= seller,
            defaults={
                "category": headphone,
                "description": "Autofilled example headphone product",
                "price": 60.00,
                "stock": 5,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="cd1", seller= seller1,
            defaults={
                "category": cd,
                "description": "Autofilled example cd product",
                "price": 6.99,
                "stock": 11,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        Product.objects.get_or_create(
            name="cleaner kit1", seller= seller,
            defaults={
                "category": cleaning_kit,
                "description": "Autofilled example cleaning kit product",
                "price": 14.99,
                "stock": 9,
                "is_active": True,
                "is_approved": True,
                "approval_status": "Approved",
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database.'))