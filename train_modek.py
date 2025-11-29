import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from sklearn.model_selection import train_test_split
import requests
import os
import json

print("Setup complete! TensorFlow version:", tf.__version__)

# ============================================
# ADD MORE CATEGORIES HERE (from 345 available)
# ============================================
CATEGORIES = [
    'cloud', 'sun', 'tree', 'cat', 'dog', 'house', 'mountain', 'flower',
    'car', 'airplane', 'bicycle', 'bird', 'butterfly', 'fish', 'apple',
    'banana', 'pizza', 'cake',  'face', 
]

NUM_CLASSES = len(CATEGORIES)
IMG_SIZE = 28
SAMPLES_PER_CATEGORY = 2000  # Reduce if you get memory errors
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

# ============================================
# IMPROVED MODEL FOR MORE CATEGORIES
# ============================================
model = Sequential([
    Conv2D(64, (3, 3), activation='relu', input_shape=(28, 28, 1)),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    
    Conv2D(256, (3, 3), activation='relu'),
    Dropout(0.3),
    
    Flatten(),
    Dense(512, activation='relu'),
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
    epochs=20,  # More epochs for more categories
    validation_data=(X_test, y_test),
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

test_loss, test_accuracy = model.evaluate(X_test, y_test)
print(f"\nTest Accuracy: {test_accuracy*100:.2f}%")

model.save('sketch_model.h5')
with open('categories.json', 'w') as f:
    json.dump(CATEGORIES, f)

with open('model_accuracy.txt', 'w') as f:
    f.write(str(test_accuracy))

print("✅ Model saved! Now run app.py to start the server.")
