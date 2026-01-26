import logging
import os
import pandas as pd
import requests
from django.shortcuts import redirect, render
from .forms import XYForm, AssetForm
from pyproj import Proj, transform
from .all_invest import save_to_csv, get_binance_data, plot_total_balance, plot_total_profit, plot_monthly_profit_candles, plot_diversification_asset
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


logger = logging.getLogger(__name__)


proj_2000 = Proj(init='epsg:2178')
proj_wgs84 = Proj(init='epsg:4326')

def convert_view(request):
    result = None
    if request.method == 'POST':
        form = XYForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            lat, lon= transform(proj_2000, proj_wgs84, x, y)
            lon = round(lon, 5)
            lat = round(lat, 5)
            result = f"{lon},{lat}"
    else:
        form = XYForm()

    return render(request, 'djangoapp/main.html', {'form': form, 'result': result})


@login_required
def private_view(request):
    logger.warning("PRIVATE_VIEW CALLED, METHOD=%s", request.method)

    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")

    history = []
    assets_from_csv = {}
    profit = None

    # ✅ ALWAYS define form
    form = AssetForm()

    # ---------------- POST ----------------
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            deposit = form.cleaned_data["deposit"]

            names = request.POST.getlist("asset_name[]")
            values = request.POST.getlist("asset_value[]")

            assets = {
                name.strip(): float(value)
                for name, value in zip(names, values)
                if name.strip() and value
            }

            total_pln = sum(assets.values())
            profit = total_pln - deposit

            save_to_csv(assets, total_pln, deposit)
            return redirect("private")

    # ---------------- READ CSV (GET or after redirect) ----------------
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        history = df.tail(20).to_dict(orient="records")

        if not df.empty:
            last = df.iloc[-1]
            excluded = {"Date", "Total", "Deposit"}

            assets_from_csv = {
                col: float(last[col])
                for col in df.columns
                if col not in excluded
            }

            # prefill deposit
            form = AssetForm(initial={"deposit": last["Deposit"]})

    # ---------------- CHARTS ----------------
    chart_total_balance = plot_total_balance()
    chart_total_profit = plot_total_profit()
    chart_monthly_profit = plot_monthly_profit_candles()
    chart_diversification = plot_diversification_asset()

    return render(request, "djangoapp/private.html", {
        "form": form,
        "history": history,
        "assets": assets_from_csv,
        "profit": profit,
        "chart_total_balance": chart_total_balance,
        "chart_total_profit": chart_total_profit,
        "chart_monthly_profit": chart_monthly_profit,
        "chart_diversification": chart_diversification,
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


def save_assets(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():


            names = request.POST.getlist("asset_name[]")
            values = request.POST.getlist("asset_value[]")

            assets = {
                name: float(value)
                for name, value in zip(names, values)
                if name and value
            }

            # assets = {'bitcoin': 1200, 'gold': 3000, ...}

            print(assets)

