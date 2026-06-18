import requests

def fetch_usdt_rate():
    try:
        url = "https://api.bitpin.ir/v1/mkt/markets/"
        res = requests.get(url, timeout=10)
        data = res.json()

        for market in data.get("results", []):
            if market.get("code") == "USDT_IRT":  # ✅ کد صحیح در بیت‌پین
                return float(market["price"])
    except Exception as e:
        print("Error fetching Bitpin API:", e)
    return None

print("📡 نرخ تتر:", fetch_usdt_rate())
