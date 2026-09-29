import os
import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Professional Movie Recapper AI Pro", layout="wide")

st.title("🎬 Professional Movie Recapper AI Pro")
st.write("ဗီဒီယိုဖိုင်ကို အသေးစိတ် Analysis လုပ်ပြီး ဇာတ်ကွက်အလိုက် Recapper Script ရေးသားပေးသော စနစ်။")

# Sidebar - API Key Configuration
st.sidebar.header("⚙️ API Configuration")
api_key = st.sidebar.text_input("Gemini API Key ထည့်ရန်", type="password")

# File Upload
st.subheader("📌 ဗီဒီယိုဖိုင် တင်ရန်")
video_file = st.file_uploader("🎥 မူရင်း ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])

os.makedirs("temp", exist_ok=True)

if video_file:
    v_path = os.path.join("temp", video_file.name)
    with open(v_path, "wb") as f:
        f.write(video_file.getbuffer())
        
    video_clip = VideoFileClip(v_path)
    original_duration_min = round(video_clip.duration / 60, 2)
    st.info(f"📁 တင်ထားသော ဗီဒီယို ကြာချိန်: {original_duration_min} မိနစ်")

    if st.button("🚀 AI ဖြင့် အသေးစိတ် Recapper Script ထုတ်မည်"):
        if not api_key:
            st.error("ကျေးဇူးပြု၍ Sidebar တွင် Gemini API Key ထည့်သွင်းပေးပါ။")
        else:
            with st.spinner("ဗီဒီယိုဖိုင်ကို AI ဖြင့် အသေးစိတ် လေ့လာဆန်းစစ်နေပါပြီ (Analyzing Visuals & Subtitles)..."):
                try:
                    # Configure Gemini API
                    genai.configure(api_key=api_key)
                    
                    # Upload video file to Gemini File API for processing
                    st.write("📤 Gemini API သို့ ဗီဒီယိုဖိုင် တင်နေပါပြီ...")
                    video_ref = genai.upload_file(v_path)
                    
                    # Wait for file processing if necessary
                    import time
                    while video_ref.state.name == "PROCESSING":
                        time.sleep(2)
                        video_ref = genai.get_file(video_ref.name)
                        
                    if video_ref.state.name == "FAILED":
                        raise ValueError("ဗီဒီယိုဖိုင် ဆန်းစစ်မှု မအောင်မြင်ပါ။")

                    # Prompt for Script Generation (React code မှ ယူထားသော Professional Prompt)
                    prompt = """
                    Watch this video closely and strictly READ its on-screen text/subtitles to extract accurate character names and plot points. Write a continuous recap script in Myanmar Language (Burmese) specifically designed for a voiceover.
                    
                    ROLE & STYLE:
                    - Act as a professional Movie Commentary Writer (ရုပ်ရှင်ပြန်ပြောပြတဲ့သူ).
                    - Write like an expert scriptwriter using engaging storytelling techniques.
                    - EXACT CHARACTER NAMES IN BURMESE: You MUST look at the embedded subtitles or on-screen text in the video to find the explicit names of the characters. However, you MUST transliterate/translate those names into Myanmar language (Burmese) in the script. Do not leave names in English characters. Do not invent names or use generic names if their identities are visible.

                    HOOKS & CTA (CRITICAL):
                    - Start the script with a very STRONG HOOK designed for the first 3 seconds of the video to immediately grab audience attention.
                    - End the script with a compelling Outro Hook (cliffhanger) and a strong Call to Action (CTA).

                    CRITICAL LENGTH & TIMING MATCH (MUST READ):
                    - Write precisely and scene-by-scene like a professional scriptwriter. Match the pacing precisely without dragging details out too naturally.
                    - Avoid awkward silences, but keep the voiceover flowing smoothly across the entire timeline based purely on the story details.
                    - DO NOT add unnecessary filler phrases or artificial interactive commentary (e.g., completely AVOID phrases like "ဒီနေရာမှာဆိုရင်...", "ကြည့်လိုက်ပါဦး...", "တကယ်ကို မထင်မှတ်ထားဘူး..."). Keep the storytelling focused and organic.
                    
                    CRITICAL CONSTRAINTS:
                    - Do NOT use pronouns (နာမ်စားများ) unless absolutely necessary for clarity.
                    - Do NOT use formal/bookish words: "ဖြစ်သည်", "ရှိသည်", "ဤ", "သို့မဟုတ်", "၏", "ထို့နောက်".
                    - Use conversational, everyday Burmese instead (စကားပြောဟန် စစ်စစ်ကိုသာ သုံးပါ).
                    
                    Output MUST be in Myanmar Language (Burmese) only.
                    """

                    st.write("🤖 AI ဖြင့် Script ကို ရေးသားနေပါပြီ...")
                    # Using gemini-2.5-flash or compatible model for multimodal video input
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content([video_ref, prompt])
                    
                    generated_script = response.text
                    
                    st.success("✅ Recapper Script အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
                    
                    st.subheader("📝 Generated Recapper Script")
                    st.text_area("Copy ကူးပြီး Voiceover အတွက် အသုံးပြုနိုင်ပါသည်", value=generated_script, height=300)
                    
                    # Clean up file from Gemini server after use
                    genai.delete_file(video_ref.name)

                except Exception as e:
                    st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
