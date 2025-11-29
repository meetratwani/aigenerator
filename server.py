import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from sklearn.model_selection import train_test_split
import requests
import os
import json
from PIL import Image
import io
import time

print("Setup complete! TensorFlow version:", tf.__version__)

from flask import Flask, request, jsonify, make_response, send_file
from flask_cors import CORS
import base64
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Global CORS, removes the need for @cross_origin

# Prevent TensorFlow from allocating all GPU memory at once (optional, only if training crashes)
# physical_devices = tf.config.list_physical_devices('GPU')
# if physical_devices:
#     tf.config.experimental.set_memory_growth(physical_devices[0], True)

CATEGORIES = ['cloud', 'sun', 'tree', 'cat', 'dog', 'house', 'mountain', 'flower']
NUM_CLASSES = len(CATEGORIES)
IMG_SIZE = 28
SAMPLES_PER_CATEGORY = 2000  # Reduce if you see OOM errors
BASE_URL = 'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/'

print(f"Training model for {NUM_CLASSES} categories: {CATEGORIES}")

def download_category(category):
    url = BASE_URL + category.replace('_', '%20') + '.npy'
    filename = f'{category}.npy'
    if not os.path.exists(filename):
        print(f"Downloading {category}...")
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
    return filename

for category in CATEGORIES:
    download_category(category)
print("Download complete!")

def load_data(categories, samples_per_category):
    X, y = [], []
    for idx, category in enumerate(categories):
        data = np.load(f'{category}.npy')[:samples_per_category]
        X.append(data)
        y.append([idx] * len(data))
        print(f"Loaded {len(data)} samples for {category}")

    X = np.concatenate(X).reshape(-1, 28, 28, 1).astype('float32') / 255.0
    y = keras.utils.to_categorical(np.concatenate(y), NUM_CLASSES)
    return X, y

X, y = load_data(CATEGORIES, SAMPLES_PER_CATEGORY)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training: {X_train.shape}, Testing: {X_test.shape}")

model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(128, (3, 3), activation='relu'),
    Dropout(0.25),
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(NUM_CLASSES, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2)

history = model.fit(
    X_train, y_train,
    batch_size=128,
    epochs=15,
    validation_data=(X_test, y_test),
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_accuracy*100:.2f}%")

model.save('sketch_model.h5')
with open('categories.json', 'w') as f:
    json.dump(CATEGORIES, f)
print("Model saved!")

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

test_img = X_test[0]
result = predict_drawing(test_img)
print(f"\nTest Prediction: {result['prediction']} ({result['confidence']:.2%} confidence)")
print("\n✅ Model ready! Use predict_drawing() function with your frontend.")

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

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400

        canvas_data = data.get('canvas_data')
        description = data.get('description', '')

        if not canvas_data:
            return jsonify({'error': 'No canvas data provided', 'success': False}), 400

        try:
            if 'base64,' in canvas_data:
                canvas_data = canvas_data.split('base64,')[1]

            image_data = base64.b64decode(canvas_data)
            image = Image.open(BytesIO(image_data)).convert('L').resize((28, 28))
            img_array = 255 - np.array(image)
        except Exception as e:
            return jsonify({'error': f'Invalid image data: {str(e)}', 'success': False}), 400

        result = predict_drawing(img_array)
        response_data = {
            'success': True,
            'prediction': result['prediction'],
            'confidence': f"{result['confidence']:.1%}",
            'confidence_value': result['confidence'],
            'all_predictions': {k: f"{v:.1%}" for k, v in result['all_predictions'].items()},
            'all_predictions_values': result['all_predictions'],
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'categories': CATEGORIES
        }

        print(f"✅ Prediction: {result['prediction']} | Confidence: {result['confidence']:.1%} | Description: {description}")
        return jsonify(response_data), 200

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify({
        'categories': CATEGORIES,
        'count': NUM_CLASSES
    }), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Sketch Recognition API',
        'endpoints': {
            '/api/health': 'GET - Health check',
            '/api/predict': 'POST - Submit drawing for prediction',
            '/api/categories': 'GET - Get available categories'
        },
        'status': 'online'
    }), 200

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prediction = data.get('prediction', '')
        style = data.get('style', 'realistic')
        if not prediction:
            return jsonify({'error': 'No prediction provided', 'success': False}), 400

        prompts = {
            'realistic': f"a highly detailed, photorealistic {prediction}, professional photography, 4k, sharp focus, natural lighting",
            'artistic': f"a beautiful artistic painting of a {prediction}, oil painting style, vibrant colors, masterpiece",
            'cartoon': f"a cute cartoon illustration of a {prediction}, colorful, friendly, child-friendly art style",
            'sketch': f"a detailed pencil sketch of a {prediction}, professional drawing, shading, realistic proportions"
        }
        prompt = prompts.get(style, prompts['realistic'])

        print(f"🎨 Generating image for: {prediction} (style: {style})")
        # Try Hugging Face, fallback to Pollinations, else error
        try:
            image_url = generate_with_huggingface(prompt)
            if image_url:
                return jsonify({
                    'success': True,
                    'image_url': image_url,
                    'prompt': prompt,
                    'prediction': prediction,
                    'style': style,
                    'method': 'huggingface'
                }), 200
        except Exception as e:
            print(f"Hugging Face failed: {e}")

        try:
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
            print(f"Pollinations failed: {e}")
            return jsonify({'error': 'Image generation failed', 'success': False, 'details': str(e)}), 500

    except Exception as e:
        print(f"❌ Error in generate_image: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

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

def generate_with_huggingface(prompt):
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    HF_TOKEN = None  # Optionally add your HuggingFace token here for higher rate limit
    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    if response.status_code == 200:
        image_filename = os.path.join('static', f"generated_{int(time.time())}.png")
        with open(image_filename, 'wb') as f:
            f.write(response.content)
        return f"/static/{os.path.basename(image_filename)}"
    elif response.status_code == 503:
        raise Exception("Hugging Face model is loading. Try again in 30 seconds.")
    else:
        raise Exception(f"HuggingFace API error: {response.status_code}")

@app.route('/static/<filename>')
def serve_image(filename):
    try:
        return send_file(os.path.join('static', filename), mimetype='image/png')
    except:
        return jsonify({'error': 'Image not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SKETCH RECOGNITION API SERVER")
    print("="*60)
    print(f"📊 Model Categories: {', '.join(CATEGORIES)}")
    print(f"📈 Test Accuracy: {test_accuracy*100:.2f}%")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🔗 Health Check: http://localhost:5000/api/health")
    print(f"🎨 Prediction Endpoint: http://localhost:5000/api/predict")
    print("="*60)
    print("✅ CORS enabled globally")
    print("✅ Ready to accept drawing submissions!")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )

