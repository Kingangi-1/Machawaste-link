from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import WasteItem, Match, WasteCategory, User, CreditTransaction
from .forms import UserRegistrationForm, WasteItemForm, MatchForm, Match
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

#from .models import WasteItem, , CreditTransaction



@login_required
def user_credits(request):
    """Display user's credit balance and transaction history"""
    credit_transactions = CreditTransaction.objects.filter(user=request.user)
    context = {
        'credit_balance': request.user.digital_credits,
        'transactions': credit_transactions
    }
    return render(request, 'core/credits.html', context)


def test_award_credits(request, waste_id):
    """Test function to manually award credits for a waste item"""
    if not request.user.is_superuser:
        return HttpResponse("Admin only")
    
    waste_item = get_object_or_404(WasteItem, id=waste_id)
    credits_awarded = waste_item.award_credits()
    
    return HttpResponse(f"Credits awarded: {credits_awarded}. User now has: {waste_item.poster.digital_credits} credits")


def complete_waste_transaction(waste_item_id, collector_id):
    """Handle completion of waste transaction and credit transfer"""
    try:
        with transaction.atomic():
            waste_item = get_object_or_404(WasteItem, id=waste_item_id)
            collector = get_object_or_404(User, id=collector_id)
            
            if waste_item.status != 'matched':
                return False, "Waste item is not in matched status"
            
            # Calculate final credit value
            credit_amount = waste_item.calculate_credit_value()
            
            # Add credits to waste generator
            waste_item.posted_by.add_credits(
                credit_amount,
                reason=f"Credit for waste: {waste_item.title}"
            )
            
            # Update waste item status
            waste_item.status = 'completed'
            waste_item.save()
            
            return True, f"Transaction completed! {credit_amount} credits added to your account."
            
    except Exception as e:
        return False, f"Error completing transaction: {str(e)}"

#start manage match function

def manage_match(request, pk, action):
    match = get_object_or_404(Match, pk=pk)
    
    print(f"DEBUG: User: {request.user.username} (ID: {request.user.id})")
    print(f"DEBUG: Match Collector: {match.collector.username} (ID: {match.collector.id})")
    print(f"DEBUG: Action: {action}")
    print(f"DEBUG: User == Collector: {request.user == match.collector}")
    print(f"DEBUG: User ID == Collector ID: {request.user.id == match.collector.id}")
    
    # Check permissions for complete action
    if action == 'complete':
        # Only the collector who made the request can complete it
        if request.user != match.collector:  # Changed from ID comparison to object comparison
            messages.error(request, f'You cannot complete this collection. You are {request.user.username} but this collection was requested by {match.collector.username}.')
            return redirect('dashboard')
        
        # Check if match is in the right status
        if match.status != 'accepted':
            messages.error(request, f'Cannot complete collection. Current status is "{match.status}", but should be "accepted".')
            return redirect('dashboard')
        
        # Now complete the match
        success, credits_awarded = match.complete_match()
        if success:
            messages.success(request, f'✅ Collection completed! {credits_awarded} credits awarded to {match.waste_item.poster.username}.')
        else:
            messages.error(request, 'Could not complete collection. Please try again.')
        return redirect('dashboard')
    
    # Handle other actions (accept/reject)
    elif action in ['accept', 'reject']:
        # Only waste poster can accept/reject
        if request.user != match.waste_item.poster:
            messages.error(request, 'You can only manage requests for your own waste items.')
            return redirect('dashboard')
        
        if action == 'accept':
            if match.accept_match():
                messages.success(request, 'Request accepted! The collector can now complete the collection.')
            else:
                messages.error(request, 'Could not accept request.')
        else:  # reject
            match.status = 'rejected'
            match.save()
            messages.success(request, 'Request rejected.')
        
        return redirect('dashboard')
    
    messages.error(request, 'Invalid action.')
    return redirect('dashboard')

# end of manage match ends here


@login_required
def request_match(request, waste_item_id):
    waste_item = get_object_or_404(WasteItem, id=waste_item_id)
    
    # Check if waste item is available
    if waste_item.status != 'available':
        messages.error(request, "This waste item is no longer available for matching.")
        return redirect('waste_list')
    
    # Check if user is a collector (not a poster)
    if request.user.user_type != 'collector':
        messages.error(request, "Only collectors can request waste items.")
        return redirect('waste_list')
    
    # Check if user is trying to collect their own waste
    if waste_item.poster == request.user:
        messages.error(request, "You cannot request your own waste item.")
        return redirect('waste_list')
    
    # Check if match already exists
    existing_match = Match.objects.filter(
        waste_item=waste_item,
        collector=request.user
    ).first()
    
    if existing_match:
        messages.warning(request, f"You already have a {existing_match.status} request for this item.")
        return redirect('waste_list')
    
    # Create the match
    try:
        Match.objects.create(
            waste_item=waste_item,
            collector=request.user,
            status='pending',
            message=f"Interested in collecting your {waste_item.get_waste_type_display()} waste"
        )
        messages.success(request, "Match request sent successfully! The poster will review your request.")
    except Exception as e:
        messages.error(request, f"Error creating match: {str(e)}")
    
    return redirect('waste_list')

# it reaches here

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

# start of dashboard view
@login_required
def dashboard(request):
    user_waste = WasteItem.objects.filter(poster=request.user)
    matches_received = Match.objects.filter(waste_item__poster=request.user)
    
    # Different views based on user type
    if request.user.user_type in ['collector', 'recycler']:
        available_waste = WasteItem.objects.filter(status='available').exclude(poster=request.user)
        matches_made = Match.objects.filter(collector=request.user)
        
        # NEW: Show accepted matches that need completion
        accepted_matches = Match.objects.filter(
            collector=request.user, 
            status='accepted'
        )
        
        # For collectors: show nearby waste
        if request.user.location:
            available_waste = available_waste.filter(location__icontains=request.user.location)
    else:
        available_waste = None
        matches_made = None
        accepted_matches = None
    
    # Statistics for dashboard
    total_waste_posted = user_waste.count()
    total_credits_earned = sum([waste.credits_earned for waste in user_waste])
    pending_matches = matches_received.filter(status='pending').count()
    
    # Credit transaction data
    recent_transactions = CreditTransaction.objects.filter(user=request.user).order_by('-created_at')[:5]
    transaction_count = CreditTransaction.objects.filter(user=request.user).count()
    
    # Calculate credits earned this month
    current_month = timezone.now().month
    current_year = timezone.now().year
    credits_this_month = CreditTransaction.objects.filter(
        user=request.user,
        transaction_type='credit',
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Alternative calculation for total credits earned from all credit transactions
    total_credits_from_transactions = CreditTransaction.objects.filter(
        user=request.user,
        transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'user_waste': user_waste,
        'matches_received': matches_received,
        'available_waste': available_waste,
        'matches_made': matches_made,
        'accepted_matches': accepted_matches,  # NEW
        'total_waste_posted': total_waste_posted,
        'total_credits_earned': total_credits_earned,
        'pending_matches': pending_matches,
        'recent_transactions': recent_transactions,
        'transaction_count': transaction_count,
        'credits_this_month': credits_this_month,
        'total_credits_from_transactions': total_credits_from_transactions,
    }
    return render(request, 'core/dashboard.html', context)
#End of dashboard view

@login_required
def post_waste(request):
    if request.method == 'POST':
        form = WasteItemForm(request.POST, request.FILES)
        if form.is_valid():
            waste_item = form.save(commit=False)
            waste_item.poster = request.user
            
            try:
                # Calculate estimated credits before saving
                estimated_credits = waste_item.calculate_estimated_credits()
                waste_type = waste_item.get_waste_type_display()
                quantity = waste_item.quantity
                unit = waste_item.unit
                
                waste_item.save()
                
                messages.success(
                    request, 
                    f'✅ Waste item "{waste_item.title}" posted successfully! '
                    f'📊 Estimated credit value: {estimated_credits} points '
                    f'({quantity} {unit} of {waste_type})'
                )
                return redirect('dashboard')
                
            except TypeError as e:
                # Handle the Decimal/float multiplication error
                waste_item.save()  # Save without calculated credits for now
                messages.warning(
                    request,
                    f'✅ Waste item "{waste_item.title}" posted successfully! '
                    '⚠️ Credit calculation will be updated soon.'
                )
                return redirect('dashboard')
                
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = WasteItemForm()
    
    # Add credit rates to context for display in template
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
    
    context = {
        'form': form,
        'credit_rates': credit_rates
    }
    
    return render(request, 'core/post_waste.html', context) 


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

""""
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

"""