from django.contrib import admin
from .models import User, Collection, Card


class CardAdmin(admin.ModelAdmin):
    list_display = ('card_name', 'print_uri', 'quantity')


admin.site.register(User)
admin.site.register(Collection)
admin.site.register(Card, CardAdmin)
