import os
import streamlit as st
import google.generativeai as genai
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Professional Movie Recapper AI Pro", layout="wide")

st.title("🎬 Professional Movie Recapper AI Pro")

# Streamlit secrets မှ API Key ကို အလိုအလျောက် ယူမည်
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key ထည့်ရန်", type="password")

os.makedirs("temp", exist_ok=True)
video_file = st.file_uploader("🎥 မူရင်း ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])

if video_file:
    v_path = os.path.join("temp", video_file.name)
    with open(v_path, "wb") as f:
        f.write(video_file.getbuffer())
        
    if st.button("🚀 AI ဖြင့် အသေးစိတ် Recapper Script ထုတ်မည်"):
        if not api_key:
            st.error("ကျေးဇူးပြု၍ API Key ထည့်သွင်းပေးပါ။")
        else:
            with st.spinner("ဗီဒီယိုဖိုင်ကို AI ဖြင့် လေ့လာဆန်းစစ်နေပါပြီ..."):
                try:
                    genai.configure(api_key=api_key)
                    video_ref = genai.upload_file(v_path)
                    
                    import time
                    while video_ref.state.name == "PROCESSING":
                        time.sleep(2)
                        video_ref = genai.get_file(video_ref.name)
                        
                    prompt = "Watch this video closely and write a professional recap script in Myanmar language (Burmese) scene-by-scene without fillers."
                    
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content([video_ref, prompt])
                    
                    st.success("✅ Recapper Script ထွက်ရှိလာပါပြီ!")
                    st.text_area("Generated Script", value=response.text, height=300)
                    
                    genai.delete_file(video_ref.name)
                except Exception as e:
                    st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
