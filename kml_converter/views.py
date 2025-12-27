import os
import pandas as pd
from django.shortcuts import redirect, render
from .forms import XYForm, AssetForm
from pyproj import Proj, transform
from .all_invest import save_to_csv, get_binance_data, plot_total_balance, plot_total_profit, plot_monthly_profit_candles, plot_diversification_asset
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login



@login_required
def private_view(request):
    ...



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

    return render(request, 'main.html', {'form': form, 'result': result})

@login_required
def private_view(request):
    result = None
    profit = None

    DEPO_XTB = 12000
    DEPO_BINANCE = 8000
    deposit = DEPO_XTB + DEPO_BINANCE

    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    history = []

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        history = df.tail(20).to_dict(orient="records")

    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            bitcoin = form.cleaned_data["bitcoin"]
            altcoin = form.cleaned_data["altcoin"]
            silver = form.cleaned_data["silver"]
            mwig40 = form.cleaned_data["mwig40"]
            tsmc = form.cleaned_data["tsmc"]
            cameco = form.cleaned_data["cameco"]
            usd = get_binance_data(symbol="BUSDPLN")
            bitcoin_pln = bitcoin * usd
            print("bitcoin_pln:", bitcoin_pln)
            altcoins_pln = (altcoin * usd) - bitcoin_pln
            saldo_binance = bitcoin_pln + altcoins_pln
            xtb = silver + mwig40 + tsmc + cameco
            total_pln = saldo_binance  + xtb

            profit = total_pln - deposit

            save_to_csv(
                round(bitcoin_pln), round(altcoins_pln), round(silver),
                round(mwig40), round(tsmc), round(cameco),
                round(total_pln), round(deposit)
            )

    else:
        form = AssetForm()

    chart_total_balance = plot_total_balance()
    chart_total_profit = plot_total_profit()
    chart_monthly_profit = plot_monthly_profit_candles()
    chart_diversification = plot_diversification_asset()


    return render(request, "private.html", {
        "form": form,
        "result": result,
        "profit": profit,
        "history": history,
        "chart_total_balance": chart_total_balance,
        "chart_total_profit": chart_total_profit,
        "chart_monthly_profit": chart_monthly_profit,
        "chart_diversification": chart_diversification
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

    return render(request, "login.html", {"error": error})
