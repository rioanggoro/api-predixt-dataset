import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Path ke model dan vectorizer yang telah disimpan
model_path = 'model/dataset_all_category.pkl'
vectorizer_path = 'model/vectorizer.pkl'

# Load model dan vectorizer dari file
try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
except FileNotFoundError as e:
    raise FileNotFoundError(f"Model atau vectorizer file tidak ditemukan di path: {e.filename}")

def adjust_price_based_on_condition(item_name, base_price):
    """
    Adjust the price based on condition keywords in the product name.
    """
    condition_keywords = {
        "baru": 0.95, "segel": 0.95, "original": 0.95, "authentic": 0.95,
    "bagus": 0.9, "baik": 0.9, "layak": 0.9, "bersih": 0.9, "terawat": 0.9,
    "terpakai": 0.8, "bekas": 0.8, "second": 0.8, "used": 0.8, "preloved": 0.8,
    "normal": 0.8, "sempurna": 0.8, "mulus": 0.8, "halus": 0.8,
    "kotor": 0.7, "berdebu": 0.7, "debu": 0.7, "tergores": 0.7, "warna pudar": 0.7,
    "usang": 0.7, "lama": 0.7, "belang": 0.7, "kusam": 0.7,
    "lecet": 0.6, "berminyak": 0.6, "terkelupas": 0.6, "retak kecil": 0.6, "penyok": 0.6,
    "terkikis": 0.6, "terbakar": 0.6, "menguning": 0.6, "berkerak": 0.6,
    "rusak": 0.5, "pecah": 0.5, "berlubang": 0.5, "sobek": 0.5, "retak": 0.5,
    "cacat": 0.5, "miring": 0.5, "tidak berfungsi": 0.5, "mati": 0.3,
    "parah": 0.4, "jelek": 0.4, "berjamur": 0.4, "berkarat": 0.4, "hancur": 0.4,
    "roboh": 0.4, "hilang bagian": 0.4, "tidak lengkap": 0.4, "tidak bisa dipakai": 0.2,
    "baret": 0.6, "tergores ringan": 0.6, "kering": 0.7, "terlalu lama": 0.5,
    "berkerut": 0.6, "kendor": 0.7, "terselip": 0.6, "terjatuh": 0.5,
    "bekas pakai": 0.8, "minim kerusakan": 0.8, "terguling": 0.6,
    "retak halus": 0.5, "rusak ringan": 0.5, "cacat kosmetik": 0.5,
    "berjamur sedikit": 0.4, "pudar warna": 0.7, "tidak berfungsi sepenuhnya": 0.5,
    "rapuh": 0.4, "pecah kecil": 0.5, "hilang bagian kecil": 0.5, "penggunaan jangka panjang": 0.6,
    "masih layak pakai": 0.8, "tidak lengkap": 0.7, "retak halus": 0.6,
    "bubuk": 0.4, "tergores sedikit": 0.7, "sudah dipakai lama": 0.5,
    "kemasannya rusak": 0.6, "terlalu usang": 0.5, "menyusut": 0.5,
    "kaca retak": 0.4, "lapisan luar pudar": 0.7, "sedikit kotor": 0.6,
    "berkarat sedikit": 0.5, "tumpul": 0.4, "rusak tidak signifikan": 0.5,
    "hilang aksesori": 0.4, "tertutup noda": 0.5, "tidak ada garansi": 0.6,
    "penurunan kualitas": 0.4, "menguning": 0.5, "berkerut": 0.7
    }
    
    # Penyesuaian harga berdasarkan kondisi
    adjustment_multiplier = 1.0
    for word, multiplier in condition_keywords.items():
        if word in item_name.lower():
            adjustment_multiplier = min(adjustment_multiplier, multiplier)

    adjusted_price = base_price * adjustment_multiplier
    return adjusted_price, adjustment_multiplier

# Valid categories and models
valid_categories = [
    "Celana", "Botol Susu", "Stroller", "Panci", "Blender", "Wajan",
    "Alat Olahraga", "Furniture", "Elektronik"
]

valid_models = [
    "Celana Chino", "Botol Susu Anti Gores", "Stroller Baby Jogger", "Panci Multifungsi",
    "Blender Kapasitas Besar", "Sofa Chesterfield", "iPhone 11", "iPhone 12", "iPhone 13",
    "TV SAMSUNG LED 32 Inch", "Mesin Cuci AQUA", "Mesin Cuci Sanken"
]

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "OK", "message": "API berjalan dengan baik!"})

@app.route("/predict", methods=["GET"])
def predict():
    # Ambil nama produk dari parameter query
    nama_produk = request.args.get("nama", "")
    if not nama_produk:
        return jsonify({"status": "error", "message": "Nama produk tidak diberikan"}), 400

    # Pisahkan kategori atau model dan kondisi dari input pengguna
    words = nama_produk.lower().split()
    detected_product = None

    for word in words:
        if any(word in model.lower() for model in valid_models):
            detected_product = word
            break

    if not detected_product:
        return jsonify({"status": "error", "message": "Produk tidak ada"}), 400

    try:
        # Transformasi nama produk dengan vectorizer
        item_name_vectorized = vectorizer.transform([detected_product])
        # Prediksi harga dasar menggunakan model
        base_price = model.predict(item_name_vectorized)[0]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error in prediction: {str(e)}"}), 500

    # Penyesuaian harga berdasarkan kondisi
    adjusted_price, adjustment_multiplier = adjust_price_based_on_condition(nama_produk, base_price)

    # Format harga ke IDR dan bulatkan ke ribuan
    formatted_price = "Rp{:,.0f}".format(round(adjusted_price, -3))

    return jsonify({"status": "OK", "predicted_price": formatted_price})

@app.route("/predictprice", methods=["GET"])
def predict_with_explanation():
    nama_produk = request.args.get("nama", "")
    if not nama_produk:
        return jsonify({"status": "error", "message": "Nama produk tidak diberikan"}), 400

    # Pisahkan kategori atau model dan kondisi dari input pengguna
    words = nama_produk.lower().split()
    detected_product = None

    for word in words:
        if any(word in model.lower() for model in valid_models):
            detected_product = word
            break

    if not detected_product:
        return jsonify({"status": "error", "message": "Produk tidak ada"}), 400

    try:
        # Transformasi nama produk dengan vectorizer
        item_name_vectorized = vectorizer.transform([detected_product])
        # Prediksi harga dasar menggunakan model
        base_price = model.predict(item_name_vectorized)[0]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error in prediction: {str(e)}"}), 500

    # Penyesuaian harga berdasarkan kondisi
    adjusted_price, adjustment_multiplier = adjust_price_based_on_condition(nama_produk, base_price)

    # Penjelasan tentang penyesuaian harga
    explanation = f"Harga dasar produk ini adalah Rp{base_price:.0f}. "
    if adjustment_multiplier == 1.0:
        explanation += "Produk ini dalam kondisi baru atau sangat baik, sehingga harga tidak ada perubahan."
    elif adjustment_multiplier < 1.0:
        explanation += f"Harga produk ini diturunkan karena kondisi produk yang lebih rendah, dengan penyesuaian faktor {adjustment_multiplier}."
    else:
        explanation += "Harga produk ini disesuaikan berdasarkan kondisi produk."

    # Format harga ke IDR dan bulatkan ke ribuan
    formatted_price = "Rp{:,.0f}".format(round(adjusted_price, -3))

    return jsonify({
        "status": "OK",
        "predicted_price": formatted_price,
        "explanation": explanation  # Menambahkan penjelasan
    })

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

