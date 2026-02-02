import logging
import requests
from django.shortcuts import redirect, render
from .forms import DepositForm
from .models import AssetHolding, Asset, PortfolioSnapshot
from .services import apply_transactions
from .all_invest import save_to_csv
from django.db.models import Sum
from .all_invest import save_to_csv, plot_total_balance, plot_total_profit, plot_monthly_profit_candles, plot_diversification_asset
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


logger = logging.getLogger(__name__)


@login_required
def private_view(request):
    logger.warning("PRIVATE_VIEW CALLED, METHOD=%s", request.method)

    assets_from_db = AssetHolding.objects.filter(user=request.user)
    profit = None

    if request.method == "POST":
        form = DepositForm(request.POST)

        if form.is_valid():
            deposit = form.cleaned_data["deposit"]

            names = request.POST.getlist("asset_name[]")
            values = request.POST.getlist("asset_value[]")

            assets = {
                name.strip(): float(value)
                for name, value in zip(names, values)
                if name.strip() and value
            }

            apply_transactions(request.user, assets)

            total = int(AssetHolding.objects.filter(
                user=request.user
            ).aggregate(
                total=Sum("amount")
            )["total"] or 0)
            PortfolioSnapshot.objects.create(
                total=total,
                deposit=deposit
            )

            save_to_csv(assets, total, deposit)

            return redirect("private")

    else:
        form = DepositForm()

    return render(request, "djangoapp/private.html", {
        "form": form,
        "assets": assets_from_db,
        "profit": profit,
        "chart_total_balance": plot_total_balance(),
        "chart_total_profit": plot_total_profit(),
        "chart_monthly_profit": plot_monthly_profit_candles(),
        "chart_diversification": plot_diversification_asset(),
    })





def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("private")
        else:
            error = "Wrong login or password"

    return render(request, "djangoapp/login.html", {"error": error})


def get_usd_pln():
    url = "https://api.nbp.pl/api/exchangerates/rates/A/USD/?format=json"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    return data["rates"][0]["mid"]


# def save_assets(request):
#     if request.method == "POST":
#         form = AssetForm(request.POST)
#         if form.is_valid():


#             names = request.POST.getlist("asset_name[]")
#             values = request.POST.getlist("asset_value[]")

#             assets = {
#                 name: float(value)
#                 for name, value in zip(names, values)
#                 if name and value
#             }

#             # assets = {'bitcoin': 1200, 'gold': 3000, ...}

#             print(assets)

