from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import random
from datetime import timedelta
from django.utils import timezone
from core.models import WasteItem, WasteCategory, Match

class Command(BaseCommand):
    help = "Create sample data for testing Machawaste Link"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of sample users to create (default: 5)'
        )
        parser.add_argument(
            '--items',
            type=int, 
            default=10,
            help='Number of sample waste items to create (default: 10)'
        )

    def handle(self, *args, **options):
        clear_existing = options.get('clear')
        num_users = options.get('users')
        num_items = options.get('items')
        
        self.stdout.write("=== Creating Sample Data for Machawaste Link ===")
        
        # Clear existing sample data if requested
        if clear_existing:
            self.clear_sample_data()
        
        # Create sample data
        users = self.create_sample_users(num_users)
        categories = WasteCategory.objects.all()
        waste_items = self.create_sample_waste_items(num_items, users, categories)
        self.create_sample_matches(waste_items, users)
        
        self.stdout.write(self.style.SUCCESS(
            f"✅ Sample data created: {len(users)} users, {len(waste_items)} waste items"
        ))

    def clear_sample_data(self):
        """Clear existing sample data"""
        self.stdout.write("Clearing existing sample data...")
        
        # Delete sample users (excluding superusers)
        User = get_user_model()
        sample_users = User.objects.filter(
            username__startswith='sample_',
            is_superuser=False
        )
        deleted_count = sample_users.count()
        sample_users.delete()
        
        # Delete sample waste items
        sample_items = WasteItem.objects.filter(title__startswith='Sample Waste -')
        sample_items.delete()
        
        self.stdout.write(f"Cleared {deleted_count} sample users and waste items")

    def create_sample_users(self, num_users):
        """Create sample users with different roles"""
        User = get_user_model()
        users = []
        
        user_types = ['poster', 'collector', 'recycler']
        locations = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
        
        for i in range(num_users):
            user_type = random.choice(user_types)
            username = f"sample_{user_type}_{i+1}"
            email = f"{username}@example.com"
            
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'user_type': user_type,
                        'location': random.choice(locations),
                        'digital_credits': random.randint(0, 1000)
                    }
                )
                
                if created:
                    user.set_password('password123')  # Simple password for testing
                    user.save()
                    users.append(user)
                    self.stdout.write(f"✅ Created user: {username} ({user_type})")
                else:
                    users.append(user)
                    self.stdout.write(f"⚠️ User exists: {username}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating user {username}: {e}"))
        
        return users

    def create_sample_waste_items(self, num_items, users, categories):
        """Create sample waste items"""
        waste_items = []
        status_choices = ['available', 'pending', 'collected']
        units = ['kg', 'pieces', 'liters']
        
        waste_descriptions = [
            "Household waste ready for collection",
            "Clean and sorted materials",
            "Industrial by-products available",
            "Organic waste from restaurant",
            "Construction site materials",
            "Office paper and cardboard",
            "Electronic waste from upgrade",
            "Plastic packaging materials",
            "Metal scraps from workshop",
            "Glass bottles from bar"
        ]
        
        locations = [
            "Nairobi CBD", "Westlands", "Karen", "Eastleigh", "South B",
            "Mombasa Island", "Nyali", "Bamburi", "Likoni",
            "Kisumu Town", "Milimani", "Kanyakwar"
        ]
        
        for i in range(num_items):
            try:
                # Select random user, category, and status
                poster = random.choice([u for u in users if u.user_type == 'poster'])
                category = random.choice(categories)
                status = random.choice(status_choices)
                
                # Create waste item
                waste_item = WasteItem.objects.create(
                    poster=poster,
                    title=f"Sample Waste - {category.name} #{i+1}",
                    description=random.choice(waste_descriptions),
                    waste_type=category.name.lower().split()[0],  # Simple mapping
                    category=category,
                    quantity=round(random.uniform(1.0, 50.0), 2),
                    unit=random.choice(units),
                    location=random.choice(locations),
                    status=status,
                    credits_earned=round(random.uniform(5.0, 100.0), 2) if status == 'collected' else 0
                )
                
                # Set created_at to random past date for realism
                days_ago = random.randint(0, 30)
                waste_item.created_at = timezone.now() - timedelta(days=days_ago)
                waste_item.save()
                
                waste_items.append(waste_item)
                self.stdout.write(f"✅ Created waste item: {waste_item.title}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating waste item: {e}"))
        
        return waste_items

    def create_sample_matches(self, waste_items, users):
        """Create sample matches between collectors and waste items"""
        collectors = [u for u in users if u.user_type == 'collector']
        matches_created = 0
        
        for waste_item in waste_items:
            if waste_item.status == 'available' and collectors:
                collector = random.choice(collectors)
                
                try:
                    match, created = Match.objects.get_or_create(
                        waste_item=waste_item,
                        collector=collector,
                        defaults={
                            'status': random.choice(['pending', 'accepted']),
                            'message': f"Interested in collecting your {waste_item.waste_type} waste"
                        }
                    )
                    
                    if created:
                        matches_created += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error creating match: {e}"))
        
        self.stdout.write(f"✅ Created {matches_created} sample matches")