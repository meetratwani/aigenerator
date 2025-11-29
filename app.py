# ============================================
# IMPORTS FIRST - BEFORE ANYTHING ELSE
# ============================================
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import requests
import os
import json
import time

# ============================================
# CREATE APP IMMEDIATELY AFTER IMPORTS
# ============================================
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("✅ Flask app created")

# ============================================
# LOAD MODEL AFTER APP IS CREATED
# ============================================
print("Loading model...")

if not os.path.exists('sketch_model.h5'):
    print("❌ Model not found! Run train_model.py first.")
    exit()

model = keras.models.load_model('sketch_model.h5')

with open('categories.json', 'r') as f:
    CATEGORIES = json.load(f)

NUM_CLASSES = len(CATEGORIES)

try:
    with open('model_accuracy.txt', 'r') as f:
        test_accuracy = float(f.read())
except:
    test_accuracy = 0.0

print(f"✅ Model loaded! Categories: {CATEGORIES}")
os.makedirs('static', exist_ok=True)

# ============================================
# HELPER FUNCTIONS
# ============================================
def predict_drawing(image_data):
    if isinstance(image_data, Image.Image):
        img = image_data.convert('L').resize((28, 28))
        img_array = 255 - np.array(img)
    else:
        img_array = image_data
    
    img_array = img_array.reshape(1, 28, 28, 1).astype('float32') / 255.0
    predictions = model.predict(img_array, verbose=0)[0]
    predicted_idx = np.argmax(predictions)
    
    return {
        'prediction': CATEGORIES[predicted_idx],
        'confidence': float(predictions[predicted_idx]),
        'all_predictions': {CATEGORIES[i]: float(predictions[i]) for i in range(NUM_CLASSES)}
    }

def generate_with_pollinations(prompt):
    try:
        encoded_prompt = requests.utils.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&timestamp={int(time.time())}"
        test = requests.get(image_url, timeout=15)
        if test.status_code == 200:
            return image_url
        raise Exception(f"Pollinations returned {test.status_code}")
    except requests.exceptions.Timeout:
        raise Exception("Image generation timed out")
    except Exception as e:
        raise Exception(f"Generation failed: {str(e)}")

# ============================================
# ROUTES - DEFINED AFTER APP IS CREATED
# ============================================
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Sketch Recognition API',
        'status': 'online',
        'endpoints': {
            '/api/health': 'GET - Health check',
            '/api/predict': 'POST - Submit drawing',
            '/api/categories': 'GET - Get categories',
            '/api/generate-image': 'POST - Generate image'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'Server is running',
        'model': 'Sketch Recognition Model',
        'categories': CATEGORIES,
        'num_categories': NUM_CLASSES,
        'test_accuracy': f"{test_accuracy*100:.2f}%",
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({'categories': CATEGORIES, 'count': NUM_CLASSES}), 200

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        canvas_data = data.get('canvas_data')
        description = data.get('description', '')
        
        if not canvas_data:
            return jsonify({'error': 'No canvas data', 'success': False}), 400
        
        if 'base64,' in canvas_data:
            canvas_data = canvas_data.split('base64,')[1]
        
        image_data = base64.b64decode(canvas_data)
        image = Image.open(BytesIO(image_data)).convert('L').resize((28, 28))
        img_array = 255 - np.array(image)
        
        result = predict_drawing(img_array)
        
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'confidence': f"{result['confidence']:.1%}",
            'confidence_value': result['confidence'],
            'all_predictions': {k: f"{v:.1%}" for k, v in result['all_predictions'].items()},
            'timestamp': datetime.now().isoformat(),
            'categories': CATEGORIES
        }), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prediction = data.get('prediction', '')
        style = data.get('style', 'realistic')
        
        if not prediction:
            return jsonify({'error': 'No prediction', 'success': False}), 400
        
        prompts = {
            'realistic': f"photorealistic {prediction}, 4k, professional photography",
            'artistic': f"artistic painting of {prediction}, vibrant colors",
            'cartoon': f"cute cartoon {prediction}, colorful, child-friendly",
            'sketch': f"pencil sketch of {prediction}, detailed shading"
        }
        
        prompt = prompts.get(style, prompts['realistic'])
        image_url = generate_with_pollinations(prompt)
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'prompt': prompt,
            'prediction': prediction,
            'style': style,
            'method': 'pollinations'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

# ============================================
# RUN SERVER
# ============================================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SKETCH RECOGNITION API")
    print("="*60)
    print(f"📊 Categories: {', '.join(CATEGORIES)}")
    print(f"📈 Accuracy: {test_accuracy*100:.2f}%")
    print(f"🌐 Server: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
