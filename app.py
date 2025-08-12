from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

app = Flask(__name__)

@app.route('/')
def index():
    """一次スクリーニング（ファンダメンタル）"""
    try:
        response = requests.get(f"{API_URL}?type=fundamental")
        response.raise_for_status()
        stocks = response.json()
    except Exception as e:
        stocks = []
        print(f"一次スクリーニングAPI取得エラー: {e}")

    return render_template('index.html', stocks=stocks)

@app.route('/technical')
def technical():
    """二次スクリーニング（テクニカル）"""
    try:
        response = requests.get(f"{API_URL}?type=technical")
        response.raise_for_status()
        stocks = response.json()
    except Exception as e:
        stocks = []
        print(f"二次スクリーニングAPI取得エラー: {e}")

    return render_template('technical.html', stocks=stocks)

@app.route('/final')
def final():
    """三次スクリーニング（テクニカル + 出来高・価格条件など）"""
    try:
        response = requests.get(f"{API_URL}?type=technical")
        response.raise_for_status()
        stocks = response.json()
    except Exception as e:
        stocks = []
        print(f"三次スクリーニングAPI取得エラー: {e}")

    # 三次条件
    filtered = []
    for s in stocks:
        try:
            if (
                s.get("volume", 0) >= 100000 and
                s.get("trading_value", 0) >= 1e8 and
                500 <= s.get("price", 0) <= 3000 and
                30 <= s.get("RSI", 0) <= 70
            ):
                filtered.append(s)
        except Exception as e:
            print(f"フィルタ中エラー: {e}")

    return render_template('final.html', stocks=filtered)

if __name__ == '__main__':
    app.run()
