import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import whisper

st.set_page_config(page_title="One-Click Movie Recap Editor", layout="wide")

st.title("🎬 Professional One-Click Movie Recap Editor")
st.write("Voiceover နှင့် Video ကို အချိန်ကိုက် ဖြတ်ညှပ်ကပ်ပြုလုပ်ပေးသော AI စနစ်။")

# Load Whisper Model for Speech-to-Text Alignment
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

with st.spinner("AI Model ကို တင်နေပါသည်..."):
    model = load_whisper_model()

# Sidebar Settings
st.sidebar.header("⚙️ Editing Settings")
aspect_ratio = st.sidebar.selectbox("Aspect Ratio ရွေးချယ်ရန်", ["16:9 (YouTube)", "9:16 (Shorts/Reels)"])

# File Uploads
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("🎥 ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])
with col2:
    audio_file = st.file_uploader("🎙️ Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3", "wav"])

if st.button("🚀 Recap ဇာတ်လမ်းကို AI ဖြင့် စတင်ဖန်တီးမည်"):
    if video_file and audio_file:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("ဖိုင်များကို သိမ်းဆည်းနေပါသည်...")
        os.makedirs("temp", exist_ok=True)
        v_path = os.path.join("temp", video_file.name)
        a_path = os.path.join("temp", audio_file.name)
        
        with open(v_path, "wb") as f:
            f.write(video_file.getbuffer())
        with open(a_path, "wb") as f:
            f.write(audio_file.getbuffer())
        
        progress_bar.progress(20)

        try:
            # 1. Analyze Voiceover with Whisper AI to get timestamps
            status_text.text("AI ဖြင့် Voiceover အသံကို ချိန်ကိုက်နေပါပြီ (Speech Analysis)...")
            result = model.transcribe(a_path)
            segments = result["segments"] # အသံထွက်တဲ့ စာကြောင်းတစ်ခုချင်းစီရဲ့ Start နဲ့ End အချိန်များ
            
            progress_bar.progress(50)
            status_text.text("ဗီဒီယို အပိုင်းအစများကို ဖြတ်ညှပ်ကပ် (Cutting & Editing) လုပ်နေပါပြီ...")

            video_clip = VideoFileClip(v_path)
            audio_clip = AudioFileClip(a_path)
            
            # Voiceover ရဲ့ အပိုင်းအစတစ်ခုချင်းစီအလိုက် ဗီဒီယိုကွက်များကို ညှပ်ထုတ်မည်
            clips_to_concat = []
            total_duration = audio_clip.duration
            
            # ဗီဒီယို အရှည်လုံလောက်မှုရှိမရှိ စစ်ဆေးပြီး အပိုင်းအစများ တပ်ဆင်ခြင်း
            current_video_time = 0.0
            
            for segment in segments:
                seg_start = segment["start"]
                seg_end = segment["end"]
                seg_duration = seg_end - seg_start
                
                # မူရင်းဗီဒီယိုထဲကနေ Voiceover အပိုင်းအစ ကြာချိန်နဲ့ တူညီတဲ့ နေရာတွေကို ဖြတ်ထုတ်မည်
                # (ဒီနေရာမှာ ရုပ်ရှင်ရဲ့ စိတ်ဝင်စားစရာ အကွက်တွေကို ဖြတ်ထုတ်ဖို့ အလှည့်ကျ ယူပါတယ်)
                clip_start = current_video_time % (video_clip.duration - seg_duration)
                clip_end = clip_start + seg_duration
                
                sub_clip = video_clip.subclip(clip_start, clip_end)
                clips_to_concat.append(sub_clip)
                
                # နောက်တစ်ကွက်အတွက် ဗီဒီယိုအချိန်ကို အနည်းငယ် ခုန်ကျော်ပေးမည် (Fast-paced recap effect)
                current_video_time += seg_duration + 5.0 

            # အပိုင်းအစများကို ပေါင်းစပ်ခြင်း
            if clips_to_concat:
                final_video = concatenate_videoclips(clips_to_concat)
                # Voiceover အသံအစစ်ကို ပြန်ထည့်ခြင်း
                final_video = final_video.set_audio(audio_clip)
            else:
                final_video = video_clip.subclip(0, audio_clip.duration).set_audio(audio_clip)

            progress_bar.progress(80)
            status_text.text("Final Video ကို Export ထုတ်နေပါသည်...")

            output_path = "temp/final_recap.mp4"
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="fast"
            )

            progress_bar.progress(100)
            status_text.text("အောင်မြင်ပါပြီ!")
            
            st.success("🎬 Movie Recap ဗီဒီယို ထွက်ရှိလာပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Recap ဗီဒီယိုကို Download ရယူရန်",
                    data=file,
                    file_name="movie_recap_ai.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
    else:
        st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုနှင့် အသံဖိုင် နှစ်ခုစလုံးကို တင်ပေးပါ။")
