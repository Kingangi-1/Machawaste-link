from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    USER_TYPES = (
        ('household', 'Household'),
        ('farmer', 'Farmer'),
        ('collector', 'Waste Collector (Youth/Women)'),
        ('recycler', 'Recycler/Processor'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='household')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="Location in Machakos County")
    digital_credits = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class WasteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

"""
class WasteItem(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('pending', 'Pending Pickup'),
        ('collected', 'Collected'),
    )
    
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waste_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(WasteCategory, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='kg')
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titlesssssssssssssssssssssssssssssssssssssssssssss} - {self.poster.username}"
    
"""
class WasteItem(models.Model):
    WASTE_TYPES = (
        ('plastic', 'Plastic'),
        ('paper', 'Paper/Cardboard'),
        ('metal', 'Metal'),
        ('glass', 'Glass'),
        ('organic', 'Organic/Food Waste'),
        ('agricultural', 'Agricultural Residues'),
        ('e-waste', 'E-Waste'),
        ('textile', 'Textile'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('pending', 'Pending Pickup'),
        ('collected', 'Collected'),
        ('recycled', 'Recycled'),
    )
    
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='waste_items')
    title = models.CharField(max_length=200)
    description = models.TextField()
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPES, default='plastic')
    category = models.ForeignKey(WasteCategory, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='kg')
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='waste_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    credits_earned = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.poster.username}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate credits based on waste type and quantity
        if self.status == 'collected' and self.credits_earned == 0:
            credit_rates = {
                'plastic': 2.0,    # 2 credits per kg
                'paper': 1.5,      # 1.5 credits per kg  
                'metal': 3.0,      # 3 credits per kg
                'glass': 1.0,      # 1 credit per kg
                'organic': 0.5,    # 0.5 credits per kg
                'agricultural': 0.3, # 0.3 credits per kg
                'e-waste': 5.0,    # 5 credits per kg
                'textile': 1.0,    # 1 credit per kg
                'other': 1.0,      # 1 credit per kg
            }
            rate = credit_rates.get(self.waste_type, 1.0)
            self.credits_earned = self.quantity * rate
            
            # Add credits to user
            if self.poster:
                self.poster.digital_credits += self.credits_earned
                self.poster.save()
        
        super().save(*args, **kwargs)


class Match(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    waste_item = models.ForeignKey(WasteItem, on_delete=models.CASCADE)
    collector = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['waste_item', 'collector']
    
    def __str__(self):
        return f"Match: {self.waste_item.title} - {self.collector.username}"