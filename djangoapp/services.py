from django.db import transaction
from .models import Asset, AssetHolding, AssetTransaction


@transaction.atomic
def apply_transactions(user, assets_dict):
    """
    assets_dict = { "bitcoin": 1200, "silver": 300 }
    """

    for name, value in assets_dict.items():
        asset, _ = Asset.objects.get_or_create(name=name)

        holding, _ = AssetHolding.objects.get_or_create(
            user=user,
            asset=asset,
            defaults={"amount": 0}
        )

        delta = value - holding.amount

        if delta == 0:
            continue

        tx_type = AssetTransaction.ADD if delta > 0 else AssetTransaction.SUB

        AssetTransaction.objects.create(
            user=user,
            asset=asset,
            amount=abs(delta),
            transaction_type=tx_type
        )

        holding.amount = value
        holding.save()

