import os
import csv
import requests
from datetime import datetime

import matplotlib
matplotlib.use("Agg")   # <<< MUSI BYĆ PRZED pyplot

import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf

from django.conf import settings




def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()
    return float(data["price"]) if "price" in data else None


def plot_total_balance():
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    img_path = os.path.join(settings.BASE_DIR, "kml_converter", "static", "charts", "total_balance.png")

    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    if df.empty:
        return None

    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Total"], label="Total Balance")
    plt.plot(df["Date"], df["Deposit"], label="Deposit")

    plt.xlabel("Date")
    plt.ylabel("PLN")
    plt.title("Total Balance Over Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    plt.savefig(img_path)
    plt.close()

    return "charts/total_balance.png"


def plot_total_profit():
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    img_path = os.path.join(settings.BASE_DIR, "kml_converter",  "static", "charts", "total_profit.png")

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['Date'])

    if df.empty:
        return None

    plt.figure(figsize=(10,5))
    plt.plot(df['Date'], df['Total'] - df['Deposit'], linestyle='-', color='b', label='Profit')
    plt.title('Total Profit Over Time')
    plt.xlabel('Date')
    plt.ylabel('Profit (PLN)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    plt.savefig(img_path)
    plt.close()

    return "charts/total_profit.png"



def plot_monthly_profit_candles():
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    img_path = os.path.join(settings.BASE_DIR, "kml_converter", "static", "charts", "monthly_profit.png")

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Profit'] = df['Total'] - df['Deposit']
    df.set_index('Date', inplace=True)

    monthly_ohlc = df['Profit'].resample('ME').ohlc()
    monthly_ohlc = monthly_ohlc.dropna()

    if monthly_ohlc.empty:
        return None

    mpf.plot(
        monthly_ohlc,
        type='candle',
        style='charles',
        title='Monthly Profit (Candlestick)',
        ylabel='Profit (PLN)',
        figratio=(10,6),
        volume=False,
        savefig=dict(fname=img_path, dpi=100, pad_inches=0.25)
    )

    return "charts/monthly_profit.png"


def plot_diversification_asset():
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    img_path = os.path.join(settings.BASE_DIR, "kml_converter", "static", "charts", "asset_diversification.png")

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()  # usuwa ewentualne spacje

    if df.empty:
        return None

    last = df.iloc[-1]
    bitcoin_pln = last.get('bitcoin', 0)
    altcoins_pln = last.get('altcoin', 0)
    silver = last.get('silver', 0)
    mwig40 = last.get('mwig40', 0)
    tsmc = last.get('tsmc', 0)
    cameco = last.get('cameco', 0)

    labels = ['bitcoin', 'altcoins', 'silver', 'mwig40', 'tsmc', 'cameco']
    sizes = [bitcoin_pln, altcoins_pln, silver, mwig40, tsmc, cameco]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', "#d36f0b",  "#d30bc2"]
    explode = (0.05, 0.05, 0.05, 0.05, 0.05, 0.05)

    plt.figure(figsize=(6,6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    plt.title('Asset Diversification')
    plt.axis('equal')
    plt.tight_layout()

    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    plt.savefig(img_path)
    plt.close()

    return "charts/asset_diversification.png"




def save_to_csv(bitcoin, altcoin, silver, mwig40, tsmc, cameco, total, deposit):
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    file_exists = os.path.exists(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            header = [
                "Date", "bitcoin", "altcoin", "silver",
                "mwig40", "tsmc", "cameco", "Total", "Deposit"
            ]
            writer.writerow(header)

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            bitcoin, altcoin, silver,
            mwig40, tsmc, cameco,
            total, deposit
        ]
        writer.writerow(row)


