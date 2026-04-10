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
            ("buyer", "buyer.buying@example.com", "Buyer Buying"),
            ("buyer1", "buyer.1@example.com", "Buyer One"),
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
            "Record Player": "product_photos/recordplayer.jpg",
            "Amp": "product_photos/amp.jpg",
            "Tuner": "product_photos/tuner.jpg",
            "Headphone": "product_photos/headphones.jpg",
            "CD": "product_photos/testcd.jpg",
            "Cleaning Kit": "product_photos/cleaning-kit-product-photo.jpg",
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

        product_descriptions = {
            "Fleetwood Mac – Rumours": "Fleetwood Mac’s Rumours is a classic soft rock record with warm vocals, polished production, and a smooth mix of heartbreak and melody. A great pick for listeners who want something timeless and easy to keep on repeat.",
            "Abbey Road": "Abbey Road by The Beatles blends melodic rock, layered harmonies, and some of the band’s most recognizable songwriting. This record has a clean, balanced sound that fits both casual listening and a serious vinyl setup.",
            "Dark Side of the Moon": "Pink Floyd’s Dark Side of the Moon has a deep, atmospheric sound with rich guitars, synth textures, and seamless transitions from track to track. A strong choice for anyone building a serious record collection.",
            "Hotel California": "Hotel California by the Eagles delivers polished classic rock with crisp guitar work, laid-back vocals, and a smooth West Coast sound. It is an easy album to throw on when you want something familiar and well produced.",
            "Thriller": "Michael Jackson’s Thriller mixes pop, funk, and R&B with sharp production and huge energy. This is one of those records that sounds lively on almost any setup and works well for both collectors and casual buyers.",
            "Back in Black": "AC/DC’s Back in Black is a hard rock staple with punchy riffs, driving drums, and a raw, energetic sound. A great record for buyers who want something louder, heavier, and instantly recognizable.",
            "Led Zeppelin IV": "Led Zeppelin IV brings together hard rock, folk influence, and a powerful analog sound. The record has strong dynamics and a full-bodied feel that makes it a favorite for classic rock fans.",
            "Born in the U.S.A.": "Bruce Springsteen’s Born in the U.S.A. has an anthemic rock sound with big drums, bright synths, and strong vocal presence. A solid addition for buyers who like heartland rock with a lot of personality.",

            "Audio-Technica AT-LP60X": "A dependable entry-level turntable with fully automatic operation and a clean, user-friendly design. Great for buyers who want an easy starter record player without a complicated setup.",
            "Victrola Vintage 3-Speed": "A compact 3-speed record player with a vintage-inspired look and simple controls. Best for casual listening, smaller spaces, or buyers who want an affordable all-in-one option.",
            "Sony PS-LX310BT": "A sleek belt-drive turntable with Bluetooth support and a modern, minimal design. Good for buyers who want the flexibility of wireless listening while still enjoying vinyl playback.",
            "Fluance RT81": "A more premium record player with a solid wood finish, balanced sound, and a smoother listening experience. A nice fit for buyers looking to step up from basic starter models.",
            "Deluxe Turntable Mat": "A simple upgrade piece that helps protect records and gives a turntable setup a more finished look. Good for users who want to improve daily use without spending much.",

            "Sony Stereo Receiver": "A reliable stereo receiver with clean output and enough power for a home listening setup. A solid match for buyers building a straightforward audio system.",
            "Hi-Fi Receiver": "A good midrange receiver designed for balanced sound and everyday listening. Works well for music lovers who want dependable performance without too much complexity.",
            "Speaker Cable Pack": "Basic speaker cable pack for connecting home audio gear quickly and easily. A practical add-on for buyers putting together a receiver and speaker setup.",
            "Pioneer Home Audio Receiver": "A versatile home audio receiver with strong brand recognition and a clean sound profile. Great for buyers who want a dependable centerpiece for their listening space.",
            "Compact Stereo Amplifier": "A smaller amplifier that fits neatly into tighter setups while still delivering clear, consistent sound. Good for apartments, desks, or smaller shelves.",

            "Yamaha Natural Sound Tuner": "A tuner designed for clean FM and AM playback with Yamaha’s classic understated style. A nice add-on for buyers who want traditional radio in their audio stack.",
            "Digital FM/AM Tuner": "Straightforward digital tuner with simple controls and dependable station access. Best for buyers who want a practical and affordable radio component.",
            "Classic Stereo Tuner": "A traditional stereo tuner with a familiar look and a simple listening experience. A good pick for vintage audio fans and buyers rounding out a stack setup.",

            "Sony WH-1000XM4": "Popular wireless headphones known for comfort, strong noise canceling, and a smooth overall sound. A strong choice for everyday listening, travel, and longer sessions.",
            "Bose QuietComfort": "Comfort-focused headphones with soft ear cushions, clear audio, and reliable noise reduction. Great for buyers who want something easy to wear for extended use.",
            "Studio Monitor Headphones": "Closed-back monitor headphones with a straightforward sound profile that works well for detail listening and casual home use. A solid budget-friendly option.",
            "Audio-Technica M50x": "Well-known monitor headphones with clear mids, crisp highs, and a more detailed sound than typical consumer models. Good for buyers who want a more studio-style listening experience.",
            "Wireless Bass Headphones": "Wireless headphones tuned with a stronger low end and an easy everyday fit. A nice option for buyers who prefer a fuller, more energetic sound.",

            "Greatest Hits Collection": "A dependable CD pick for buyers who want familiar tracks in one place without having to track down a full catalog. Great for casual listening and quick gifting.",
            "Classic Rock Essentials": "A CD collection built around recognizable classic rock favorites with broad appeal. A simple pickup for buyers who want an easy playlist-style option.",
            "Jazz Favorites Volume 1": "A relaxed jazz compilation with a smooth, easygoing feel that works well for background listening or quieter setups. Nice for buyers wanting something more mellow.",
            "Acoustic Sessions": "A softer acoustic collection with warm vocals and stripped-back arrangements. Great for listeners who prefer a more intimate, laid-back sound.",

            "Vinyl Cleaning Brush": "A simple record cleaning brush for knocking dust off before playback. A practical basic accessory that helps keep records and stylus contact cleaner.",
            "Turntable Care Set": "A complete little care kit for buyers who want to keep records, stylus, and surfaces in better shape. A smart add-on for anyone using vinyl regularly.",
            "Stylus Cleaning Gel": "Easy stylus cleaning gel designed to lift dust and buildup with very little effort. Good for regular maintenance and helping playback stay cleaner.",
            "Record Sleeve Pack": "Protective sleeve pack for storing records more neatly and reducing wear over time. A useful low-cost pickup for collectors trying to keep albums in good condition.",
            "Anti-Static Record Cloth": "Soft anti-static cloth meant for quick wipe-downs before and after listening. Handy for keeping dust down in everyday use.",
            "Portable Record Case": "A portable storage case for keeping a smaller vinyl collection protected and easy to carry. A nice fit for casual collectors or buyers who like organized storage.",
        }

        fallback_descriptions = [
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
                description=product_descriptions.get(name, random.choice(fallback_descriptions)),
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