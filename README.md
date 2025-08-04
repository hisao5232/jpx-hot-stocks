# JPX Hot Stocks 🔥  
_A web application to screen hot stocks from the Tokyo Stock Exchange (Prime Market)_

東証プライム市場から「今、注目すべき銘柄」をスクリーニングするWebアプリです。

---

## 🚀 Features | 主な機能

- 🔍 Screen Japanese stocks (Prime Market only) based on technical signals
- 📈 Golden Cross detection (25MA > 75MA)
- 🔥 Volume spike screening (today > 2x average of last 5 days)
- 💡 Clean stock list UI with chart visualization
- 🗃 SQLite-based lightweight storage
- 🌐 Deployable to [Render](https://render.com/) or any cloud platform

---

## 📊 Screener Logic | スクリーニング条件

**🧪 Stage 1: Technical Focus**
- Belongs to JPX Prime Market
- 25-day moving average > 75-day moving average (Golden Cross)
- Today's volume > 2× 5-day average volume
- Closing price > 25-day moving average

> Further stages will include fundamental metrics and earnings data.
> 今後は決算情報やファンダメンタル指標によるスクリーニングも実装予定です。

---

## 🛠 Tech Stack | 技術構成

- **Python 3.10+**
- **Flask** – Lightweight backend framework
- **Jinja2** – Template rendering
- **Chart.js / Plotly.js** – Interactive chart rendering
- **SQLite** – Local DB for price and volume data
- **Render** – For production deployment

---

## 📦 Installation | インストール手順

```bash
# 1. Clone this repository
git clone https://github.com/your-username/jpx-hot-stocks.git
cd jpx-hot-stocks

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app locally
python app.py
```
Then open http://localhost:5000 in your browser.

---

🌐 Deployment | デプロイ方法（Renderなど）

1. Push to GitHub


2. Create a new "Web Service" on Render


3. Set:

Build Command: pip install -r requirements.txt

Start Command: python app.py

Environment: Python 3.10+



4. Auto-deploy from your GitHub repository




---

📁 Directory Structure | ディレクトリ構成（予定）

jpx-hot-stocks/
├── app.py                # Main Flask app
├── screener.py           # Screener logic
├── models.py             # DB schema and queries
├── static/               # CSS / JS
├── templates/            # HTML templates (Jinja2)
├── data/                 # Stock price CSV / DB
├── requirements.txt
├── README.md
└── Procfile              # For Render deployment


---

📌 License

This project is licensed under the MIT License.


---

👤 Author

Created by hisao
Inspired by a desire to make Japanese stock screening smarter and accessible.


---

Let’s find hot opportunities in the Tokyo market.🔥
日本株の“今、熱い銘柄”を見つけよう！

---
