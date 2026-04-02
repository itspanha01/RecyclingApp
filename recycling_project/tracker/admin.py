from django.contrib import admin
from .models import RecyclingEntry

@admin.register(RecyclingEntry)
class RecyclingEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'material', 'weight_kg', 'points', 'date']
    list_filter = ['material', 'date']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['points', 'created_at']
    ordering = ['-created_at']