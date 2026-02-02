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
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M', errors='coerce')
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
    img_path = os.path.join(
        settings.BASE_DIR,
        "kml_converter",
        "static",
        "charts",
        "monthly_profit.png"
    )

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    if len(df) < 2:
        return None

    df['Profit'] = df['Total'] - df['Deposit']
    df.set_index('Date', inplace=True)

    monthly_ohlc = df['Profit'].resample('ME').ohlc()
    monthly_ohlc = monthly_ohlc.dropna()

    if len(monthly_ohlc) < 1:
        return None

    mpf.plot(
        monthly_ohlc,
        type='candle',
        style='charles',
        title='Monthly Profit (Candlestick)',
        ylabel='Profit (PLN)',
        volume=False,
        savefig=dict(fname=img_path, dpi=100)
    )

    return "charts/monthly_profit.png"


def plot_diversification_asset():
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    img_path = os.path.join(
        settings.BASE_DIR,
        "kml_converter",
        "static",
        "charts",
        "asset_diversification.png"
    )

    if not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    if df.empty:
        return None

    last = df.iloc[-1]

    # columns that are NOT assets
    excluded_columns = {"Date", "Total", "Deposit"}

    asset_columns = [col for col in df.columns if col not in excluded_columns]

    sizes = [last[col] for col in asset_columns]

    # optional: remove zero-value assets
    asset_columns, sizes = zip(
        *[(c, v) for c, v in zip(asset_columns, sizes) if v > 0]
    ) if any(sizes) else ([], [])

    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=asset_columns,
        autopct='%1.1f%%',
        startangle=140
    )
    plt.title('Asset Diversification')
    plt.axis('equal')
    plt.tight_layout()

    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    plt.savefig(img_path)
    plt.close()

    return "charts/asset_diversification.png"


FIELDS_ORDER = [
    "bitcoin",
    "altcoin",
    "silver",
    "mwig40",
    "tsmc",
    "cameco",
    "samsung",
    "free_money",
]


def save_to_csv(assets, total, deposit):
    csv_path = os.path.join(settings.BASE_DIR, "balance_data.csv")
    file_exists = os.path.exists(csv_path)

    with open(csv_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # ---- HEADER ----
        if not file_exists:
            header = ["Date"] + FIELDS_ORDER + ["Total", "Deposit"]
            writer.writerow(header)

        # ---- ROW ----
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            *[int(round(assets.get(field, 0))) for field in FIELDS_ORDER],
            total,
            deposit,
        ]

        writer.writerow(row)