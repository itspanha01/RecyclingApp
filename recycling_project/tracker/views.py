from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count
from .models import RecyclingEntry
from .forms import RegisterForm, RecyclingEntryForm

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to EcoTrack! 🌿')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    entries = RecyclingEntry.objects.filter(user=request.user)
    total_points = entries.aggregate(Sum('points'))['points__sum'] or 0
    total_weight = entries.aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    total_entries = entries.count()

    # Material breakdown
    breakdown = entries.values('material').annotate(
        count=Count('id'),
        total_weight=Sum('weight_kg'),
        total_points=Sum('points')
    ).order_by('-total_points')

    # Badge logic
    badge = None
    if total_points >= 500:
        badge = ('🌳', 'Forest Guardian', 'earth-badge')
    elif total_points >= 200:
        badge = ('🌱', 'Green Sprout', 'sprout-badge')
    elif total_points >= 50:
        badge = ('♻️', 'Eco Starter', 'starter-badge')

    if request.method == 'POST':
        form = RecyclingEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, f'+{entry.points} points earned!')
            return redirect('dashboard')
    else:
        form = RecyclingEntryForm()

    context = {
        'entries': entries[:10],
        'total_points': total_points,
        'total_weight': total_weight,
        'total_entries': total_entries,
        'breakdown': breakdown,
        'badge': badge,
        'form': form,
    }
    return render(request, 'tracker/dashboard.html', context)