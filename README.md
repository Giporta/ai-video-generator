# 🎬 AI Video Generator - Render Deployment

## 📋 Files in this repo:

1. **app.py** - Main Gradio application
2. **video_generator.py** - Video generation script
3. **requirements.txt** - Python dependencies
4. **render.yaml** - Render configuration

## 🚀 Deploy to Render:

### Step 1: Create GitHub Repo

1. Go to https://github.com/new
2. Repository name: `ai-video-generator`
3. Public
4. Create repository

### Step 2: Upload Files

1. Click "uploading an existing file"
2. Drag all 4 files from this folder
3. Commit

### Step 3: Deploy on Render

1. Go to https://render.com/dashboard
2. Click "New Web Service"
3. Connect GitHub account
4. Select `ai-video-generator` repo
5. Click "Connect"

### Step 4: Configure

Render will auto-detect settings from `render.yaml`, but verify:

- **Name:** ai-video-generator
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`
- **Plan:** Starter ($7/month) ← IMPORTANT!

### Step 5: Add Environment Variables

In Render dashboard, add these secrets:

```
DEEPSEEK_KEY = sk-1b7b3c9829c841d6b429b05334e0462c
ANTHROPIC_KEY = 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
FIREWORKS_KEY = fw_3Ze6uLjzsHjNy39HRYAREyYp
GROQ_KEY = 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
```

### Step 6: Deploy!

1. Click "Create Web Service"
2. Wait 5-10 minutes for build
3. Get your public URL: `https://ai-video-generator-xxxx.onrender.com`

## 💰 Costs:

- Render Starter: **$7/month**
- API costs per video: **~$0.19**

Total: $7 + (number_of_videos × $0.19)

## 📊 Usage:

Share your Render URL with friends/clients!

They can:
1. Enter their name
2. Enter story title
3. Select voice
4. Generate video (15-20 min)
5. Download result

## 🔧 Troubleshooting:

If deployment fails, check:
- All 4 files uploaded to GitHub
- Environment variables added correctly
- Selected "Starter" plan ($7/month) not Free tier
