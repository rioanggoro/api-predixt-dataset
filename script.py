import joblib
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Database connection string
CONNECTION = "dbname='db_anjelina' user='db_anjelina_owner' host='ep-tight-snowflake-a1qhi62o.ap-southeast-1.aws.neon.tech' password='ruY6faXkm0wV' port='5432' sslmode='require'"

# Establish database connection
def get_db_connection():
    conn = psycopg2.connect(CONNECTION)
    return conn

# Paths to model and vectorizer files
model_path = "model/model_prediksi_harga.pkl"
vectorizer_path = "model/vectorizer.pkl"

try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
except FileNotFoundError:
    raise FileNotFoundError(f"File model or vectorizer not found at path: {model_path} or {vectorizer_path}")

def adjust_price_based_on_condition(item_name, base_price):
    # Your existing code for price adjustment
    pass

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "OK", "message": "API is running!"})

@app.route("/predict", methods=["GET"])
def predict():
    # Your existing code for price prediction
    pass

@app.route("/check_stock", methods=["GET"])
def check_stock():
    product_name = request.args.get("name", "").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT stock FROM "Products" WHERE name = %s;', (product_name,))
    stock = cur.fetchone()
    cur.close()
    conn.close()
    if stock:
        return jsonify({"status": "OK", "product_name": product_name, "stock": stock[0]})
    else:
        return jsonify({"status": "error", "message": "Product not found"}), 404

@app.route("/recommend_products", methods=["GET"])
def recommend_products():
    category = request.args.get("category", "").strip()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, description FROM products WHERE category = %s LIMIT 5;", (category,))
    products = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"status": "OK", "Products": [{"name": p[0], "description": p[1]} for p in products]})

@app.route("/faq", methods=["GET"])
def faq():
    question = request.args.get("Question", "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT answer FROM questions WHERE LOWER(question) LIKE %s LIMIT 1;", ('%' + question + '%',))
    answer = cur.fetchone()
    cur.close()
    conn.close()
    if answer:
        return jsonify({"status": "OK", "answer": answer[0]})
    else:
        return jsonify({"status": "error", "message": "Question not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
