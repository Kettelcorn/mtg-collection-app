from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Card
from .serializers import CardSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        print("Request Headers:", request.headers)
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)
        return super().list(request, *args, **kwargs)
