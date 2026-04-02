from django.db import models
from django.contrib.auth.models import User

MATERIAL_CHOICES = [
    ('plastic', 'Plastic'),
    ('glass', 'Glass'),
    ('paper', 'Paper'),
    ('metal', 'Metal'),
    ('electronics', 'Electronics'),
    ('organic', 'Organic'),
    ('other', 'Other'),
]

POINTS_MAP = {
    'plastic': 10,
    'glass': 15,
    'paper': 8,
    'metal': 20,
    'electronics': 50,
    'organic': 5,
    'other': 5,
}

class RecyclingEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    points = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.points = POINTS_MAP.get(self.material, 5) * int(self.weight_kg)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.material} ({self.weight_kg}kg)"

    class Meta:
        ordering = ['-created_at']