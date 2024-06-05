from rest_framework import serializers
from .models import User, Collection


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['discord_id', 'discord_username']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        Collection.objects.create(user=user)
        return user


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['card_name', 'print_uri', 'quantity', 'collection']
