from flask import Flask, render_template
import requests
from sector_map import SECTOR_MAP

app = Flask(__name__)

# -------------------------------
# NSE SESSION (GLOBAL)
# -------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# -------------------------------
# ADD SECTOR INFO
# -------------------------------
def add_sector(stocks):
    for s in stocks:
        s["sector"] = SECTOR_MAP.get(s["symbol"], "OTHER")
    return stocks


# -------------------------------
# TOP BANK FUNCTIONS
# -------------------------------
def top_banks_by_volume(stocks, top_n=5):
    banks = [s for s in stocks if s["sector"] == "BANK"]
    return sorted(
        banks,
        key=lambda x: x["totalTradedVolume"],
        reverse=True
    )[:top_n]


def top_banks_by_value(stocks, top_n=5):
    banks = [s for s in stocks if s["sector"] == "BANK"]
    return sorted(
        banks,
        key=lambda x: x["totalTradedVolume"] * x["lastPrice"],
        reverse=True
    )[:top_n]
def top_sector(stocks, sector, top_n=5):
    return sorted(
        [s for s in stocks if s["sector"] == sector],
        key=lambda x: x["totalTradedVolume"],
        reverse=True
    )[:top_n]


# -------------------------------
# FETCH NIFTY DATA
# -------------------------------
def get_nifty_data():
    # Important: warm up cookies
    SESSION.get("https://www.nseindia.com")

    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    response = SESSION.get(url, timeout=10)
    response.raise_for_status()

    stocks = response.json()["data"]
    
    # Add sector dynamically
    stocks = add_sector(stocks)
    
    # Top gainers & losers
    gainers = sorted(stocks, key=lambda x: x["pChange"], reverse=True)[:5]
    losers = sorted(stocks, key=lambda x: x["pChange"])[:5]
    
    # Top banks
    top_bank_volume = top_banks_by_volume(stocks)
    top_bank_value = top_banks_by_value(stocks)
    top_it = top_sector(stocks, "IT")
    top_other = top_sector(stocks, "OTHER")

    return gainers, losers, top_bank_volume, top_bank_value,top_it, top_other


    #return gainers, losers, top_bank_volume, top_bank_value



# -------------------------------
# ROUTE
# -------------------------------
@app.route("/")
def home():
    gainers, losers, top_bank_volume, top_bank_value,top_it, top_other = get_nifty_data()

    return render_template(
        "index.html",
        gainers=gainers,
        losers=losers,
        top_bank_volume=top_bank_volume,
        top_bank_value=top_bank_value,
        top_it=top_it,
        top_other=top_other
    )


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
