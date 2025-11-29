# 🔧 Drawing Studio - Fetch Error Troubleshooting

## Problem: "Unable to Fetch" Error

If you're seeing fetch errors when submitting drawings, follow this guide step-by-step.

---

## ❌ Common Error Messages

```
1. "Failed to fetch"
2. "Server is not running"
3. "Cannot connect to localhost:5000"
4. "CORS error"
5. "Network request failed"
```

---

## ✅ Step-by-Step Fix

### Step 1: Make Sure Server is Running

**Check if server.py is running:**
1. Look for a PowerShell/Terminal window with server output
2. Should show: `🚀 Starting Flask API Server on http://localhost:5000`
3. Should show: `📊 Model Categories: [...]`

**If server is NOT running:**

Open PowerShell in the ArpitSir folder:
```powershell
cd C:\Users\Meet\OneDrive\Desktop\ArpitSir
python server.py
```

**Wait for output:**
```
Setup complete! TensorFlow version: ...
Loading ... samples for cloud
Loading ... samples for sun
...
Model ready! Use predict_drawing() function with your frontend.
🚀 Starting Flask API Server on http://localhost:5000
📊 Model Categories: ['cloud', 'sun', 'tree', 'cat', 'dog', 'house', 'mountain', 'flower']
📈 Test Accuracy: XX.XX%
```

**⏳ IMPORTANT:** First run takes 10-15 minutes to download and train. Subsequent runs are faster.

### Step 2: Wait for Model Training (First Time Only)

When you first run `python server.py`:

```
Timeline:
0-5 min:   Downloading dataset (~1GB)
5-10 min:  Training model
10-15 min: Saving weights
15+ min:   "Starting Flask API Server" ← Server is ready!
```

**DO NOT open drawing app until you see "Starting Flask API Server"**

### Step 3: Verify Server is Responding

Open your web browser and go to:
```
http://localhost:5000/api/health
```

**Expected response:**
```json
{"status":"Server is running","model":"Sketch Recognition Model"}
```

If you see this, server is working! ✅

### Step 4: Check Port is Available

If server won't start with "Port 5000 in use" error:

```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with the number)
taskkill /PID <PID> /F
```

Then try starting server again:
```powershell
python server.py
```

### Step 5: Verify Dependencies

Make sure all packages are installed:

```powershell
# Install/update all dependencies
pip install -r requirements.txt

# Or install individually
pip install flask flask-cors tensorflow keras numpy pillow scikit-learn requests
```

Check specific packages:
```powershell
python -c "import flask; print('Flask OK')"
python -c "import tensorflow; print('TensorFlow OK')"
python -c "from flask_cors import CORS; print('Flask-CORS OK')"
```

### Step 6: Test the Drawing App

1. **Close and reopen drawing_app.html** (refresh with Ctrl+F5)
2. **Draw something simple** (circle, triangle, etc.)
3. **Add optional description**
4. **Click "Submit Drawing"**
5. **Wait 2-5 seconds** for processing

---

## 🔍 Debugging Tips

### Open Browser Console
```
Press: F12 (or Ctrl+Shift+I)
Go to: Console tab
Look for: Error messages in red
```

**Copy any error messages and read them carefully.**

### Check Server Terminal

Look at the PowerShell window where server is running:
- Error messages appear in red
- Successful predictions show prediction details
- Connection issues show error stack traces

### Enable Verbose Logging

Add this to your `server.py` before `app.run()`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test with Simple Drawing

Instead of complex drawings:
1. Draw a **simple circle** (for sun)
2. Draw a **simple square** (for house)
3. These have higher accuracy

---

## 🚨 If Nothing Works

### Complete Reset

```powershell
# 1. Stop server (Ctrl+C in server terminal)

# 2. Delete cached files
Remove-Item -Path "sketch_model.h5" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "categories.json" -Force -ErrorAction SilentlyContinue

# 3. Reinstall all packages
pip install --upgrade --force-reinstall tensorflow flask flask-cors

# 4. Start fresh
python server.py
```

### Check Windows Firewall

If server starts but fetch fails:
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Add Python to allowed apps

### Try Different Port

Edit `server.py`, change last line:
```python
app.run(debug=True, port=8000)  # Changed from 5000
```

Also update `drawing_app.html`:
```javascript
const response = await fetch('http://localhost:8000/api/predict', {
```

---

## 📋 Verification Checklist

- [ ] Python is installed (`python --version`)
- [ ] Dependencies are installed (`pip list` shows flask, tensorflow)
- [ ] Server is running in a terminal window
- [ ] Server shows "Starting Flask API Server" message
- [ ] Browser can access `http://localhost:5000/api/health`
- [ ] Browser console (F12) shows no errors
- [ ] Canvas drawing works
- [ ] Drawing app HTML file is open in browser
- [ ] You've waited for model training to complete (first time)

---

## 💡 Quick Fixes (Try These First)

### Fix 1: Refresh Browser
```
Ctrl+F5  (Hard refresh - clears cache)
```

### Fix 2: Close/Reopen App
```
1. Close drawing_app.html in browser
2. Wait 5 seconds
3. Reopen drawing_app.html
4. Try submitting again
```

### Fix 3: Restart Server
```
1. Close PowerShell terminal (Ctrl+C)
2. Wait 5 seconds
3. Run: python server.py
4. Wait for "Starting Flask API Server"
5. Try again in app
```

### Fix 4: Use Simplified Drawing
```
- Draw very simple shapes
- Keep drawing in center
- Use dark pen (black/dark blue)
- Keep shapes connected
```

---

## 🆘 Still Not Working?

Check these files for detailed info:

| Issue | Read This File |
|-------|--------------|
| Setup problem | SETUP_INSTRUCTIONS.md |
| How API works | WORKFLOW_GUIDE.md |
| Server issues | README.md - Troubleshooting |
| Architecture | ARCHITECTURE.md |
| Quick reference | QUICK_START.md |

---

## 📞 Error Messages & Solutions

### "Failed to fetch"
```
Cause: Server not running
Fix: Run python server.py and wait for "Starting Flask API Server"
```

### "Server is not running"
```
Cause: Health check failed
Fix: Same as above - start server
```

### "CORS error"
```
Cause: Flask-CORS not installed
Fix: pip install flask-cors
```

### "Port 5000 already in use"
```
Cause: Another app using port 5000
Fix: netstat -ano | findstr :5000
     taskkill /PID <PID> /F
```

### "No module named 'flask'"
```
Cause: Flask not installed
Fix: pip install -r requirements.txt
```

### "No module named 'tensorflow'"
```
Cause: TensorFlow not installed
Fix: pip install tensorflow
     (This can take 5-10 minutes)
```

### "CUDA error" or GPU errors
```
Cause: GPU/TensorFlow issues
Fix: Use CPU only by setting environment variable
     set CUDA_VISIBLE_DEVICES=-1
     python server.py
```

---

## 🎯 Most Common Solutions

**99% of fetch errors are fixed by:**

```powershell
# Terminal 1: Install dependencies
pip install -r requirements.txt

# Terminal 2: Start server (wait for startup message!)
python server.py

# Then: Refresh drawing_app.html in browser (Ctrl+F5)
# And: Try submitting drawing again
```

---

## ✨ Success Indicators

You'll know it's working when:

1. ✅ Server terminal shows model loading messages
2. ✅ Server terminal shows "Starting Flask API Server on http://localhost:5000"
3. ✅ Browser console (F12) shows network request to `/api/predict`
4. ✅ You see the prediction modal appear after 2-5 seconds
5. ✅ Modal shows prediction name (CAT, DOG, etc.) and confidence percentage

---

**Still having issues? Check the server terminal output - it will tell you what's wrong!** 🔍

Remember: The server MUST be running for the drawing app to work. Keep both windows open side-by-side if possible.

Good luck! 🎨
