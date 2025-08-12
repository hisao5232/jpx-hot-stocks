from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_URL") 

app = Flask(__name__)

def fetch_stocks(stock_type):
    try:
        url = f"{API_BASE_URL}?type={stock_type}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API取得エラー ({stock_type}): {e}")
        return []

@app.route("/")
def index():
    stocks = fetch_stocks("fundamental")
    return render_template("index.html", stocks=stocks)

@app.route("/technical")
def technical():
    stocks = fetch_stocks("technical")
    return render_template("technical.html", stocks=stocks)

@app.route("/final")
def final():
    stocks = fetch_stocks("final")
    return render_template("final.html", stocks=stocks)

if __name__ == "__main__":
    app.run(debug=True)
