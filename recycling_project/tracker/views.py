from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import PlasticSubmission, PrizeRedemption, PRIZES, MONTHLY_ITEM_CAP, POINTS_PER_TYPE
from .forms import RegisterForm, SubmissionForm


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
            messages.success(request, '🌿 Welcome to EcoTrack! Start collecting.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    user = request.user
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # All submissions
    all_submissions = PlasticSubmission.objects.filter(user=user)
    month_submissions = all_submissions.filter(submitted_at__gte=month_start)

    # Totals
    total_points = all_submissions.aggregate(s=Sum('points_earned'))['s'] or 0
    total_items = all_submissions.aggregate(s=Sum('quantity'))['s'] or 0
    month_items = month_submissions.aggregate(s=Sum('quantity'))['s'] or 0
    month_remaining = max(0, MONTHLY_ITEM_CAP - month_items)

    # Already redeemed prize IDs
    redeemed_ids = list(PrizeRedemption.objects.filter(user=user).values_list('prize_id', flat=True))

    # Prize progress
    prizes_data = []
    for prize in PRIZES:
        pct = min(100, int((total_points / prize['points_required']) * 100))
        already = prize['id'] in redeemed_ids
        pts_needed = max(0, prize['points_required'] - total_points)
        prizes_data.append({**prize, 'pct': pct, 'already_redeemed': already, 'pts_needed': pts_needed})
    
    # Weekly chart data (last 7 days)
    week_labels = []
    week_counts = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = all_submissions.filter(submitted_at__date=day).aggregate(s=Sum('quantity'))['s'] or 0
        week_labels.append(day.strftime('%a'))
        week_counts.append(count)

    # Material breakdown
    breakdown = all_submissions.values('plastic_type').annotate(
        total_qty=Sum('quantity'),
        total_pts=Sum('points_earned')
    ).order_by('-total_qty')

    # Recent submissions
    recent = all_submissions[:8]

    # My redemptions
    my_redemptions = PrizeRedemption.objects.filter(user=user)

    # Handle form submission
    form = SubmissionForm()
    if request.method == 'POST' and 'submit_plastic' in request.POST:
        form = SubmissionForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            if month_items + qty > MONTHLY_ITEM_CAP:
                allowed = MONTHLY_ITEM_CAP - month_items
                messages.error(request, f'⚠️ Monthly cap reached! You can only submit {allowed} more items this month.')
            else:
                entry = form.save(commit=False)
                entry.user = user
                entry.save()
                messages.success(request, f'✅ Logged {qty} item(s) — +{entry.points_earned} points!')
                return redirect('dashboard')

    context = {
        'total_points': total_points,
        'total_items': total_items,
        'month_items': month_items,
        'month_remaining': month_remaining,
        'monthly_cap': MONTHLY_ITEM_CAP,
        'month_pct': min(100, int((month_items / MONTHLY_ITEM_CAP) * 100)),
        'prizes_data': prizes_data,
        'week_labels': json.dumps(week_labels),
        'week_counts': json.dumps(week_counts),
        'breakdown': breakdown,
        'recent': recent,
        'my_redemptions': my_redemptions,
        'form': form,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def redeem_prize(request, prize_id):
    prize = next((p for p in PRIZES if p['id'] == prize_id), None)
    if not prize:
        messages.error(request, 'Invalid prize.')
        return redirect('dashboard')

    user = request.user
    total_points = PlasticSubmission.objects.filter(user=user).aggregate(s=Sum('points_earned'))['s'] or 0
    already = PrizeRedemption.objects.filter(user=user, prize_id=prize_id).exists()

    if already:
        messages.error(request, f'You have already redeemed the {prize["name"]}.')
    elif total_points < prize['points_required']:
        messages.error(request, f'Not enough points. You need {prize["points_required"]} pts.')
    else:
        PrizeRedemption.objects.create(
            user=user,
            prize_id=prize_id,
            prize_name=prize['name'],
            points_spent=prize['points_required'],
        )
        messages.success(request, f'🎉 Redeemed: {prize["name"]}! Check your prize codes below.')

    return redirect('dashboard')

@login_required
def leaderboard(request):
    from django.contrib.auth.models import User
    from django.db.models import Sum, Count

    # Rank all users by total points
    users_ranked = User.objects.annotate(
        total_points=Sum('submissions__points_earned'),
        total_items=Sum('submissions__quantity'),
        total_entries=Count('submissions'),
    ).filter(total_points__isnull=False).order_by('-total_points')

    # Find current user's rank
    user_rank = None
    user_stats = None
    for i, u in enumerate(users_ranked, start=1):
        if u == request.user:
            user_rank = i
            user_stats = u
            break

    # If user has no submissions yet
    if user_stats is None:
        user_stats = request.user
        user_stats.total_points = 0
        user_stats.total_items = 0
        user_rank = users_ranked.count() + 1

    # Assign badges
    def get_badge(pts):
        if pts >= 300: return ('🌳', 'Forest Guardian', 'badge-gold')
        if pts >= 150: return ('💧', 'Water Saver', 'badge-silver')
        if pts >= 50:  return ('👜', 'Eco Starter', 'badge-bronze')
        return ('🌱', 'Seedling', 'badge-seed')

    ranked_list = []
    for i, u in enumerate(users_ranked, start=1):
        badge = get_badge(u.total_points or 0)
        ranked_list.append({
            'rank': i,
            'user': u,
            'total_points': u.total_points or 0,
            'total_items': u.total_items or 0,
            'badge': badge,
            'is_me': u == request.user,
        })

    context = {
        'ranked_list': ranked_list,
        'user_rank': user_rank,
        'user_stats': user_stats,
        'user_badge': get_badge(user_stats.total_points or 0),
    }
    return render(request, 'tracker/leaderboard.html', context)