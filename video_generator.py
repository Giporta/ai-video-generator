# ═══════════════════════════════════════════════════════════════
# 🎬 AI STORY VIDEO GENERATOR - FIREWORKS EDITION (ZOOM ONLY)
# ═══════════════════════════════════════════════════════════════
# 
# STACK:
# ✅ Script: DeepSeek V3 (Chat)
# ✅ Image Prompts: Claude Sonnet 4.5 (Title-matching)
# ✅ Image Generation: Fireworks AI (Flux-1-Schnell-FP8)
# ✅ Video Effect: PIL Zoom (smooth cinematic)
# ✅ Audio: Edge-TTS via HuggingFace
# ✅ Subtitles: Whisper + ASS format
# ✅ Costo: ~$0.19 per video
# 
# 🔮 FUTURE: RunPod Serverless per animazioni (primi 20-30 sec)
# ═══════════════════════════════════════════════════════════════
import subprocess
import sys
import os
import json
import requests
import time
import jwt
import subprocess as sp
import math
import shutil
import httpx
from openai import OpenAI
from groq import Groq
from anthropic import Anthropic
import numpy as np
import gc
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

print("✅ Import completati!\n")

# ═══════════════════════════════════════════════════════════════
# CONFIGURAZIONE
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("⚙️  CONFIGURAZIONE")
print("=" * 60)

# API Keys (from environment variables)
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY", "")
FIREWORKS_KEY = os.getenv("FIREWORKS_KEY", "")
GROQ_KEY = os.getenv("GROQ_KEY", "")

print("✅ API Keys caricate!")
print("🤖 Script: DeepSeek V3")
print("🎨 Prompts: Claude Sonnet 4.5")
print("🖼️  Images: Fireworks AI (Flux-1-Schnell)")
print("🎬 Video: PIL Zoom Effect (smooth)")
print("💰 Costo: ~$0.19 per video")
print("🔮 Future: RunPod animation integration\n")

# Story title and voice will be set by the Gradio wrapper
# STORY_TITLE = "..." (set by wrapper)
# VOICE_ID = "..." (set by wrapper)
# TOTAL_DURATION_SEC = 600 (set by wrapper)
# ENABLE_SUBTITLES = True (set by wrapper)

if 'STORY_TITLE' not in globals():
    STORY_TITLE = "Test Story"
if 'VOICE_ID' not in globals():
    VOICE_ID = "en-US-GuyNeural"
if 'TOTAL_DURATION_SEC' not in globals():
    TOTAL_DURATION_SEC = 600
if 'ENABLE_SUBTITLES' not in globals():
    ENABLE_SUBTITLES = True

print(f"📝 Titolo: {STORY_TITLE}")
print(f"🎙️  Voce: {VOICE_ID}")
print(f"⏱️  Durata: {TOTAL_DURATION_SEC}s")

# Configuration is set by wrapper, skip interactive prompts
# Calculate derived values
NUM_IMAGES = 4
TOTAL_DURATION_MIN = TOTAL_DURATION_SEC // 60
IMAGE_DURATION = 30  # Default 30 seconds per image
zoom_percent = min(15.0, (IMAGE_DURATION / 40.0) * 15.0)
ZOOM_MAX = 1.0 + (zoom_percent / 100.0)

CHARS_PER_MINUTE = 850
TOTAL_CHARS = int(TOTAL_DURATION_MIN * CHARS_PER_MINUTE * 1.1)
TOTAL_WORDS = int(TOTAL_CHARS / 5)
WORDS_PER_CHAPTER = int(TOTAL_WORDS / NUM_IMAGES)

VOICE_SPEED = 1.0  # Normal speed

# Rendering settings
print("✅ Rendering: 24 FPS, preset faster")
SUPERSAMPLING = 1
MOTION_BLUR_SAMPLES = 1


FPS = 24  # 24 fps (standard cinema)


print("\n" + "=" * 60)
print("📊 RIEPILOGO CONFIGURAZIONE")
print("=" * 60)
print(f"📏 Durata: {TOTAL_DURATION_MIN} minuti")
print(f"🖼️  Immagini: {NUM_IMAGES}")
print(f"⏱️  Durata immagine: {IMAGE_DURATION} sec")
print(f"🔍 Zoom: {zoom_percent:.1f}%")
print(f"📝 Parole per capitolo: ~{WORDS_PER_CHAPTER}")
print(f"💬 Sottotitoli: {'Attivi' if ENABLE_SUBTITLES else 'Disattivati'}")
print(f"🎤 Velocità: {VOICE_SPEED}x")
print(f"🤖 AI: DeepSeek V3 + Competitor Prompts")
print(f"💰 Costo: ~$0.20 (vs $0.33 GPT-4o)")
print("=" * 60)

# Auto-confirm when running from wrapper
print(f"\n✅ Config OK!\n")

# ═══════════════════════════════════════════════════════════════
# GENERA SCRIPT CON DEEPSEEK V3 (COMPETITOR-STYLE PROMPTS)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("📝 GENERAZIONE SCRIPT (DeepSeek V3)")
print("=" * 60)

# DeepSeek client with explicit httpx client to bypass proxy issues
http_client = httpx.Client(
    timeout=60.0,
    transport=httpx.HTTPTransport(retries=3)
)

client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com",
    http_client=http_client
)

# OUTLINE PROMPT (Competitor-analyzed)
outline_prompt = f"""Create a detailed plot outline for a {NUM_IMAGES}-chapter story based on this title: "{STORY_TITLE}"

STEP 1 - ANALYZE THE TITLE & AUTO-DETECT STORY TYPE:

Based on "{STORY_TITLE}", identify story TYPE:

**HOA/LEGAL/PROPERTY** (keywords: demolished, built on my land, evicted, HOA, lawsuit, sue)
→ Style: David vs Goliath, dramatic confrontations, courtroom reveals, property battles
→ Opening: Physical destruction or discovery of violation
→ Peak Drama: Demolition scenes, document reveals, power reversals

**MYSTERY/HORROR** (keywords: vanished, disappeared, discovered, hidden, secret, found)
→ Style: Slow-burn mystery, shocking reveals, dark secrets
→ Opening: Memorial or search scene
→ Peak Drama: Discovery moment, truth revealed, rescue

**ROMANCE/WESTERN** (keywords: bride, cowboy, Apache, cabin, sold, widow, territory)
→ Style: Emotional journey, survival, forbidden love, honor
→ Opening: Meet-cute or dramatic situation
→ Peak Drama: Declaration, sacrifice, overcoming prejudice

**FEEL-GOOD/JUSTICE** (keywords: waitress, kindness, inherits, discovers, secret, millionaire)
→ Style: Underdog triumph, hidden tests, life-changing reveals
→ Opening: Daily routine showing character
→ Peak Drama: Big reveal, confrontation, transformation

STEP 2 - STORY REQUIREMENTS:

CRITICAL FOR VISUAL VIDEO CONTENT:
- Every chapter MUST contain ONE dramatic, visually powerful scene (YouTube thumbnail moment)
- Chapter 1: SHORT hook that stops scroll (HALF the words of other chapters)
- Chapters 2-4: MAIN dramatic action matching the title (these generate the 4 images!)
- Focus 60% on VISUAL MOMENTS with physical action and visible emotions
- Each chapter needs ONE "freeze-frame thumbnail moment"

VISUAL SCENE TYPES by Story Type:

FOR HOA/LEGAL:
- Demolition/destruction (bulldozers, wrecking balls, debris)
- Confrontations (pointing, blocking machinery, standing defiant)
- Document reveals (holding up deeds, courtroom drama)

FOR MYSTERY:
- Discovery moments (finding evidence, shocking reveals)
- Search scenes (investigating, uncovering secrets)
- Emotional breakdowns (tears, collapse, screaming)

FOR ROMANCE:
- Meeting scene (first encounter, dramatic situation)
- Conflict moment (separation, obstacle, tension)
- Resolution (declaration, embrace, union)

FOR FEEL-GOOD:
- Daily life establishing character
- Hidden test/kindness moment
- Big reveal/transformation scene

REQUIREMENTS:
- {NUM_IMAGES} chapters total
- Chapter 1: ~{int(WORDS_PER_CHAPTER * 0.7)} words (HOOK - shorter!)
- Chapters 2-{NUM_IMAGES}: ~{WORDS_PER_CHAPTER} words each
- Specific visual details: lighting, weather, clothing COLORS, facial expressions, props
- Each chapter ends with visual hook for next scene

OUTPUT FORMAT:
Chapter 1: [Attention-Grabbing Hook Title]
Brief summary focusing on the HOOK and promise of story (shorter chapter!)

Chapter 2: [Dramatic Visual Title]
Brief summary focusing on KEY VISUAL MOMENT in this chapter

Chapter 3: [Dramatic Visual Title]
Brief summary focusing on KEY VISUAL MOMENT in this chapter

Chapter 4: [Dramatic Visual Title]
Brief summary focusing on KEY VISUAL MOMENT in this chapter

Remember: Think "What would make someone STOP SCROLLING?" for each chapter."""

print("⏳ Creazione outline con DeepSeek V3...")
print("💡 DeepSeek sta analizzando il titolo (competitor-style)...\n")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are an expert at creating visually dramatic stories optimized for viral YouTube video content based on competitor analysis. You understand that every chapter must contain a powerful visual moment that could serve as a compelling thumbnail image."},
        {"role": "user", "content": outline_prompt}
    ],
    temperature=0.8,
    max_tokens=4000
)
outline = response.choices[0].message.content
print("✅ Outline creato!\n")

# GENERAZIONE CAPITOLI con prompt COMPETITOR-STYLE
full_script = ""
for chapter in range(1, NUM_IMAGES + 1):
    
    # Chapter 1 è più corto (HOOK)
    if chapter == 1:
        target_words = int(WORDS_PER_CHAPTER * 0.7)
        chapter_style = """CHAPTER 1: THE HOOK (Stop the scroll!)

This is THE MOST IMPORTANT chapter - viewers decide in 30 seconds.

STRUCTURE:
1. Opening Line: Dramatic statement or shocking question
2. Setup: 2-3 sentences heightening drama
3. Promise: What's coming in the story
4. Hook: Make them NEED Chapter 2

STYLE:
✅ SHORT sentences (10-15 words average)
✅ Active voice ONLY
✅ Present-tense feel
✅ Punchy, conversational tone
✅ NO backstory yet - pure hook!
✅ ONE clear visual image

EXAMPLE (HOA style):
"They built 96 houses on my land. Not by accident. On purpose. I inherited 47 acres from my grandfather. Went to visit and found an entire subdivision. The HOA president told me I was a deadbeat squatter. Here's what I did. Absolutely nothing. Let them finish construction. Then I walked into federal court with the original 1971 deed."

Write Chapter 1 in THIS exact punchy style."""
    
    else:
        target_words = WORDS_PER_CHAPTER
        chapter_style = f"""CHAPTER {chapter}: VISUAL DRAMATIC ACTION

This chapter MUST contain ONE major dramatic visual moment - a "freeze-frame" perfect for YouTube thumbnail.

CRITICAL VISUAL REQUIREMENTS:
1. ONE clear dramatic scene perfect for a single image
2. Specific physical actions (running, collapsing, pointing, destroying, discovering)
3. Strong visible emotions:
   - Tears streaming down face
   - Jaw dropped in shock
   - Eyes blazing with fury
   - Determined clenched jaw
   
4. Detailed visual descriptions:
   - Clothing: colors, condition (torn blue shirt, pristine black suit, dusty work clothes)
   - Facial expressions: (wide eyes, tears on cheeks, furrowed brow, trembling lip)
   - Body language: (pointing accusingly, collapsed on knees, arms crossed defensively)
   - Lighting: (golden sunset, harsh noon sun, soft morning light, dramatic shadows)
   - Props: Be SPECIFIC - "yellow CAT excavator" not "equipment", "crumpled legal deed" not "document"

5. What would a CAMERA SEE:
   - Describe visual action, not internal thoughts
   - "The wrecking ball SLAMS into the chimney" not "demolition happened"
   - "Tears stream down her face as she clutches the photo" not "she was sad"

WRITING STYLE:
- Short, punchy paragraphs (2-4 sentences max)
- Include dialogue that creates visual drama (shouting, accusations, reveals)
- Focus 60% of chapter on the KEY VISUAL MOMENT
- End with visual hook for next chapter

AVOID:
- Long internal monologues
- Static scenes (just sitting/thinking)
- Vague descriptions ("looked upset" → "tears streamed, jaw trembling")

Think: "If I could show only ONE IMAGE from this chapter for the thumbnail, what would make viewers desperate to click?"

Write Chapter {chapter} with ONE powerful, visually dramatic scene."""

    chapter_prompt = f"""Write Chapter {chapter} of {NUM_IMAGES} for the story "{STORY_TITLE}"

OUTLINE REFERENCE:
{outline}

TARGET: EXACTLY {target_words} WORDS

{chapter_style}

UNIVERSAL REQUIREMENTS:
- Start with "## Chapter {chapter}: [Title]"
- EXACTLY {target_words} words
- Include specific sensory details
- Natural dialogue with action beats
- End with hook/cliffhanger (unless final chapter)

Write Chapter {chapter} now."""

    print(f"⏳ Scrivendo Capitolo {chapter}/{NUM_IMAGES} (DeepSeek V3 - {target_words} parole)...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are an expert visual storyteller creating content for viral YouTube videos using competitor-analyzed techniques. Every scene you write must be cinematically vivid and emotionally powerful."},
            {"role": "user", "content": chapter_prompt}
        ],
        temperature=0.8,
        max_tokens=2500
    )
    chapter_text = response.choices[0].message.content
    full_script += chapter_text + "\n\n"
    print(f"   ✅ Capitolo {chapter} completato!\n")

print("✅ Script completo generato!\n")

with open("script.txt", "w", encoding="utf-8") as f:
    f.write(full_script)

# ═══════════════════════════════════════════════════════════════
# GENERA VOICEOVER CON EDGE-TTS (ORIGINALE FUNZIONANTE!)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🎤 GENERAZIONE VOICEOVER (Edge-TTS)")
print("=" * 60)

max_retries = 3
tts_success = False

print(f"🎙️  Voce: {VOICE_ID}")
print(f"📝 Testo: {len(full_script)} caratteri\n")

for attempt in range(max_retries):
    try:
        print(f"   🎙️  Tentativo {attempt + 1}/{max_retries}...")
        print("   🔌 Connessione a HuggingFace...")
        
        client_tts = Client("Gippoo/Edge-TTS-Text-to-Speech")
        
        print("   ⚙️  Generazione audio...")
        result = client_tts.predict(
            text=full_script,
            voice=VOICE_ID,
            rate=0,
            pitch=0,
            api_name="/tts_interface"
        )
        
        if result and len(result) > 0:
            audio_filepath = result[0]
            print(f"   ✅ Audio generato!")
            
            if audio_filepath.startswith("http"):
                print("   ⏳ Download...")
                mp3_response = requests.get(audio_filepath, timeout=60)
                if mp3_response.status_code == 200:
                    with open("voiceover.mp3", "wb") as f:
                        f.write(mp3_response.content)
                    print("   ✅ Salvato!\n")
                    tts_success = True
                    break
            else:
                print("   📋 Copia file...")
                shutil.copy(audio_filepath, "voiceover.mp3")
                print("   ✅ Salvato!\n")
                tts_success = True
                break
        
        if not tts_success and attempt < max_retries - 1:
            wait_time = (attempt + 1) * 20
            print(f"   ⏳ Attendo {wait_time}s...")
            time.sleep(wait_time)
            
    except Exception as e:
        print(f"   ⚠️  Errore: {str(e)[:150]}")
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 20
            print(f"   ⏳ Attendo {wait_time}s...")
            time.sleep(wait_time)

if not tts_success:
    print("\n❌ ERRORE: Edge-TTS non disponibile")
    exit(1)

audio_filename = "voiceover.mp3"

# ═══════════════════════════════════════════════════════════════
# TRASCRIZIONE CON WHISPER (ORIGINALE FUNZIONANTE!)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("📝 TRASCRIZIONE CON WHISPER")
print("=" * 60)

groq_client = Groq(api_key=GROQ_KEY)

audio_size_mb = os.path.getsize(audio_filename) / (1024 * 1024)
print(f"📊 Dimensione audio: {audio_size_mb:.1f} MB")

if audio_size_mb > 24:
    print("⚠️  File > 24MB, splitting necessario...")
    print("⏳ Split audio...")
    
    audio_duration_cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_filename
    ]
    duration_output = sp.run(audio_duration_cmd, capture_output=True, text=True)
    total_duration = float(duration_output.stdout.strip())
    
    chunk_duration = 300
    num_chunks = math.ceil(total_duration / chunk_duration)
    
    word_timestamps = []
    
    for i in range(num_chunks):
        start_time = i * chunk_duration
        chunk_file = f"audio_chunk_{i}.mp3"
        
        print(f"   Chunk {i+1}/{num_chunks}...")
        
        split_cmd = [
            'ffmpeg', '-y', '-i', audio_filename,
            '-ss', str(start_time),
            '-t', str(chunk_duration),
            '-c', 'copy',
            chunk_file
        ]
        sp.run(split_cmd, capture_output=True)
        
        with open(chunk_file, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=(chunk_file, audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )
        
        for word_data in transcription.words:
            word_timestamps.append({
                'word': word_data['word'],
                'start': word_data['start'] + start_time,
                'end': word_data['end'] + start_time
            })
        
        os.remove(chunk_file)
    
else:
    print("⏳ Trascrizione diretta...")
    with open(audio_filename, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
            file=(audio_filename, audio_file.read()),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            timestamp_granularities=["word"]
        )
    
    word_timestamps = []
    for word_data in transcription.words:
        word_timestamps.append({
            'word': word_data['word'],
            'start': word_data['start'],
            'end': word_data['end']
        })

print(f"✅ {len(word_timestamps)} parole trascritte!\n")

# ═══════════════════════════════════════════════════════════════
# SOTTOTITOLI ASS (ORIGINALE FUNZIONANTE!)
# ═══════════════════════════════════════════════════════════════
subtitle_file = None

if ENABLE_SUBTITLES:
    print("=" * 60)
    print("📝 CREAZIONE SOTTOTITOLI")
    print("=" * 60)

    def format_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int((seconds % 1) * 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    ass_header = """[Script Info]
Title: Subtitles
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,2,2,10,10,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_content = ass_header
    
    for i, word_info in enumerate(word_timestamps):
        word = word_info['word']
        start = word_info['start']
        end = word_info['end']
        
        words_before = ' '.join([w['word'] for w in word_timestamps[max(0, i-3):i]])
        words_after = ' '.join([w['word'] for w in word_timestamps[i+1:min(len(word_timestamps), i+4)]])
        
        subtitle_text = f"{words_before} {{\\c&H00FFFF&}}{word}{{\\c&HFFFFFF&}} {words_after}".strip()
        
        ass_content += f"Dialogue: 0,{format_ass_time(start)},{format_ass_time(end)},Default,,0,0,0,,{subtitle_text}\n"
    
    subtitle_file = "subtitles.ass"
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"✅ Sottotitoli creati: {subtitle_file}\n")

# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# GENERA IMAGE PROMPTS CON CLAUDE SONNET 4.5 (TITLE + SCRIPT MATCHING!)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🎨 GENERAZIONE PROMPTS IMMAGINI (Claude Sonnet 4.5 - TITLE MATCHING)")
print("=" * 60)

# Anthropic client
anthropic_client = Anthropic(api_key=ANTHROPIC_KEY)

print(f"📖 Analizzando titolo e script completo...")
print(f"🎯 Titolo: {STORY_TITLE}\n")

# NUOVO PROMPT: TITLE + SCRIPT MATCHING 🔥
narrative_prompt = f"""You are an expert at creating image prompts for YouTube story videos.

TITLE: "{STORY_TITLE}"

STEP 1: IDENTIFY THE MAIN VISUAL PROMISE FROM THE TITLE
What is the ONE KEY ACTION the title promises viewers will see?

Examples:
- "Demolished My Mansion" → Mansion being demolished
- "Built on My Land" → Construction on land  
- "Evicted from Home" → Eviction happening

STEP 2: READ THE SCRIPT FOR DETAILS
SCRIPT:
{full_script}

Extract from script:
- Character descriptions (age, clothing, emotions)
- Specific details (colors, objects, setting)
- Key dramatic moments
- Emotional context

STEP 3: COMBINE TITLE + SCRIPT

Create 4 VARIATIONS of the TITLE'S MAIN SCENE, using SCRIPT DETAILS:

CRITICAL RULES:
✅ All 4 prompts show the MAIN ACTION from title (not minor objects)
✅ Use character details from script (clothing, age, emotions)
✅ Use setting details from script (lake, driveway, time of day)
✅ Use emotional context from script (shock, anger, defiance)
✅ Vary camera angles and focus points

❌ DO NOT show minor objects if title mentions main building
   (If title says "demolished mansion", don't show fountain instead)

REQUIREMENTS:
- Include people with emotions when possible
- Specific details (colors, clothing, objects)
- Different camera angles for variety
- Photorealistic, cinematic
- 40-60 words each

CREATE 4 VARIATIONS:

1. [Wide/aerial angle of TITLE'S MAIN ACTION + script details]
2. [Close-up of TITLE'S MAIN ACTION + script details]  
3. [Human reaction to TITLE'S MAIN ACTION + script character details]
4. [Different angle of TITLE'S MAIN ACTION + script setting details]

EXAMPLE:

Title: "HOA Demolished My Lake Mansion"
Script details: "man in navy polo, yellow bulldozer with HOA logo, cobblestone driveway, lakefront, bright sunlight, fists clenched"

CORRECT PROMPTS (title's main action + script details):

1. Aerial view of yellow bulldozer with HOA logo demolishing lakefront mansion, walls crumbling, debris flying, cobblestone driveway visible, bright sunlight, photorealistic

2. Close-up of bulldozer claw tearing through mansion's wall, bricks and dust exploding outward, dramatic lighting, photorealistic

3. Middle-aged man in navy polo standing in driveway, fists clenched, watching his lakefront mansion being demolished behind him, face showing controlled rage, photorealistic

4. Side angle showing mansion half-collapsed with yellow bulldozer actively demolishing it, lake in background, photorealistic

WRONG PROMPTS:
❌ "Bulldozer destroying fountain with mansion intact"
❌ "Man watching fountain demolished"

The title promises MANSION demolished → Show MANSION demolished
Use script for: character details, colors, emotions, setting
Use title for: what main action to show

FORMAT YOUR RESPONSE:
Just return 4 numbered prompts (1-4), one per line.
Each prompt 40-60 words.
Focus on TITLE'S MAIN ACTION with SCRIPT DETAILS."""

print("⏳ Generating title-matching prompts...")
prompts_response = anthropic_client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=2000,
    temperature=0.7,
    messages=[{"role": "user", "content": narrative_prompt}]
)

prompts_text = prompts_response.content[0].text

# Parse prompts
import re
lines = prompts_text.strip().split('\n')
image_prompts = []

for line in lines:
    cleaned = re.sub(r'^\d+[\.\):\-]\s*|^IMAGE\s+\d+:\s*|^PROMPT\s+\d+:\s*', '', line.strip(), flags=re.IGNORECASE)
    if cleaned and len(cleaned) > 40:
        image_prompts.append(cleaned)

# Assicura 4 prompts
if len(image_prompts) > NUM_IMAGES:
    image_prompts = image_prompts[:NUM_IMAGES]
elif len(image_prompts) < NUM_IMAGES:
    while len(image_prompts) < NUM_IMAGES:
        image_prompts.append(image_prompts[-1] if image_prompts else "Photorealistic scene matching title")

print(f"✅ {len(image_prompts)} title-matching prompts ready!\n")

print("📋 Generated prompts (matching title's promise):")
for i, prompt in enumerate(image_prompts, 1):
    print(f"   {i}. {prompt[:100]}..." if len(prompt) > 100 else f"   {i}. {prompt}")
print()

with open("image_prompts.txt", "w", encoding="utf-8") as f:
    f.write(f"TITLE: {STORY_TITLE}\n\n")
    f.write("=" * 80 + "\n")
    f.write("TITLE-MATCHING PROMPTS (4 variations of main scene):\n")
    f.write("=" * 80 + "\n\n")
    for i, prompt in enumerate(image_prompts, 1):
        f.write(f"{i}. {prompt}\n\n")

print("💾 Title-matching prompts saved!\n")



# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# GENERA IMMAGINI CON FIREWORKS AI (FLUX-1-SCHNELL-FP8)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🖼️  GENERAZIONE IMMAGINI (Fireworks AI - Flux)")
print("=" * 60)

image_files = []

for i, prompt in enumerate(image_prompts, 1):
    print(f"\n⏳ Immagine {i}/{NUM_IMAGES}...")
    
    # Clean prompt
    clean_prompt = prompt.replace("**", "").strip()
    print(f"   Prompt: {clean_prompt[:80]}...")
    
    # Fireworks API request
    url = "https://api.fireworks.ai/inference/v1/workflows/accounts/fireworks/models/flux-1-schnell-fp8/text_to_image"
    headers = {
        "Content-Type": "application/json",
        "Accept": "image/jpeg",
        "Authorization": f"Bearer {FIREWORKS_KEY}",
    }
    data = {
        "prompt": clean_prompt,
        "aspect_ratio": "16:9",
        "guidance_scale": 3.5,
        "num_inference_steps": 4,
        "seed": -1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            filename = f"img_{i}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            image_files.append(filename)
            print(f"✅ Saved: {filename}")
        else:
            print(f"❌ Fireworks error ({response.status_code}): {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print(f"\n✅ {len(image_files)}/{NUM_IMAGES} immagini generate!\n")

if len(image_files) == 0:
    print("=" * 60)
    print("❌ FIREWORKS AI - NESSUNA IMMAGINE GENERATA")
    print("=" * 60)
    print("Verifica:")
    print("1. API Key valida")
    print("2. Crediti disponibili su Fireworks")
    print("3. Connessione internet")
    print("=" * 60)
    exit(1)

# ═══════════════════════════════════════════════════════════════
# RENDERING ZOOM CLIPS (TUTTE LE IMMAGINI)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🎬 RENDERING ZOOM CLIPS")
print("=" * 60)

# Per ora usiamo solo zoom per tutto il video
# In futuro integreremo RunPod per animazioni nei primi 20-30 sec
animated_video_files = []  # Empty per ora


# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🎬 RENDERING ZOOM CLIPS")
print("=" * 60)

def generate_zoom_frames(img_path, output_folder, duration_sec, fps, zoom_max, supersampling, motion_blur_samples):
    print(f"⏳ {img_path}...")
    img = Image.open(img_path).convert('RGB')
    
    target_w, target_h = 1280, 720
    render_w = target_w * supersampling
    render_h = target_h * supersampling
    
    min_size_w = int(render_w * zoom_max * 1.1)
    min_size_h = int(render_h * zoom_max * 1.1)
    
    aspect = img.width / img.height
    if aspect > 16/9:
        scale_h = min_size_h
        scale_w = int(scale_h * aspect)
    else:
        scale_w = min_size_w
        scale_h = int(scale_w / aspect)
    
    img = img.resize((scale_w, scale_h), Image.Resampling.LANCZOS)
    img_width, img_height = img.size
    
    total_frames = int(duration_sec * fps)
    if total_frames <= 1:
        total_frames = 2
    
    os.makedirs(output_folder, exist_ok=True)
    
    center_x = img_width / 2.0
    center_y = img_height / 2.0
    
    for frame_num in range(total_frames):
        progress = frame_num / (total_frames - 1)
        ease = 0.5 - 0.5 * math.cos(math.pi * progress)
        zoom = 1.0 + (zoom_max - 1.0) * ease
        
        accumulator = None
        
        for sub in range(motion_blur_samples):
            sub_progress = (frame_num + sub / motion_blur_samples) / (total_frames - 1)
            sub_ease = 0.5 - 0.5 * math.cos(math.pi * sub_progress)
            sub_zoom = 1.0 + (zoom_max - 1.0) * sub_ease
            
            window_w = render_w / sub_zoom
            window_h = render_h / sub_zoom
            
            offset_x = center_x - window_w / 2.0
            offset_y = center_y - window_h / 2.0
            
            scale_x = window_w / render_w
            scale_y = window_h / render_h
            
            affine_matrix = (scale_x, 0, offset_x, 0, scale_y, offset_y)
            
            subframe = img.transform(
                (render_w, render_h),
                Image.AFFINE,
                affine_matrix,
                resample=Image.Resampling.BICUBIC
            )
            
            subframe_array = np.array(subframe, dtype=np.float32)
            if accumulator is None:
                accumulator = subframe_array
            else:
                accumulator += subframe_array
        
        if motion_blur_samples > 1:
            blurred = (accumulator / motion_blur_samples).astype(np.uint8)
        else:
            blurred = accumulator.astype(np.uint8)
        
        frame_img = Image.fromarray(blurred)
        
        if supersampling > 1:
            frame_img = frame_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        frame_path = os.path.join(output_folder, f"frame_{frame_num:04d}.png")
        frame_img.save(frame_path, compress_level=1)
        
        if frame_num % 25 == 0:
            print(f"  Frame {frame_num}/{total_frames}")
    
    gc.collect()
    return output_folder

def process_image(img_index, img_file):
    folder = f"frames_clip_{img_index}"
    generate_zoom_frames(img_file, folder, IMAGE_DURATION, FPS, ZOOM_MAX, SUPERSAMPLING, MOTION_BLUR_SAMPLES)
    return (img_index, folder)

print("🚀 Rendering zoom clips parallelo...\n")

print("🚀 Rendering zoom clips per TUTTE le immagini...\n")
print(f"📊 Genererò zoom clips per tutte le {len(image_files)} immagini")
print(f"   (verranno usate per tutto il video con loop)\n")

# Genera zoom clips per TUTTE le immagini
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(process_image, i, img_file): i 
        for i, img_file in enumerate(image_files, 1)
    }
    
    zoom_results = {}
    for future in as_completed(futures):
        img_index, folder = future.result()
        zoom_results[img_index] = folder
        print(f"✅ Zoom clip {img_index}/{len(image_files)}!")

video_folders_zoom = zoom_results
print(f"\n✅ {len(video_folders_zoom)} zoom clips renderizzati!\n")

# ═══════════════════════════════════════════════════════════════
# MONTAGGIO VIDEO (Animated + Zoom Clips)
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("🎬 MONTAGGIO VIDEO")
print("=" * 60)

def run_ffmpeg(cmd, description):
    print(f"⏳ {description}...")
    result = sp.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ERRORE: {result.stderr[-500:]}")
        raise Exception(f"FFmpeg failed: {description}")
    return result

# Step 1: Convert zoom frames to video clips
zoom_video_clips = []

for img_idx in sorted(video_folders_zoom.keys()):
    folder = video_folders_zoom[img_idx]
    output_clip = f"zoom_clip_{img_idx}.mp4"
    
    frames_cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-i', f'{folder}/frame_%04d.png',
        '-c:v', 'libx264',
        '-preset', 'faster',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        output_clip
    ]
    
    run_ffmpeg(frames_cmd, f"Zoom Clip {img_idx}")
    zoom_video_clips.append((img_idx, output_clip))

# Step 2: Combine all video clips in order
all_video_clips = []

print("\n📊 Struttura video:")
print(f"   Tutto zoom clips (smooth cinematic effect)\n")

# Since we have no animated videos, we use only zoom clips
# Calculate how many clips needed for total duration
zoom_clip_duration = IMAGE_DURATION
clips_needed = int(TOTAL_DURATION_SEC / zoom_clip_duration) + 1

print(f"📊 Durata totale: {TOTAL_DURATION_SEC}s")
print(f"📊 Durata per clip: {zoom_clip_duration}s")
print(f"📊 Zoom clips necessari: {clips_needed}\n")

# Build zoom clips list (con loop)
zoom_clips_ordered = [clip for idx, clip in sorted(zoom_video_clips)]

if len(zoom_clips_ordered) > 0:
    for i in range(clips_needed):
        clip_idx = i % len(zoom_clips_ordered)
        clip = zoom_clips_ordered[clip_idx]
        all_video_clips.append(clip)
        print(f"✅ Clip {i + 1}: {clip} (zoom, {zoom_clip_duration}s)")

# Safety check
if len(all_video_clips) == 0:
    print("\n❌ ERRORE: Nessun video clip generato!")
    exit(1)

# Trim to exact duration needed
clips_for_duration = []
current_time = 0
for clip in all_video_clips:
    if current_time >= TOTAL_DURATION_SEC:
        break
    clips_for_duration.append(clip)
    current_time += zoom_clip_duration

# Step 3: Concatenate all clips
with open('clips.txt', 'w') as f:
    for clip in clips_for_duration:
        f.write(f"file '{clip}'\n")

concat_cmd = [
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', 'clips.txt',
    '-c', 'copy',
    'concat.mp4'
]
run_ffmpeg(concat_cmd, "Concatenazione clips")

print(f"\n✅ {len(clips_for_duration)} clips concatenati!\n")

# Audio
audio_cmd = [
    'ffmpeg', '-y',
    '-i', 'concat.mp4',
    '-i', audio_filename,
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-b:a', '192k',
    'video_audio.mp4'
]
run_ffmpeg(audio_cmd, "Audio")

# Sottotitoli
if ENABLE_SUBTITLES and subtitle_file:
    sub_cmd = [
        'ffmpeg', '-y',
        '-i', 'video_audio.mp4',
        '-vf', f"ass={subtitle_file}",
        '-c:v', 'libx264',
        '-preset', 'faster',
        '-crf', '23',
        '-c:a', 'copy',
        'final_video.mp4'
    ]
    run_ffmpeg(sub_cmd, "Sottotitoli")
else:
    shutil.copy('video_audio.mp4', 'final_video.mp4')

# Cleanup
print("\n⏳ Pulizia...")
# Cleanup zoom frame folders
for img_idx, folder in video_folders_zoom.items():
    if os.path.exists(folder):
        shutil.rmtree(folder)

# Cleanup all video clips (animated + zoom)
for clip in all_video_clips:
    if os.path.exists(clip):
        os.remove(clip)

# Cleanup temp image files
for img_file in image_files:
    if os.path.exists(img_file):
        os.remove(img_file)

print("✅ Video completato!\n")

# ═══════════════════════════════════════════════════════════════
# COMPLETAMENTO
# ═══════════════════════════════════════════════════════════════
print("=" * 60)
print("✅ VIDEO PRONTO!")
print("=" * 60)

if os.path.exists('final_video.mp4'):
    print("✅ Video disponibile: final_video.mp4")

if os.path.exists('script.txt'):
    print("✅ Script disponibile: script.txt")

if os.path.exists('image_prompts.txt'):
    print("✅ Prompts disponibili: image_prompts.txt")

print("\n" + "=" * 60)
print("🎉 COMPLETATO! 🚀")
print("=" * 60)
print(f"💰 Costo: ~$0.19 per video")
print("=" * 60)
