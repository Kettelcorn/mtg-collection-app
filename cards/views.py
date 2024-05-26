from django.http import JsonResponse
from django.views import View
from .models import Card


class CardNameView(View):
    def get(self, request, *args, **kwargs):
        card_name = request.GET.get('name')
        if card_name:
            try:
                card = Card.objects.get(name=card_name)
                data = {
                    'name': card.name,
                    'stats': card.stats,
                    'description': card.description,
                    'price': card.price,
                }
                return JsonResponse(data)
            except Card.DoesNotExist:
                return JsonResponse({'error': 'Card not found'}, status=404)
        else:
            return JsonResponse({'error': 'No card name provided'}, status=400)
