import pandas as pd
import requests
import time
import os
import yfinance as yf
import sqlite3

# 作業ディレクトリのパスを固定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === 1. JPXサイトから最新の.xlsファイルをダウンロード ===
JPX_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
xls_path = os.path.join(BASE_DIR, "data_j.xls")

print("📥 Downloading JPX data...")
res = requests.get(JPX_URL)
with open(xls_path, "wb") as f:
    f.write(res.content)

# === 2. Excelファイル読み込み & プライム銘柄抽出 ===
print("📊 Extracting Prime Market stocks...")
df = pd.read_excel(xls_path, header=0)

# プライム市場のみ抽出
df_prime = df[df["市場・商品区分"] == "プライム（内国株式）"].copy()

def to_yfinance_symbol(code):
    try:
        return f"{int(code):04d}.T"
    except ValueError:
        return None

df_prime["symbol"] = df_prime["コード"].apply(to_yfinance_symbol)
df_prime = df_prime[df_prime["symbol"].notnull()]

# === 3. スクリーニング条件 ===
ROE_MIN = 0.10  # yfinanceは比率で返す（例：0.12 = 12%）
PER_MAX = 20.0
OPM_MIN = 0.10

results = []

print(f"🔍 Screening {len(df_prime)} stocks...")
for _, row in df_prime.iterrows():
    code = row["コード"]
    name = row["銘柄名"]
    symbol = row["symbol"]

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        roe = info.get("returnOnEquity")
        per = info.get("trailingPE")
        opm = info.get("operatingMargins")

        if roe is None or per is None or opm is None:
            continue

        if roe >= ROE_MIN and per <= PER_MAX and opm >= OPM_MIN:
            results.append({
                "code": code,
                "name": name,
                "symbol": symbol,
                "ROE": round(roe * 100, 2),
                "PER": round(per, 2),
                "OPM": round(opm * 100, 2)
            })

    except Exception as e:
        print(f"❌ Error with {symbol}: {e}")

    time.sleep(1.0)  # Yahoo APIも連続アクセスに注意

# === 4. 結果出力 ===
db_path = os.path.join(BASE_DIR, "screened_stocks.db")
df_result = pd.DataFrame(results)
if df_result.empty:
    print("😢 No stocks matched the criteria.")
else:
    # SQLiteに保存
    conn = sqlite3.connect(db_path)
    df_result.to_sql("stocks", conn, if_exists="replace", index=False)
    conn.close()
    print(f"✅ {len(df_result)} stocks matched. Saved to {db_path}")