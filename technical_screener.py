import os
import pandas as pd
import yfinance as yf
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")

# 作業ディレクトリを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLiteファイルのパス
db_path = os.path.join(BASE_DIR, "screened_stocks.db")

# SQLiteからファンダメンタルスクリーニング済銘柄を読み込み
conn = sqlite3.connect(db_path)
df_funda = pd.read_sql("SELECT * FROM stocks", conn)
conn.close()

CHANNEL_ACCESS_TOKEN = "あなたのチャネルアクセストークン"

def send_line_notify(message):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"通知送信失敗: {response.status_code} {response.text}")
        
def technical_screening(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="60d")  # 過去60日分データ取得
        if hist.empty:
            return False
        
        # 移動平均線計算
        hist['MA5'] = hist['Close'].rolling(window=5).mean()
        hist['MA25'] = hist['Close'].rolling(window=25).mean()
        hist['Volume_MA5'] = hist['Volume'].rolling(window=5).mean()

        latest = hist.iloc[-1]
        prev = hist.iloc[-2]

        # 条件例: 現在の終値がMA25を上回っている
        cond1 = latest['Close'] > latest['MA25']

        # 条件例: 5日MAが25日MAを上抜け（ゴールデンクロス）
        cond2 = (prev['MA5'] < prev['MA25']) and (latest['MA5'] > latest['MA25'])

        # 条件例: 出来高が直近5日の平均を上回る
        cond3 = latest['Volume'] > latest['Volume_MA5']

        # ゴールデンクロスの場合は通知
        if cond2:
            send_line_notify(f"📈 ゴールデンクロス検出: {symbol}")

        return cond1 and cond3

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return False

# スクリーニング実行
filtered = []
for _, row in df_funda.iterrows():
    symbol = row['symbol']
    if technical_screening(symbol):
        filtered.append(row)

df_filtered = pd.DataFrame(filtered)

if df_filtered.empty:
    print("No stocks passed technical screening.")
else:
    print(f"{len(df_filtered)} stocks passed technical screening.")
    print(df_filtered[['code', 'name', 'symbol', 'ROE', 'PER', 'OPM']])

    # 別のDBファイルのパス
    db_path = os.path.join(BASE_DIR, "technical_screened.db")
    
    # 別のDBファイルに保存
    conn = sqlite3.connect(db_path)
    df_filtered.to_sql("stocks", conn, if_exists="replace", index=False)
    conn.close()

    print("Technical screening results saved to technical_screened.db")
 # df_filtered.to_csv('technical_screened.csv', index=False)
