from flask import Flask, jsonify, g
import sqlite3

app = Flask(__name__)
DATABASE = 'screened_stocks.db'  # SQLiteファイル名（スクリーン結果を保存しているファイル）

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 行を辞書のように扱う
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    db = get_db()
    cursor = db.execute('SELECT code, name, symbol, ROE, PER, OPM FROM stocks')
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
