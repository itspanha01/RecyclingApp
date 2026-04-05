from django.contrib import admin
from .models import PlasticSubmission, PrizeRedemption

@admin.register(PlasticSubmission)
class PlasticSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plastic_type', 'quantity', 'points_earned', 'submitted_at']
    list_filter = ['plastic_type', 'submitted_at']
    search_fields = ['user__username']

@admin.register(PrizeRedemption)
class PrizeRedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'prize_name', 'points_spent', 'code', 'redeemed_at', 'is_used']
    list_filter = ['prize_id', 'is_used']
    search_fields = ['user__username', 'code']
    readonly_fields = ['code', 'redeemed_at']