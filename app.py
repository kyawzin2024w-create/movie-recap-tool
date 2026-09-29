import os
import time
import streamlit as st
from google import genai
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Professional Movie Recapper AI Pro", layout="wide")

st.title("🎬 Professional Movie Recapper AI Pro")
st.write("ဗီဒီယိုဖိုင်ကို အသေးစိတ် Analysis လုပ်ပြီး ဇာတ်ကွက်အလိုက် Recapper Script ရေးသားပေးသော စနစ်။")

# Streamlit secrets သို့မဟုတ် Sidebar မှ API Key ကို ရယူခြင်း
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
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
            st.error("ကျေးဇူးပြု၍ Gemini API Key ထည့်သွင်းပေးပါ။")
        else:
            with st.spinner("ဗီဒီယိုဖိုင်ကို AI ဖြင့် အသေးစိတ် လေ့လာဆန်းစစ်နေပါပြီ..."):
                try:
                    # SDK အသစ်ဖြင့် Client တည်ဆောက်ခြင်း
                    client = genai.Client(api_key=api_key)
                    
                    st.write("📤 Gemini API သို့ ဗီဒီယိုဖိုင် တင်နေပါပြီ...")
                    video_ref = client.files.upload(file=v_path)
                    
                    # ဖိုင် Processing ပြီးဆုံးသည်အထိ စောင့်ဆိုင်းခြင်း
                    while video_ref.state.name == "PROCESSING":
                        time.sleep(2)
                        video_ref = client.files.get(name=video_ref.name)
                        
                    if video_ref.state.name == "FAILED":
                        raise ValueError("ဗီဒီယိုဖိုင် ဆန်းစစ်မှု မအောင်မြင်ပါ။")

                    prompt = """
                    Watch this video closely and strictly READ its on-screen text/subtitles to extract accurate character names and plot points. Write a continuous recap script in Myanmar Language (Burmese) specifically designed for a voiceover.
                    
                    ROLE & STYLE:
                    - Act as a professional Movie Commentary Writer (ရုပ်ရှင်ပြန်ပြောပြတဲ့သူ).
                    - Write like an expert scriptwriter using engaging storytelling techniques.
                    - EXACT CHARACTER NAMES IN BURMESE: You MUST look at the embedded subtitles or on-screen text in the video to find the explicit names of the characters. Transliterate or translate those names into Myanmar language (Burmese).

                    HOOKS & CTA (CRITICAL):
                    - Start the script with a very STRONG HOOK designed for the first 3 seconds.
                    - End the script with a compelling Outro Hook and Call to Action (CTA).

                    CRITICAL CONSTRAINTS:
                    - Do NOT use pronouns unnecessarily.
                    - Do NOT use formal/bookish words ("ဖြစ်သည်", "ရှိသည်", "ဤ", "သို့မဟုတ်", "၏", "ထို့နောက်").
                    - Use conversational, everyday Burmese instead (စကားပြောဟန် စစ်စစ်ကိုသာ သုံးပါ).
                    
                    Output MUST be in Myanmar Language (Burmese) only.
                    """

                    st.write("🤖 AI ဖြင့် Script ကို ရေးသားနေပါပြီ...")
                    # Gemini 2.5 Flash မော်ဒယ်ကို အသုံးပြု၍ Content ထုတ်ခြင်း
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[video_ref, prompt]
                    )
                    
                    generated_script = response.text
                    
                    st.success("✅ Recapper Script အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
                    st.subheader("📝 Generated Recapper Script")
                    st.text_area("Copy ကူးပြီး Voiceover အတွက် အသုံးပြုနိုင်ပါသည်", value=generated_script, height=300)
                    
                    # အသုံးပြုပြီးပါက Server ပေါ်မှ ဖိုင်ကို ဖျက်ပစ်ခြင်း
                    client.files.delete(name=video_ref.name)

                except Exception as e:
                    st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
