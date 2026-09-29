import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
from PIL import Image

st.set_page_config(page_title="One-Click Movie Recap Editor", layout="wide")

st.title("🎬 One-Click Movie Recap & Fair-Use Editor")
st.write("ရုပ်ရှင်ဗီဒီယိုနှင့် Voiceover ဖိုင်များကို တင်ပြီး အလိုအလျောက် Edit လုပ်ပါ။")

# Sidebar - Settings & Customization
st.sidebar.header("⚙️ Editing Settings")
aspect_ratio = st.sidebar.selectbox("Aspect Ratio ရွေးချယ်ရန်", ["16:9 (YouTube)", "9:16 (Shorts/Reels)"])
enable_blur = st.sidebar.checkbox("Video ပေါ်တွင် Blur ထည့်ရန် (Fair Use အတွက်)")
font_choice = st.sidebar.file_uploader("Custom Font တင်ရန် (.ttf)", type=["ttf"])
logo_file = st.sidebar.file_uploader("Logo ပုံတင်ရန် (PNG)", type=["png", "jpg"])

# Main Area - File Uploads
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("🎥 ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])
with col2:
    audio_file = st.file_uploader("🎙️ Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3", "wav"])

if st.button("🚀 Recap Video စတင်ဖန်တီးမည်"):
    if video_file and audio_file:
        with st.spinner("ဗီဒီယိုနှင့် အသံကို ချိန်ကိုက်နေပါပြီ (Processing)..."):
            # Temporary files သိမ်းဆည်းရန်
            os.makedirs("temp", exist_ok=True)
            v_path = os.path.join("temp", video_file.name)
            a_path = os.path.join("temp", audio_file.name)
            
            with open(v_path, "wb") as f:
                f.write(video_file.getbuffer())
            with open(a_path, "wb") as f:
                f.write(audio_file.getbuffer())

            try:
                # MoviePy ဖြင့် Video နှင့် Audio ကို ချိတ်ဆက်ခြင်း
                video_clip = VideoFileClip(v_path)
                audio_clip = AudioFileClip(a_path)
                
                # Voiceover အရှည်အတိုင်း ဗီဒီယိုကို ညှပ်မည် (သို့ ချိန်ကိုက်မည်)
                if video_clip.duration > audio_clip.duration:
                    final_clip = video_clip.subclip(0, audio_clip.duration)
                else:
                    final_clip = video_clip
                
                final_clip = final_clip.with_audio(audio_clip)
                
                # Output Path
                output_path = "temp/output_recap.mp4"
                final_clip.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=24,
                    preset="fast"
                )

                st.success("✅ ဗီဒီယို အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Recap ဗီဒီယိုကို Download ရယူရန်",
                        data=file,
                        file_name="movie_recap_final.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
    else:
        st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုနှင့် အသံဖိုင် နှစ်ခုစလုံးကို တင်ပေးပါ။")
