# model_test.py
import joblib
import numpy as np
import json

class CropPredictionModel:
    def __init__(self):
        """Model ve encoder'ları yükle"""
        # Model dosyalarının doğru yolda olduğundan emin olun
        try:
            self.model = joblib.load('crop_prediction_model.pkl')
            self.city_encoder = joblib.load('city_encoder.pkl')
            self.crop_encoder = joblib.load('crop_encoder.pkl')
            self.soil_encoder = joblib.load('soil_encoder.pkl')
            
            # Encoder bilgilerini yükle
            with open('encoders_info.json', 'r', encoding='utf-8') as f:
                self.encoders_info = json.load(f)
            print("✅ Model ve encoder'lar başarıyla yüklendi.")
        except FileNotFoundError as e:
            print(f"Hata: Gerekli model veya encoder dosyaları bulunamadı. Lütfen tüm dosyaların 'proje_klasoru' içinde olduğundan emin olun. Detay: {e}")
            # Uygulamanın çökmesini önlemek için boş veya varsayılan değerler atayabilirsiniz
            self.model = None
            self.city_encoder = None
            self.crop_encoder = None
            self.soil_encoder = None
            self.encoders_info = {'cities': [], 'crops': [], 'soil_types': []}
        except Exception as e:
            print(f"Model yüklenirken bilinmeyen bir hata oluştu: {e}")
            self.model = None
            self.city_encoder = None
            self.crop_encoder = None
            self.soil_encoder = None
            self.encoders_info = {'cities': [], 'crops': [], 'soil_types': []}


    def predict_yield(self, city, crop, soil_type, temperature, humidity, rainfall):
        """Mahsul verimini tahmin et"""
        if not self.model: # Model yüklenemediyse
            return 50.0 # Varsayılan değer döndür

        try:
            # Kategorik değişkenleri encode et
            # OHE: Tahmin için gelen şehir, mahsul veya toprak tipi eğitim setinde yoksa hata verecektir.
            # Bunu yakalamak ve uygun şekilde ele almak önemlidir.
            try:
                city_enc = self.city_encoder.transform([city])[0]
            except ValueError:
                print(f"Uyarı: '{city}' şehri eğitim setinde bulunamadı. Varsayılan değer kullanılıyor.")
                city_enc = -1 # Veya bilinen bir varsayılan/ortalama kod

            try:
                crop_enc = self.crop_encoder.transform([crop])[0]
            except ValueError:
                print(f"Uyarı: '{crop}' mahsulü eğitim setinde bulunamadı. Varsayılan değer kullanılıyor.")
                crop_enc = -1

            try:
                soil_enc = self.soil_encoder.transform([soil_type])[0]
            except ValueError:
                print(f"Uyarı: '{soil_type}' toprak tipi eğitim setinde bulunamadı. Varsayılan değer kullanılıyor.")
                soil_enc = -1
            
            # Tahmin yap
            X_pred = np.array([[city_enc, crop_enc, soil_enc, temperature, humidity, rainfall]])
            prediction = self.model.predict(X_pred)[0]
            
            return max(0, min(100, round(prediction, 2)))
        except Exception as e:
            print(f"Hata: Tahmin sırasında bir sorun oluştu: {e}")
            return 50.0 # Hata durumunda varsayılan değer
    
    def get_available_options(self):
        """Mevcut seçenekleri döndür"""
        if not self.encoders_info: # Encoder bilgileri yüklenemediyse
            return {'cities': [], 'crops': [], 'soil_types': []}
        return {
            'cities': self.encoders_info.get('city_classes', []),
            'crops': self.encoders_info.get('crop_classes', []),
            'soil_types': self.encoders_info.get('soil_classes', [])
        }

# Test
if __name__ == "__main__":
    predictor = CropPredictionModel()
    
    # Test tahmini
    result = predictor.predict_yield(
        city='İstanbul',
        crop='Buğday', 
        soil_type='Tınlı',
        temperature=20,
        humidity=60,
        rainfall=45
    )
    
    print(f"Tahmin edilen verim skoru: {result}")
    print(f"Mevcut şehirler: {predictor.get_available_options()['cities']}")
