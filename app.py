import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model dan vectorizer dari file
model_prediksi_harga = joblib.load("model/model_prediksi_harga.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")  # Pastikan vectorizer sudah di-fit

@app.route("/")
def index():
    return {"status": "OK", "message": "Hello World!"}, 200

@app.route("/predict", methods=["GET"])
def predict():
    nama_produk = request.args.get("nama", "")
    if not nama_produk:
        return jsonify({"status": "error", "message": "Nama produk tidak diberikan"}), 400

    # Transform nama produk menggunakan vectorizer yang sudah di-fit
    nama_produk_vectorized = vectorizer.transform([nama_produk])
    predicted_price = model_prediksi_harga.predict(nama_produk_vectorized)[0]

    return jsonify({"status": "OK", "predicted_price": predicted_price}), 200

if __name__ == "__main__":
    app.run(debug=True)
