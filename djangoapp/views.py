import logging
import requests
from django.shortcuts import redirect, render
from .forms import DepositForm
from .models import AssetHolding, SnapshotAsset, PortfolioSnapshot
from .services import apply_transactions
from .all_invest import save_to_csv
from django.db.models import Sum
from .all_invest import save_to_csv, plot_total_balance, plot_total_profit, plot_monthly_profit_candles, plot_diversification_asset
from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


# logger = logging.getLogger(__name__)


# @login_required
def private_view(request):

    user, _ = User.objects.get_or_create(username="JacekOsa")


    assets_from_db = AssetHolding.objects.filter(user=user)

    last_snapshot = PortfolioSnapshot.objects.filter(user=user).order_by("-created_at").first()

    deposit = last_snapshot.deposit if last_snapshot else 0

    if request.method == "POST":
        form = DepositForm(request.POST)

        if form.is_valid():
            deposit = int(form.cleaned_data["deposit"])

            names = request.POST.getlist("asset_name[]")
            values = request.POST.getlist("asset_value[]")

            assets = {
                name.strip(): int(float(value))
                for name, value in zip(names, values)
                if name.strip() and value
            }

            apply_transactions(user, assets)

            total = AssetHolding.objects.filter(
                user=user
            ).aggregate(
                total=Sum("amount")
            )["total"] or 0

            snapshot = PortfolioSnapshot.objects.create(
                user=user,   # 🔥 nie request.user
                total=total,
                deposit=deposit
            )

            holdings = AssetHolding.objects.filter(user=user)

            for holding in holdings:
                SnapshotAsset.objects.create(
                    snapshot=snapshot,
                    asset=holding.asset,
                    amount=holding.amount
                )

            return redirect("private")

    else:
        form = DepositForm(initial={"deposit": deposit})

    # 🔥 HISTORIA Z BAZY
    history = PortfolioSnapshot.objects.order_by("-created_at")

    return render(request, "djangoapp/private.html", {
        "form": form,
        "assets": assets_from_db,
        "deposit": deposit,
        "history": history,
        "chart_total_balance": plot_total_balance(),
        "chart_total_profit": plot_total_profit(),
        "chart_monthly_profit": plot_monthly_profit_candles(),
        "chart_diversification": plot_diversification_asset(),
    })






# def login_view(request):
#     error = None
#     if request.method == "POST":
#         username = request.POST["username"]
#         password = request.POST["password"]

#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect("private")
#         else:
#             error = "Wrong login or password"

#     return render(request, "djangoapp/login.html", {"error": error})


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

