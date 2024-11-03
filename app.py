import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model dan vectorizer dari file
model_path = "/Users/rioanggoro/Documents/skripsi/model/deployment/model/model_prediksi_harga.pkl"
vectorizer_path = "/Users/rioanggoro/Documents/skripsi/model/deployment/model/vectorizer.pkl"

# Periksa apakah file ada untuk menghindari error
try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
except FileNotFoundError:
    raise FileNotFoundError(f"File model atau vectorizer tidak ditemukan di path: {model_path} atau {vectorizer_path}")

def adjust_price_based_on_condition(item_name, base_price):
    # Daftar kata kunci kondisi dan bobot diskon
    condition_keywords = {
        "baru": 1.0, "segel": 1.0, "original": 1.0, "authentic": 1.0,
        "bagus": 0.9, "baik": 0.9, "layak": 0.9, "bersih": 0.9, "terawat": 0.9,
        "terpakai": 0.8, "bekas": 0.8, "second": 0.8, "used": 0.8, "preloved": 0.8,
        "normal": 0.8, "sempurna": 0.8, "mulus": 0.8, "halus": 0.8,
        "kotor": 0.7, "berdebu": 0.7, "debu": 0.7, "tergores": 0.7, "warna pudar": 0.7,
        "usang": 0.7, "lama": 0.7, "belang": 0.7, "kusam": 0.7,
        "lecet": 0.6, "berminyak": 0.6, "terkelupas": 0.6, "retak kecil": 0.6, "penyok": 0.6,
        "terkikis": 0.6, "terbakar": 0.6, "menguning": 0.6, "berkerak": 0.6,
        "rusak": 0.5, "pecah": 0.5, "berlubang": 0.5, "sobek": 0.5, "retak": 0.5,
        "cacat": 0.5, "miring": 0.5, "tidak berfungsi": 0.5, "mati": 0.5,
        "parah": 0.4, "jelek": 0.4, "berjamur": 0.4, "berkarat": 0.4, "hancur": 0.4,
        "roboh": 0.4, "hilang bagian": 0.4, "tidak lengkap": 0.4, "tidak bisa dipakai": 0.4
    }
    # Gender adjustment
    gender_keywords = {
        "pria, laki-laki,cowo, cowok": 1.0,
        "wanita, perempuan,cewek,cewe": 1.0
    }
    adjustment_multiplier = 1.0
    gender_multiplier = 1.0

    for word, multiplier in condition_keywords.items():
        if word in item_name.lower():
            adjustment_multiplier = min(adjustment_multiplier, multiplier)

    for gender, gender_adjust in gender_keywords.items():
        if gender in item_name.lower():
            gender_multiplier = gender_adjust

    adjusted_price = base_price * adjustment_multiplier * gender_multiplier
    return adjusted_price

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "OK", "message": "API berjalan dengan baik!"})

@app.route("/predict", methods=["GET"])
def predict():
    nama_produk = request.args.get("nama", "")
    if not nama_produk:
        return jsonify({"status": "error", "message": "Nama produk tidak diberikan"}), 400

     # Prediksi harga dasar
    item_name_vectorized = vectorizer.transform([nama_produk])
    base_price = model.predict(item_name_vectorized)[0]

    # Penyesuaian harga berdasarkan kondisi
    adjusted_price = adjust_price_based_on_condition(nama_produk, base_price)

    # Format ke IDR dan bulatkan ke ribuan
    formatted_price = "Rp{:,.0f}".format(round(adjusted_price, -3))

    return jsonify({"status": "OK", "predicted_price": formatted_price})

if __name__ == "__main__":
    app.run(debug=True)

