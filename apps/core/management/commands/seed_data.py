"""
Management command to seed the database with test data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta

from apps.users.models import User, INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS, INVITATION_PRIVACY_NONE
from apps.geography.models import Country, City
from apps.events.models import Event, EVENT_STATUS_PUBLISHED, EVENT_STATUS_DRAFT, EVENT_STATUS_COMPLETED, INVITATION_PERM_PARTICIPANTS, INVITATION_PERM_ADMINS, INVITATION_PERM_ORGANIZER
from apps.categories.models import Category
from apps.friendships.models import Friendship, FRIENDSHIP_STATUS_ACCEPTED, FRIENDSHIP_STATUS_PENDING
from apps.participants.models import EventParticipant, PARTICIPANT_STATUS_ACCEPTED, PARTICIPANT_STATUS_PENDING
from apps.comments.models import EventComment
from apps.media.models import EventPhoto

fake = Faker()


class Command(BaseCommand):
    help = 'Fill database with realistic test data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Clearing existing data...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('🌱 Starting database seeding...'))
        
        try:
            with transaction.atomic():
                self.stdout.write('🌍 Seeding countries and cities...')
                countries = self.create_countries()
                cities = self.create_cities(countries)
                
                self.stdout.write('👥 Seeding users...')
                users = self.create_users(60)
                
                self.stdout.write('🏷️  Seeding categories...')
                categories = self.create_categories()
                
                self.stdout.write('🎉 Seeding events...')
                events = self.create_events(users, cities, categories, 40)
                
                self.stdout.write('🤝 Seeding friendships...')
                self.create_friendships(users, 150)
                
                self.stdout.write('✅ Seeding participants...')
                self.create_participants(events, users)
                
                self.stdout.write('💬 Seeding comments...')
                self.create_comments(events, users, 200)
                
                self.stdout.write('📸 Seeding photos...')
                self.create_photos(events, users, 100)
                
                self.stdout.write(self.style.SUCCESS('✨ Database seeded successfully!'))
                self.print_statistics()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during seeding: {str(e)}'))
            raise
    
    def clear_data(self):
        """Clear all existing data from the database."""
        EventPhoto.objects.all().delete()
        EventComment.objects.all().delete()
        EventParticipant.objects.all().delete()
        Friendship.objects.all().delete()
        Event.objects.all().delete()
        Category.objects.all().delete()
        City.objects.all().delete()
        Country.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('✓ Data cleared'))
    
    def create_countries(self):
        """Create realistic country data."""
        countries_data = [
            ('Kazakhstan', 'KZ'),
            ('United States', 'US'),
            ('United Kingdom', 'GB'),
            ('Germany', 'DE'),
            ('France', 'FR'),
            ('Spain', 'ES'),
            ('Italy', 'IT'),
            ('Russia', 'RU'),
            ('Japan', 'JP'),
            ('South Korea', 'KR'),
            ('Canada', 'CA'),
            ('Australia', 'AU'),
            ('Brazil', 'BR'),
            ('Mexico', 'MX'),
            ('India', 'IN'),
            ('China', 'CN'),
            ('Turkey', 'TR'),
            ('Netherlands', 'NL'),
            ('Poland', 'PL'),
            ('Sweden', 'SE'),
        ]
        
        countries = []
        for name, code in countries_data:
            country, created = Country.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            countries.append(country)
            if created:
                self.stdout.write(f'  ✓ Created country: {name}')
        
        return countries
    
    def create_cities(self, countries):
        """Create realistic city data for each country."""
        cities_data = {
            'KZ': ['Almaty', 'Astana', 'Shymkent', 'Karaganda', 'Aktobe', 'Taraz', 'Pavlodar'],
            'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'San Francisco', 'Seattle', 'Boston', 'Miami'],
            'GB': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Edinburgh', 'Glasgow', 'Bristol'],
            'DE': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 'Dresden'],
            'FR': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Bordeaux', 'Strasbourg'],
            'ES': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao', 'Malaga'],
            'IT': ['Rome', 'Milan', 'Naples', 'Turin', 'Florence', 'Venice'],
            'RU': ['Moscow', 'Saint Petersburg', 'Novosibirsk', 'Yekaterinburg', 'Kazan'],
            'JP': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo'],
            'KR': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon'],
            'CA': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
            'AU': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
            'BR': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador'],
            'MX': ['Mexico City', 'Guadalajara', 'Monterrey', 'Cancún'],
            'IN': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'],
            'CN': ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen', 'Chengdu'],
            'TR': ['Istanbul', 'Ankara', 'Izmir', 'Antalya'],
            'NL': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht'],
            'PL': ['Warsaw', 'Krakow', 'Wroclaw', 'Gdansk'],
            'SE': ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala'],
        }
        
        cities = []
        country_dict = {c.code: c for c in countries}
        
        for country_code, city_names in cities_data.items():
            if country_code in country_dict:
                country = country_dict[country_code]
                for city_name in city_names:
                    city, created = City.objects.get_or_create(
                        name=city_name,
                        country=country
                    )
                    cities.append(city)
        
        self.stdout.write(f'  ✓ Created {len(cities)} cities')
        return cities
    
    def create_users(self, count):
        """Create diverse user profiles."""
        users = []
        privacy_choices = [INVITATION_PRIVACY_EVERYONE, INVITATION_PRIVACY_FRIENDS, INVITATION_PRIVACY_NONE]
        
        # Create a superuser first
        superuser, created = User.objects.get_or_create(
            email='admin@letsmeetup.com',
            defaults={
                'name': 'Admin User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            superuser.set_password('admin123')
            superuser.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Created superuser: admin@letsmeetup.com / admin123'))
        
        users.append(superuser)
        
        # Create regular users
        for i in range(count):
            name = fake.name()
            email = fake.email()
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                email = f"{fake.user_name()}_{i}@example.com"
            
            user = User.objects.create_user(
                email=email,
                name=name,
                password='password123',
                invitation_privacy=random.choice(privacy_choices),
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            users.append(user)
        
        self.stdout.write(f'  ✓ Created {len(users)} users')
        return users
    
    def create_categories(self):
        """Create event categories."""
        category_names = [
            'Sports & Fitness',
            'Technology',
            'Business & Professional',
            'Arts & Culture',
            'Food & Drink',
            'Music',
            'Health & Wellness',
            'Education',
            'Outdoor & Adventure',
            'Gaming',
            'Social Activities',
            'Photography',
            'Travel',
            'Language & Culture',
            'Volunteering',
            'Books & Reading',
            'Movies & Film',
            'Dance',
            'Crafts',
            'Pets & Animals',
        ]
        
        categories = []
        for name in category_names:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'slug': name.lower().replace(' & ', '-').replace(' ', '-')}
            )
            categories.append(category)
        
        self.stdout.write(f'  ✓ Created {len(categories)} categories')
        return categories
    
    def create_events(self, users, cities, categories, count):
        """Create diverse events with realistic data."""
        events = []
        statuses = [EVENT_STATUS_PUBLISHED] * 7 + [EVENT_STATUS_DRAFT, EVENT_STATUS_COMPLETED]
        invitation_perms = [INVITATION_PERM_PARTICIPANTS] * 6 + [INVITATION_PERM_ADMINS] * 3 + [INVITATION_PERM_ORGANIZER]
        
        event_titles = [
            'Weekend Hiking Adventure',
            'Tech Meetup: AI & Machine Learning',
            'Photography Walk in the City',
            'Board Game Night',
            'Yoga in the Park',
            'Startup Networking Event',
            'Language Exchange Meetup',
            'Book Club Discussion',
            'Live Music Evening',
            'Cooking Class: Italian Cuisine',
            'Marathon Training Group',
            'Art Gallery Opening',
            'Coffee & Code Session',
            'Volunteer Park Cleanup',
            'Dance Salsa Workshop',
            'Film Screening & Discussion',
            'Rock Climbing Beginners',
            'Business Pitch Practice',
            'Photography Portfolio Review',
            'Gaming Tournament',
            'Wine Tasting Evening',
            'Meditation & Mindfulness',
            'Street Food Tour',
            'Tech Conference Afterparty',
            'Cycling Group Ride',
            'Stand-up Comedy Night',
            'Pottery Workshop',
            'Outdoor Movie Night',
            'Hackathon Weekend',
            'Farmers Market Walk',
            'Karaoke Night',
            'Chess Tournament',
            'Beach Volleyball',
            'Craft Beer Tasting',
            'Sunrise Mountain Hike',
            'Poetry Reading Event',
            'Escape Room Challenge',
            'Picnic in the Park',
            'Photography Basics Workshop',
            'Networking Brunch',
        ]
        
        for i in range(count):
            organizer = random.choice(users)
            city = random.choice(cities)
            
            # Generate date (50% future, 30% recent past, 20% far past)
            rand = random.random()
            if rand < 0.5:
                # Future events
                days_ahead = random.randint(1, 90)
                event_date = timezone.now() + timedelta(days=days_ahead, hours=random.randint(9, 20))
                status = random.choice([EVENT_STATUS_PUBLISHED, EVENT_STATUS_DRAFT])
            elif rand < 0.8:
                # Recent past
                days_ago = random.randint(1, 30)
                event_date = timezone.now() - timedelta(days=days_ago, hours=random.randint(9, 20))
                status = EVENT_STATUS_COMPLETED
            else:
                # Far past
                days_ago = random.randint(31, 365)
                event_date = timezone.now() - timedelta(days=days_ago, hours=random.randint(9, 20))
                status = EVENT_STATUS_COMPLETED
            
            title = random.choice(event_titles)
            
            event = Event.objects.create(
                title=f"{title} #{i+1}",
                description=fake.paragraph(nb_sentences=5),
                address=fake.street_address(),
                date=event_date,
                status=status,
                invitation_perm=random.choice(invitation_perms),
                max_participants=random.choice([None, None, 10, 15, 20, 25, 30, 50]),
                organizer=organizer,
                country=city.country,
                city=city,
            )
            
            # Assign 1-3 categories
            event_categories = random.sample(categories, random.randint(1, 3))
            event.categories.set(event_categories)
            
            events.append(event)
        
        self.stdout.write(f'  ✓ Created {len(events)} events')
        return events
    
    def create_friendships(self, users, count):
        """Create friendship relationships."""
        created_count = 0
        attempts = 0
        max_attempts = count * 3
        
        while created_count < count and attempts < max_attempts:
            attempts += 1
            sender = random.choice(users)
            receiver = random.choice(users)
            
            if sender == receiver:
                continue
            
            # Check if friendship already exists
            if Friendship.objects.filter(
                sender=sender,
                receiver=receiver
            ).exists() or Friendship.objects.filter(
                sender=receiver,
                receiver=sender
            ).exists():
                continue
            
            status = random.choice([FRIENDSHIP_STATUS_ACCEPTED] * 7 + [FRIENDSHIP_STATUS_PENDING] * 3)
            
            Friendship.objects.create(
                sender=sender,
                receiver=receiver,
                status=status
            )
            created_count += 1
        
        self.stdout.write(f'  ✓ Created {created_count} friendships')
    
    def create_participants(self, events, users):
        """Create event participants."""
        created_count = 0
        
        for event in events:
            # Skip creating participant for organizer - they're automatically a participant
            # according to the model's validation logic
            
            # Add random participants (excluding organizer)
            num_participants = random.randint(3, 15)
            if event.max_participants:
                num_participants = min(num_participants, event.max_participants)
            
            potential_participants = [u for u in users if u != event.organizer]
            participants = random.sample(
                potential_participants,
                min(num_participants, len(potential_participants))
            )
            
            for user in participants:
                if not EventParticipant.objects.filter(event=event, user=user).exists():
                    status = random.choice([PARTICIPANT_STATUS_ACCEPTED] * 8 + [PARTICIPANT_STATUS_PENDING] * 2)
                    is_admin = random.random() < 0.1  # 10% chance to be admin
                    
                    EventParticipant.objects.create(
                        event=event,
                        user=user,
                        status=status,
                        is_admin=is_admin if status == PARTICIPANT_STATUS_ACCEPTED else False,
                        invited_by=random.choice([event.organizer, None])
                    )
                    created_count += 1
        
        self.stdout.write(f'  ✓ Created {created_count} event participants')
    
    def create_comments(self, events, users, count):
        """Create event comments with threaded replies."""
        comments = []
        created_count = 0
        
        # Create top-level comments
        for _ in range(int(count * 0.7)):
            event = random.choice(events)
            
            # Only participants and organizer can comment
            participants = EventParticipant.objects.filter(
                event=event,
                status=PARTICIPANT_STATUS_ACCEPTED
            ).select_related('user')
            
            if not participants.exists():
                continue
            
            user = random.choice([p.user for p in participants])
            
            comment = EventComment.objects.create(
                event=event,
                user=user,
                content=fake.paragraph(nb_sentences=random.randint(1, 4)),
            )
            comments.append(comment)
            created_count += 1
        
        # Create replies
        for _ in range(int(count * 0.3)):
            if not comments:
                break
            
            parent_comment = random.choice(comments)
            event = parent_comment.event
            
            participants = EventParticipant.objects.filter(
                event=event,
                status=PARTICIPANT_STATUS_ACCEPTED
            ).select_related('user')
            
            if not participants.exists():
                continue
            
            user = random.choice([p.user for p in participants])
            
            reply = EventComment.objects.create(
                event=event,
                user=user,
                parent=parent_comment,
                content=fake.paragraph(nb_sentences=random.randint(1, 3)),
            )
            comments.append(reply)
            created_count += 1
        
        self.stdout.write(f'  ✓ Created {created_count} comments')
    
    def create_photos(self, events, users, count):
        """Create event photos."""
        created_count = 0
        photo_urls = [
            'https://picsum.photos/800/600?random=',
            'https://images.unsplash.com/photo-',
        ]
        
        for event in events[:min(len(events), count // 2)]:
            # Each event gets 1-5 photos
            num_photos = random.randint(1, 5)
            
            participants = EventParticipant.objects.filter(
                event=event,
                status=PARTICIPANT_STATUS_ACCEPTED
            ).select_related('user')
            
            if not participants.exists():
                continue
            
            for i in range(num_photos):
                uploader = random.choice([p.user for p in participants])
                
                photo = EventPhoto.objects.create(
                    event=event,
                    uploaded_by=uploader,
                    url=f"{random.choice(photo_urls)}{random.randint(1000, 9999)}",
                    caption=fake.sentence() if random.random() > 0.5 else None,
                    is_cover=(i == 0)  # First photo is cover
                )
                created_count += 1
        
        self.stdout.write(f'  ✓ Created {created_count} photos')
    
    def print_statistics(self):
        """Print database statistics."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 Database Statistics:'))
        self.stdout.write('='*50)
        self.stdout.write(f'  Countries: {Country.objects.count()}')
        self.stdout.write(f'  Cities: {City.objects.count()}')
        self.stdout.write(f'  Users: {User.objects.count()}')
        self.stdout.write(f'  Categories: {Category.objects.count()}')
        self.stdout.write(f'  Events: {Event.objects.count()}')
        self.stdout.write(f'  Friendships: {Friendship.objects.count()}')
        self.stdout.write(f'  Participants: {EventParticipant.objects.count()}')
        self.stdout.write(f'  Comments: {EventComment.objects.count()}')
        self.stdout.write(f'  Photos: {EventPhoto.objects.count()}')
        self.stdout.write('='*50 + '\n')