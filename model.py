import joblib

model_path = 'model/dataset_all_category.pkl'
try:
    model = joblib.load(model_path)
    print("Model berhasil dimuat")
except Exception as e:
    print(f"Error saat memuat model: {str(e)}")
