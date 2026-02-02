from django.contrib import admin
from .models import Asset, AssetHolding, AssetTransaction, PortfolioSnapshot

admin.site.register(Asset)
admin.site.register(AssetHolding)
admin.site.register(AssetTransaction)
admin.site.register(PortfolioSnapshot)
