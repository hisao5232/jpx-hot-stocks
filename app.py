from flask import Flask, render_template
import sqlite3
import pandas as pd

app = Flask(__name__)

DB_PATH = "jpx_hot_stocks.db"

@app.route("/")
def index():
    # SQLiteからスクリーニング結果を読み込み
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM screened_stocks", conn)
    conn.close()

    # DataFrameをHTMLテーブルとして渡す
    return render_template("index.html", stocks=df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
