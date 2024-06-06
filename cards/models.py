from django.db import models


class User(models.Model):
    discord_id = models.CharField(max_length=255, unique=True)
    discord_username = models.CharField(max_length=255)
    collection = models.OneToOneField('Collection', on_delete=models.CASCADE,
                                      null=True, blank=True, related_name='user_collection')

    def __str__(self):
        return self.discord_username


class Collection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_collection')

    def __str__(self):
        return f"Collection of {self.user.discord_username}"


class Card(models.Model):
    card_name = models.CharField(max_length=255, default='Card Name')
    scryfall_id = models.CharField(max_length=255, unique=False, default='0')
    tcg_id = models.IntegerField(unique=False, default=0)
    set = models.CharField(max_length=255, default='Set Name')
    collector_number = models.CharField(max_length=10, default='0')
    finish = models.CharField(max_length=10, choices=[('foil', 'Foil'), ('nonfoil', 'Nonfoil')], default='nonfoil')
    print_uri = models.URLField(max_length=500)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='cards')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.card_name} in {self.collection.user.discord_username}'s collection"
