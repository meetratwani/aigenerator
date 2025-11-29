# Drawing Studio with AI Sketch Recognition

## Prerequisites
Make sure you have Python 3.7+ installed with the following packages:

```bash
pip install flask flask-cors numpy pillow tensorflow scikit-learn
```

## How to Run

### Step 1: Train the Model & Start Server
Run the server.py file in Python:

```bash
python server.py
```

**This will:**
1. Download the Quick Draw dataset (if not already downloaded)
2. Train the sketch recognition model
3. Start the Flask API server on `http://localhost:5000`

⏳ **Note:** First run takes 10-15 minutes to download and train. Subsequent runs will load the saved model.

### Step 2: Open the Drawing App
Once the server is running, open the `drawing_app.html` file in your browser:

```
Right-click on drawing_app.html → Open with → Your Browser
```

Or use the file path:
```
file:///c:/Users/Meet/OneDrive/Desktop/ArpitSir/drawing_app.html
```

## Features

✨ **Drawing Features:**
- Draw freely with adjustable brush (color, size, opacity)
- Undo/Redo with full history (Ctrl+Z, Ctrl+Y)
- Clear canvas with confirmation
- Dark/Light theme toggle

🎯 **AI Recognition:**
- Draw a sketch and submit to the AI model
- Get instant prediction with confidence score
- See predictions for all 8 categories (cloud, sun, tree, cat, dog, house, mountain, flower)
- Add optional description to your drawing

💾 **Actions:**
- Download your drawing as PNG
- Save prediction results
- Export with metadata

## API Endpoint

**POST** `http://localhost:5000/api/predict`

Request:
```json
{
  "canvas_data": "data:image/png;base64,...",
  "description": "optional description"
}
```

Response:
```json
{
  "success": true,
  "prediction": "cat",
  "confidence": "95.3%",
  "all_predictions": {
    "cloud": "0.2%",
    "sun": "0.1%",
    "tree": "0.3%",
    "cat": "95.3%",
    "dog": "3.8%",
    "house": "0.2%",
    "mountain": "0.1%",
    "flower": "0.0%"
  },
  "description": "optional description"
}
```

## Categories Recognized
- 🌥️ Cloud
- ☀️ Sun
- 🌳 Tree
- 🐱 Cat
- 🐕 Dog
- 🏠 House
- ⛰️ Mountain
- 🌸 Flower

## Troubleshooting

**"Error: Cannot connect to server"**
- Make sure `server.py` is running
- Check if Flask is installed: `pip install flask flask-cors`
- Try accessing `http://localhost:5000/api/health` in browser

**"Model takes too long to train"**
- First training includes dataset download (~1GB)
- Subsequent runs load from cache
- You can reduce `SAMPLES_PER_CATEGORY` in server.py for faster training

**Canvas not drawing**
- Check browser console (F12) for errors
- Ensure canvas is in focus
- Try a different browser

## Model Information
- **Architecture:** CNN (Convolutional Neural Network)
- **Dataset:** Google Quick Draw
- **Input Size:** 28x28 pixels
- **Categories:** 8 sketch types
- **Accuracy:** ~85-90% (varies by category)

Enjoy your Drawing Studio! 🎨✨
