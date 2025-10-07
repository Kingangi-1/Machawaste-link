"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, WasteItem, Match

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'address', 'password1', 'password2']

class WasteItemForm(forms.ModelForm):
    class Meta:
        model = WasteItem
        fields = ['title', 'description', 'category', 'quantity', 'unit', 'location', 'image']

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['message']
    


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, WasteItem, Match, WasteCategory

class UserRegistrationForm(UserCreationForm):
    # Add better styling and placeholders for registration form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com'})
        self.fields['phone'].widget.attrs.update({'placeholder': '+1234567890'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Your address', 'rows': 3})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'address', 'password1', 'password2']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }

class WasteItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If no categories exist, create a default one
        if not WasteCategory.objects.exists():
            default_category = WasteCategory.objects.create(
                name="General Waste", 
                description="General waste materials"
            )
            self.fields['category'].initial = default_category
        
        # Add CSS classes and placeholders for better UX
        self.fields['title'].widget.attrs.update({
            'placeholder': 'e.g., Plastic Bottles, Cardboard Boxes',
            'class': 'form-input'
        })
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Describe the waste material, condition, and any special instructions...',
            'class': 'form-textarea'
        })
        self.fields['quantity'].widget.attrs.update({
            'placeholder': '0.00',
            'min': '0',
            'step': '0.01',
            'class': 'form-input'
        })
        self.fields['location'].widget.attrs.update({
            'placeholder': 'e.g., 123 Main St, City, State',
            'class': 'form-input'
        })

    class Meta:
        model = WasteItem
        fields = ['title', 'description', 'category', 'quantity', 'unit', 'location', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'unit': forms.Select(choices=[
                ('kg', 'Kilograms (kg)'),
                ('g', 'Grams (g)'), 
                ('lbs', 'Pounds (lbs)'),
                ('pieces', 'Pieces'),
                ('bags', 'Bags'),
                ('bottles', 'Bottles'),
                ('boxes', 'Boxes'),
                ('liters', 'Liters (L)'),
            ], attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-file'}),
        }
        labels = {
            'title': 'Waste Title *',
            'description': 'Description *',
            'category': 'Waste Category *',
            'quantity': 'Quantity *',
            'unit': 'Unit *',
            'location': 'Pickup Location *',
            'image': 'Waste Image (Optional)',
        }

class MatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({
            'placeholder': 'Tell the waste poster about your recycling plans, pickup availability, or any questions...',
            'class': 'form-textarea'
        })
    
    class Meta:
        model = Match
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'message': 'Your Message *',
        }

    """

#bootstrap

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, WasteItem, Match, WasteCategory

class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['class'] += ' form-control-lg'
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'phone', 'address', 'password1', 'password2']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-select'}),
        }

class WasteItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If no categories exist, create a default one
        if not WasteCategory.objects.exists():
            WasteCategory.objects.create(name="General Waste", description="General waste materials")
        
        # Add Bootstrap classes and placeholders to all fields
        for field_name, field in self.fields.items():
            if field_name == 'category' or field_name == 'unit':
                field.widget.attrs['class'] = 'form-select'
                if field_name == 'category':
                    field.empty_label = "Select waste category..."  # Placeholder for select
            elif field_name == 'image':
                field.widget.attrs['class'] = 'form-control file-upload'
            elif field_name == 'description':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 4
                field.widget.attrs['placeholder'] = 'Describe your waste items in detail. Include condition, materials, and any special handling requirements...'
            else:
                field.widget.attrs['class'] = 'form-control'
                
        # Add specific placeholders for each field
        self.fields['title'].widget.attrs['placeholder'] = 'e.g., Plastic Bottles, Old Newspapers, Metal Cans, E-Waste...'
        self.fields['quantity'].widget.attrs['placeholder'] = 'e.g., 5.0'
        self.fields['location'].widget.attrs['placeholder'] = 'e.g., Nairobi CBD, Westlands, Mombasa Island, Kisumu...'

    class Meta:
        model = WasteItem
        fields = ['title', 'description', 'category', 'quantity', 'unit', 'location', 'image']
        widgets = {
            'unit': forms.Select(choices=[
                ('', 'Select unit...'),  # Added placeholder option
                ('kg', 'Kilograms (kg)'),
                ('g', 'Grams (g)'), 
                ('lbs', 'Pounds (lbs)'),
                ('pieces', 'Pieces'),
                ('bags', 'Bags'),
                ('bottles', 'Bottles'),
                ('boxes', 'Boxes'),
                ('liters', 'Liters (L)'),
            ]),
        }

class MatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell the waste poster about your recycling plans...'
        })
    
    class Meta:
        model = Match
        fields = ['message']