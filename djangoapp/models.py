from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AssetHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "asset")

    def __str__(self):
        return f"{self.user.username} - {self.asset.name}: {self.amount}"


class AssetTransaction(models.Model):
    ADD = "ADD"
    SUB = "SUB"

    TRANSACTION_TYPES = [
        (ADD, "Add"),
        (SUB, "Subtract"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.transaction_type} {self.amount} {self.asset}"


class PortfolioSnapshot(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()
    deposit = models.IntegerField()
