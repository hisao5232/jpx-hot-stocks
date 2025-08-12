import sqlite3
import pandas as pd
import yfinance as yf
import requests
import os
from dotenv import load_dotenv

# .envからLINEのアクセストークン読み込み
load_dotenv()
LINE_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

# 作業ディレクトリを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 入力DB（二次スクリーニング結果）
INPUT_DB = os.path.join(BASE_DIR, "technical_screened.db")
# 出力DB（三次スクリーニング結果）
OUTPUT_DB = os.path.join(BASE_DIR, "final_screened.db")

def load_technical_results():
    conn = sqlite3.connect(INPUT_DB)
    df = pd.read_sql_query("SELECT * FROM stocks", conn)
    conn.close()
    return df

def final_screening(symbol, roe):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="90d")
        if hist.empty:
            return False

        hist["Volume_MA20"] = hist["Volume"].rolling(window=20).mean()
        latest = hist.iloc[-1]

        cond1 = latest["Volume"] > 1.5 * latest["Volume_MA20"]  # 出来高条件
        cond2 = latest["Close"] >= hist["Close"].max() * 0.99   # 高値更新（1%以内）

        return cond1 and cond2
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return False

def broadcast_line_message(message):
    """LINEブロードキャスト送信"""
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"[LINE送信エラー] {r.status_code}: {r.text}")
        else:
            print("[LINE送信成功] ブロードキャスト完了")
    except Exception as e:
        print(f"[LINE送信例外] {e}")

def main():
    df = load_technical_results()
    if df.empty:
        print("二次スクリーニング結果がありません。")
        return

    # ROE順位を計算
    df["ROE_rank"] = df["ROE"].rank(ascending=False)
    top_roe_threshold = df["ROE_rank"].quantile(0.3)  # 上位30%

    final_results = []
    for _, row in df.iterrows():
        if row["ROE_rank"] <= top_roe_threshold:
            if final_screening(row["symbol"], row["ROE"]):
                final_results.append(row)

    if final_results:
        final_df = pd.DataFrame(final_results)
        conn = sqlite3.connect(OUTPUT_DB)
        final_df.to_sql("stocks", conn, if_exists="replace", index=False)
        conn.close()
        print(f"{len(final_df)}件を三次スクリーニング結果として保存しました。")

        # LINE送信用のメッセージを作成
        message_lines = ["【三次スクリーニング結果】"]
        for stock in final_results:
            message_lines.append(f"{stock['code']} {stock['name']} (ROE: {stock['ROE']}%)")
        broadcast_line_message("\n".join(message_lines))

    else:
        print("三次スクリーニング条件に合致する銘柄はありませんでした。")
        broadcast_line_message("三次スクリーニング条件に合致する銘柄はありませんでした。")

if __name__ == "__main__":
    main()
