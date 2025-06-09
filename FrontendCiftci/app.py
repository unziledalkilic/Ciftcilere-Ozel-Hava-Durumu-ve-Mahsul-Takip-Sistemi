# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from model_test import CropPredictionModel
import json

app = Flask(__name__)
CORS(app)  # CORS sorunlarını çözmek için

# Model instance'ını oluştur
predictor = CropPredictionModel()

@app.route('/predict', methods=['POST'])
def predict():
    """Tekil mahsul tahmini endpoint'i"""
    try:
        data = request.json
        
        # Gerekli parametreleri al
        city = data.get('city')
        crop = data.get('crop')
        soil_type = data.get('soil_type')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        
        # Giriş verilerini kontrol et
        if not all([city, crop, soil_type, temperature is not None, humidity is not None, rainfall is not None]):
            return jsonify({
                'success': False,
                'error': 'Eksik parametreler. Lütfen tüm alanları gönderin.'
            }), 400

        # Tahmin yap
        yield_score = predictor.predict_yield(
            city, crop, soil_type, temperature, humidity, rainfall
        )
        
        return jsonify({
            'success': True,
            'yield_score': yield_score,
            'inputs': data
        })
    
    except Exception as e:
        print(f"Hata /predict: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """Birden fazla mahsul için toplu tahmin endpoint'i"""
    try:
        data = request.json
        city = data.get('city')
        soil_type = data.get('soil_type')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        
        # Giriş verilerini kontrol et
        if not all([city, soil_type, temperature is not None, humidity is not None, rainfall is not None]):
            return jsonify({
                'success': False,
                'error': 'Eksik parametreler (şehir, toprak, hava durumu). Lütfen tüm alanları gönderin.'
            }), 400

        crops = predictor.get_available_options()['crops']
        results = []
        
        for crop in crops:
            yield_score = predictor.predict_yield(
                city, crop, soil_type, temperature, humidity, rainfall
            )
            results.append({
                'crop': crop,
                'yield_score': yield_score
            })
        
        # Skorlara göre sırala (en yüksekten en düşüğe)
        results.sort(key=lambda x: x['yield_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'predictions': results,
            'city': city,
            'conditions': {
                'soil_type': soil_type,
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall
            }
        })
    
    except Exception as e:
        print(f"Hata /batch_predict: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/options', methods=['GET'])
def get_options():
    """Mevcut seçenekleri (şehirler, mahsuller, toprak tipleri) döndür"""
    return jsonify(predictor.get_available_options())

@app.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    # Modelin yüklenip yüklenmediğini kontrol edebiliriz
    model_loaded_status = predictor.model is not None
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded_status
    })

if __name__ == '__main__':
    print("🚀 Flask API başlatılıyor...")
    print("📍 Endpoint'ler:")
    print("    POST /predict - Tekil tahmin yapar")
    print("    POST /batch_predict - Mevcut hava koşullarına göre tüm mahsuller için toplu tahmin yapar") 
    print("    GET /options - Kullanılabilir şehir, mahsul ve toprak tipi seçeneklerini döndürür")
    print("    GET /health - API sağlık kontrolü yapar")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
