from flask import Flask, jsonify, g, request
import sqlite3

app = Flask(__name__)

DATABASES = {
    "fundamental": "screened_stocks.db",
    "technical": "technical_screened.db"
}

def get_db(db_name):
    db = getattr(g, f'_database_{db_name}', None)
    if db is None:
        db = getattr(g, f'_database_{db_name}', None)
        db = g.__setattr__(f'_database_{db_name}', sqlite3.connect(DATABASES[db_name]))
        db = getattr(g, f'_database_{db_name}')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    for db_name in DATABASES:
        db = getattr(g, f'_database_{db_name}', None)
        if db is not None:
            db.close()

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    # ?type=fundamental または ?type=technical で指定
    stock_type = request.args.get('type', 'fundamental')
    if stock_type not in DATABASES:
        return jsonify({"error": "Invalid type parameter"}), 400
    
    db = get_db(stock_type)
    cursor = db.execute('SELECT code, name, symbol, ROE, PER, OPM FROM stocks')
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
