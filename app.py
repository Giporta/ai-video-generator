import gradio as gr
import os
import subprocess
import json
import datetime

# API Keys from environment
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY", "")
FIREWORKS_KEY = os.getenv("FIREWORKS_KEY", "")
GROQ_KEY = os.getenv("GROQ_KEY", "")

VOICES = {
    "Jenny - Female (US)": "en-US-JennyNeural",
    "Guy - Male (US)": "en-US-GuyNeural",
    "Aria - Female (US)": "en-US-AriaNeural",
    "Ryan - Male (UK)": "en-GB-RyanNeural",
    "Sonia - Female (UK)": "en-GB-SoniaNeural",
}

def log_generation(username, title, status):
    """Log video generation"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "username": username,
            "title": title,
            "status": status,
            "cost": 0.19
        }
        
        stats = []
        if os.path.exists("stats.json"):
            with open("stats.json") as f:
                stats = json.load(f)
        
        stats.append(entry)
        
        with open("stats.json", "w") as f:
            json.dump(stats, f, indent=2)
    except:
        pass

def get_stats():
    """Get usage statistics"""
    try:
        if not os.path.exists("stats.json"):
            return "No stats yet"
        
        with open("stats.json") as f:
            stats = json.load(f)
        
        users = {}
        for s in stats:
            u = s.get("username", "Unknown")
            users[u] = users.get(u, 0) + 1
        
        result = f"Total videos: {len(stats)}\n\n"
        for user, count in users.items():
            result += f"{user}: {count} videos\n"
        
        return result
    except:
        return "Error reading stats"

def generate_video(username, title, voice_name):
    """Generate video"""
    
    if not username or not title:
        return None, "❌ Please enter name and title!"
    
    try:
        # Set environment
        os.environ['DEEPSEEK_KEY'] = DEEPSEEK_KEY
        os.environ['ANTHROPIC_KEY'] = ANTHROPIC_KEY
        os.environ['FIREWORKS_KEY'] = FIREWORKS_KEY
        os.environ['GROQ_KEY'] = GROQ_KEY
        
        voice_id = VOICES[voice_name]
        
        # Create run script
        script = f'''
import os
STORY_TITLE = """{title}"""
VOICE_ID = "{voice_id}"
TOTAL_DURATION_SEC = 600
ENABLE_SUBTITLES = True

with open("video_generator.py") as f:
    exec(f.read())
'''
        
        with open("run.py", "w") as f:
            f.write(script)
        
        # Run
        result = subprocess.run(
            ["python3", "run.py"],
            capture_output=True,
            text=True,
            timeout=1800
        )
        
        if result.returncode == 0 and os.path.exists("final_video.mp4"):
            log_generation(username, title, "SUCCESS")
            return "final_video.mp4", f"✅ Video ready!\n\nTitle: {title}\nUser: {username}"
        else:
            log_generation(username, title, "FAILED")
            error = result.stderr[-300:] if result.stderr else "Unknown error"
            return None, f"❌ Error:\n{error}"
    
    except subprocess.TimeoutExpired:
        log_generation(username, title, "TIMEOUT")
        return None, "❌ Timeout (>30 min)"
    except Exception as e:
        log_generation(username, title, "ERROR")
        return None, f"❌ Error: {str(e)}"

# Create interface
with gr.Blocks(title="AI Video Generator") as app:
    gr.Markdown("# 🎬 AI Video Generator")
    gr.Markdown("Generate professional videos from a story title!")
    
    with gr.Row():
        username = gr.Textbox(label="👤 Your Name", placeholder="Mario")
        
    with gr.Row():
        title = gr.Textbox(label="📝 Story Title", placeholder="My Amazing Story", lines=2)
    
    with gr.Row():
        voice = gr.Dropdown(
            label="🎙️ Voice",
            choices=list(VOICES.keys()),
            value="Guy - Male (US)"
        )
    
    generate_btn = gr.Button("🚀 Generate Video", variant="primary")
    
    status = gr.Textbox(label="Status", lines=3)
    video = gr.Video(label="Video")
    
    with gr.Accordion("📊 Stats (Admin)", open=False):
        stats_box = gr.Textbox(label="Statistics", lines=8)
        refresh_btn = gr.Button("Refresh Stats")
        refresh_btn.click(get_stats, outputs=stats_box)
    
    generate_btn.click(
        generate_video,
        inputs=[username, title, voice],
        outputs=[video, status]
    )
    
    gr.Markdown("---")
    gr.Markdown("**Time:** ~15-20 min | **Cost:** ~$0.19 per video")

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860))
    )
