from rest_framework import serializers
from .models import User, Collection


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['discord_id', 'discord_username']

    def create(self, validated_data):
        # TODO: Add a check to see if the user already exists
        user = User.objects.create(**validated_data)
        collection = Collection.objects.create(user=user)
        user.collection = collection
        user.save()
        return user


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['card_name', 'scryfall_id', 'tcg_id', 'set', 'collector_number', 'finish', 'print_uri', 'collection', 'price', 'quantity']
