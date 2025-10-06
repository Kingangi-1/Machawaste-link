from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WasteItem, Match, WasteCategory, User
from .forms import UserRegistrationForm, WasteItemForm, MatchForm

def home(request):
    try:
        recent_waste = WasteItem.objects.filter(status='available').order_by('-created_at')[:6]
    except:
        recent_waste = []
    
    return render(request, 'core/home.html', {'recent_waste': recent_waste})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})
@login_required
def dashboard(request):
    user_waste = WasteItem.objects.filter(poster=request.user)
    matches_received = Match.objects.filter(waste_item__poster=request.user)
    
    # Different views based on user type
    if request.user.user_type in ['collector', 'recycler']:
        available_waste = WasteItem.objects.filter(status='available').exclude(poster=request.user)
        matches_made = Match.objects.filter(collector=request.user)
        
        # For collectors: show nearby waste
        if request.user.location:
            available_waste = available_waste.filter(location__icontains=request.user.location)
    else:
        available_waste = None
        matches_made = None
    
    # Statistics for dashboard
    total_waste_posted = user_waste.count()
    total_credits_earned = sum([waste.credits_earned for waste in user_waste])
    pending_matches = matches_received.filter(status='pending').count()
    
    context = {
        'user_waste': user_waste,
        'matches_received': matches_received,
        'available_waste': available_waste,
        'matches_made': matches_made,
        'total_waste_posted': total_waste_posted,
        'total_credits_earned': total_credits_earned,
        'pending_matches': pending_matches,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def post_waste(request):
    if request.method == 'POST':
        form = WasteItemForm(request.POST, request.FILES)
        if form.is_valid():
            waste_item = form.save(commit=False)
            waste_item.poster = request.user
            waste_item.save()
            messages.success(request, 'Waste item posted successfully!')
            return redirect('dashboard')
    else:
        form = WasteItemForm()
    return render(request, 'core/post_waste.html', {'form': form})

@login_required
def waste_list(request):
    try:
        waste_items = WasteItem.objects.filter(status='available').order_by('-created_at')
    except:
        waste_items = []
    
    return render(request, 'core/waste_list.html', {'waste_items': waste_items})

@login_required
def waste_detail(request, pk):
    waste_item = get_object_or_404(WasteItem, pk=pk)
    
    if request.method == 'POST' and request.user.user_type in ['collector', 'recycler']:
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.waste_item = waste_item
            match.collector = request.user
            match.save()
            messages.success(request, 'Match request sent!')
            return redirect('waste_list')
    else:
        form = MatchForm()
    
    return render(request, 'core/waste_detail.html', {
        'waste_item': waste_item,
        'form': form
    })

@login_required
def manage_match(request, pk, action):
    match = get_object_or_404(Match, pk=pk)
    
    if request.user != match.waste_item.poster:
        messages.error(request, 'You cannot manage this match.')
        return redirect('dashboard')
    
    if action == 'accept':
        match.status = 'accepted'
        match.waste_item.status = 'pending'
        match.waste_item.save()
        match.save()
        messages.success(request, 'Match accepted!')
    elif action == 'reject':
        match.status = 'rejected'
        match.save()
        messages.info(request, 'Match rejected.')
    
    return redirect('dashboard')