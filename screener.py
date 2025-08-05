import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

# === 1. JPXサイトから最新の.xlsファイルをダウンロード ===
JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
xls_path = "data_j.xls"

print("📥 Downloading JPX data...")
res = requests.get(JPX_URL)
with open(xls_path, "wb") as f:
    f.write(res.content)

# === 2. Excelファイル読み込み & プライム銘柄抽出 ===
print("📊 Extracting Prime Market stocks...")
df = pd.read_excel(xls_path, skiprows=1)

# プライム市場のみ
df_prime = df[df["市場・商品区分"] == "プライム市場"].copy()
df_prime["symbol"] = df_prime["コード"].apply(lambda x: f"TSE:{int(x):04d}")

# === 3. スクリーニング条件 ===
ROE_MIN = 10.0
PER_MAX = 20.0
OPM_MIN = 10.0

results = []

print(f"🔍 Screening {len(df_prime)} stocks...")
for _, row in df_prime.iterrows():
    code = row["コード"]
    name = row["銘柄名"]
    symbol = row["symbol"]

    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={API_KEY}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"⚠️ Failed: {symbol}")
            continue
        data = res.json().get("metric", {})
        roe = data.get("roe")
        per = data.get("peBasicExclExtraTTM")
        opm = data.get("operatingMarginTTM")

        if roe is None or per is None or opm is None:
            continue

        if roe >= ROE_MIN and per <= PER_MAX and opm >= OPM_MIN:
            results.append({
                "code": code,
                "name": name,
                "symbol": symbol,
                "ROE": round(roe, 2),
                "PER": round(per, 2),
                "OPM": round(opm, 2)
            })

    except Exception as e:
        print(f"❌ Error with {symbol}: {e}")

    time.sleep(1.1)  # レート制限対策（60 req/min）

# === 4. 結果出力 ===
df_result = pd.DataFrame(results)
if df_result.empty:
    print("😢 No stocks matched the criteria.")
else:
    df_result.to_csv("screened_stocks.csv", index=False, encoding="utf-8-sig")
    print(f"✅ {len(df_result)} stocks matched. Saved to screened_stocks.csv")
