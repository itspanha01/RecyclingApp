from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random, string

PLASTIC_TYPES = [
    ('bottle', 'Plastic Bottle'),
    ('bag', 'Plastic Bag'),
    ('container', 'Plastic Container'),
    ('packaging', 'Plastic Packaging'),
    ('other', 'Other Plastic'),
]

POINTS_PER_TYPE = {
    'bottle': 10,
    'bag': 5,
    'container': 8,
    'packaging': 6,
    'other': 4,
}

MONTHLY_ITEM_CAP = 50  # Max items per user per month

PRIZES = [
    {
        'id': 'tote',
        'name': 'Eco Tote Bag',
        'icon': '👜',
        'points_required': 50,
        'description': 'A reusable, sturdy tote bag made from recycled materials.',
        'color': 'prize-bronze',
    },
    {
        'id': 'bottle',
        'name': 'Metal Water Bottle',
        'icon': '💧',
        'points_required': 150,
        'description': 'Stainless steel insulated bottle — ditch plastic for good.',
        'color': 'prize-silver',
    },
    {
        'id': 'tree',
        'name': 'Plant a Tree',
        'icon': '🌳',
        'points_required': 300,
        'description': "We'll plant a tree in your name in a reforestation project.",
        'color': 'prize-gold',
    },
]


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class PlasticSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    plastic_type = models.CharField(max_length=20, choices=PLASTIC_TYPES)
    quantity = models.PositiveIntegerField(default=1)
    points_earned = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.points_earned = POINTS_PER_TYPE.get(self.plastic_type, 4) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.plastic_type} x{self.quantity}"

    class Meta:
        ordering = ['-submitted_at']


class PrizeRedemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redemptions')
    prize_id = models.CharField(max_length=20)
    prize_name = models.CharField(max_length=100)
    points_spent = models.IntegerField()
    code = models.CharField(max_length=20, default=generate_code, unique=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} — {self.prize_name} [{self.code}]"

    class Meta:
        ordering = ['-redeemed_at']