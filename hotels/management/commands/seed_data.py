from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from hotels.models import Hotel, HotelPhoto, Review, Booking
from decimal import Decimal
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Seed the database with dummy data"

    def handle(self, *args, **kwargs):
        # 1️⃣ Users
        if not User.objects.filter(username='alice').exists():
            user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
            Profile.objects.create(user=user1, wallet=Decimal('1000.00'))

        if not User.objects.filter(username='bob').exists():
            user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')
            Profile.objects.create(user=user2, wallet=Decimal('500.00'))

        users = list(User.objects.all())

        # 2️⃣ Hotels
        hotel_names = ['Grand Palace', 'Ocean View Resort', 'Mountain Retreat', 'City Lights Hotel', 'Sunset Inn']
        hotels = []
        for name in hotel_names:
            hotel = Hotel.objects.create(
                name=name,
                address=f'{random.randint(100,999)} Example Street, City',
                description=f'This is a beautiful hotel named {name}. Enjoy your stay!',
                main_image=f'hotel_photos/dummy{random.randint(1,3)}.jpg'
            )
            hotels.append(hotel)

        # 3️⃣ Hotel Photos
        for hotel in hotels:
            for i in range(1, 4):
                HotelPhoto.objects.create(
                    hotel=hotel,
                    image=f'hotel_photos/dummy{i}.jpg'
                )

        # 4️⃣ Reviews
        comments = ["Amazing stay!", "Very comfortable.", "Will visit again!", "Not bad, could be better.", "Loved the service!"]
        for hotel in hotels:
            for user in users:
                Review.objects.create(
                    hotel=hotel,
                    user=user,
                    rating=random.randint(3,5),
                    comment=random.choice(comments)
                )

        # 5️⃣ Bookings
        for hotel in hotels:
            for user in users:
                check_in = datetime.today().date() + timedelta(days=random.randint(1,10))
                check_out = check_in + timedelta(days=random.randint(1,5))
                Booking.objects.create(
                    user=user,
                    hotel=hotel,
                    check_in=check_in,
                    check_out=check_out,
                    total_price=Decimal(random.randint(100,500)),
                    confirmed=True
                )

        self.stdout.write(self.style.SUCCESS("✅ Dummy data created successfully!"))
