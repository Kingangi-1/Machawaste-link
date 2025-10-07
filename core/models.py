from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


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

    def add_credits(self, amount, reason=""):
        """Add credits to user account and create transaction record"""
        print(f"Adding credits: {amount} for user: {self.username}")  # Debug

        # Ensure amount is Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        print(f"User credits before: {self.digital_credits}")  # Debug

        self.digital_credits += amount
        self.save()

        # Create transaction record
        transaction = CreditTransaction.objects.create(
            user=self,
            amount=amount,
            transaction_type='credit',
            reason=reason
        )

        print(f"User credits after: {self.digital_credits}")  # Debug
        print(f"Transaction created: {transaction}")  # Debug

        return True

    def deduct_credits(self, amount, reason=""):
        """Deduct credits from user account if sufficient balance"""
        if self.digital_credits >= amount:
            self.digital_credits -= amount
            self.save()
            CreditTransaction.objects.create(
                user=self,
                amount=amount,
                transaction_type='debit',
                reason=reason
            )
            return True
        return False

    def get_credit_balance(self):
        """Get current credit balance"""
        return self.digital_credits

    def get_transaction_history(self):
        """Get user's credit transaction history"""
        return self.credit_transactions.all()


class CreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type}: {self.amount} - {self.reason}"


class WasteCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


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
    estimated_credits = models.DecimalField(max_digits=8, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.poster.username}"

    def calculate_estimated_credits(self):
        """Calculate estimated credits based on waste type and quantity"""
        credit_rates = {
            'plastic': 2.0,
            'paper': 1.5,
            'metal': 3.0,
            'glass': 1.0,
            'organic': 0.5,
            'agricultural': 0.3,
            'e-waste': 5.0,
            'textile': 1.0,
            'other': 1.0,
        }
        rate = credit_rates.get(self.waste_type, 1.0)

        rate_decimal = Decimal(str(rate))
        self.estimated_credits = self.quantity * rate_decimal
        return self.estimated_credits

    def award_credits(self):
        """Award credits to the poster when waste is collected"""
        print(f"Awarding credits for: {self.title}, Status: {self.status}, Credits earned: {self.credits_earned}")  # Debug

        if self.status == 'collected' and self.credits_earned == 0:
            # Use the estimated credits or calculate fresh
            if self.estimated_credits > 0:
                credit_amount = self.estimated_credits
            else:
                credit_amount = self.calculate_estimated_credits()

            print(f"Credit amount to award: {credit_amount}")  # Debug

            self.credits_earned = credit_amount

            # Add credits to user account
            success = self.poster.add_credits(
                credit_amount,
                reason=f"Credits earned for waste collection: {self.title}"
            )

            print(f"Add credits success: {success}")  # Debug
            self.save()
            return credit_amount

        print("No credits awarded - conditions not met")  # Debug
        return 0

    def save(self, *args, **kwargs):
        # Calculate estimated credits when creating/updating waste item
        if not self.pk or 'quantity' in kwargs.get('update_fields', []) or 'waste_type' in kwargs.get('update_fields', []):
            self.calculate_estimated_credits()

        # Auto-award credits when status changes to collected
        if self.status == 'collected' and self.credits_earned == 0:
            self.award_credits()

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

    def accept_match(self):
        """Accept the match and update waste item status"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.waste_item.status = 'pending'
            self.waste_item.save()
            self.save()
            return True
        return False

    
    def complete_match(self):
        """Complete the match and award credits"""
        print(f"DEBUG complete_match: Starting for match {self.id}, status: {self.status}")
    
        if self.status == 'accepted':
            self.status = 'completed'
            self.waste_item.status = 'collected'
        
            print(f"DEBUG: Status changed - match: {self.status}, waste: {self.waste_item.status}")
        
        # Award credits to the waste poster
            credits_awarded = self.waste_item.award_credits()
        
            print(f"DEBUG: Credits awarded: {credits_awarded}")
        
            self.waste_item.save()
            self.save()
        
            print(f"DEBUG: Match and waste item saved successfully")
            return True, credits_awarded
    
        print(f"DEBUG: Cannot complete - match status is {self.status}")
        return False, 0