from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Card
from .serializers import CardSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        name = request.query_params.get('name', None)

        if name is not None:
            cards = Card.objects.filter(name__icontains=name)
            serializer = self.get_serializer(cards, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Name query parameter is required."}, status=400)

    def list(self, request, *args, **kwargs):
        print("Request Headers:", request.headers)
        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)
        return super().list(request, *args, **kwargs)
