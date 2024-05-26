from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'power', 'toughness', 'colors', 'rarity', 'set_name', 'image_url', 'price')
