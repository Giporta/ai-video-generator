import streamlit as st
import os
import subprocess
import json
import datetime

st.set_page_config(page_title="AI Video Generator", page_icon="🎬", layout="centered")

# API Keys
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
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "username": username, "title": title, "status": status, "cost": 0.19}
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
        return "Error"

st.title("🎬 AI Video Generator")
st.markdown("Generate professional videos from a story title!")

username = st.text_input("👤 Your Name", placeholder="Mario")
title = st.text_area("📝 Story Title", placeholder="My Amazing Story", height=100)
voice = st.selectbox("🎙️ Voice", list(VOICES.keys()))

if st.button("🚀 Generate Video", type="primary"):
    if not username or not title:
        st.error("❌ Please enter name and title!")
    else:
        with st.spinner("Generating video... This will take 15-20 minutes..."):
            try:
                os.environ['DEEPSEEK_KEY'] = DEEPSEEK_KEY
                os.environ['ANTHROPIC_KEY'] = ANTHROPIC_KEY
                os.environ['FIREWORKS_KEY'] = FIREWORKS_KEY
                os.environ['GROQ_KEY'] = GROQ_KEY
                
                voice_id = VOICES[voice]
                
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
                
                result = subprocess.run(["python3", "run.py"], capture_output=True, text=True, timeout=1800)
                
                if result.returncode == 0 and os.path.exists("final_video.mp4"):
                    log_generation(username, title, "SUCCESS")
                    st.success(f"✅ Video ready!\n\nTitle: {title}\nUser: {username}")
                    
                    with open("final_video.mp4", "rb") as f:
                        st.download_button("📥 Download Video", f, file_name=f"{title[:30]}.mp4", mime="video/mp4")
                    
                    st.video("final_video.mp4")
                else:
                    log_generation(username, title, "FAILED")
                    error = result.stderr[-300:] if result.stderr else "Unknown"
                    st.error(f"❌ Error:\n{error}")
            
            except subprocess.TimeoutExpired:
                log_generation(username, title, "TIMEOUT")
                st.error("❌ Timeout (>30 min)")
            except Exception as e:
                log_generation(username, title, "ERROR")
                st.error(f"❌ Error: {str(e)}")

with st.expander("📊 Statistics (Admin)"):
    if st.button("Refresh Stats"):
        st.text(get_stats())

st.markdown("---")
st.markdown("**Time:** ~15-20 min | **Cost:** ~$0.19 per video")
