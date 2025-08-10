from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

app = Flask(__name__)

@app.route('/')
def index():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        stocks = response.json()
    except Exception as e:
        stocks = []
        print(f"API取得エラー: {e}")

    return render_template('index.html', stocks=stocks)

if __name__ == '__main__':
    app.run()
