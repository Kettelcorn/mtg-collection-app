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
        fields = ['card_name', 'scryfall_id', 'tcg_id', 'set', 'collector_number', 'finish', 'print_uri', 'collection', 'price', 'quantity']
