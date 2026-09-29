import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="One-Click Movie Recap Editor", layout="wide")

st.title("🎬 Professional One-Click Movie Recap Editor")
st.write("Voiceover နှင့် Video ကို ပိုမိုတိကျချောမွေ့စွာ ချိန်ကိုက်ပေးသော စနစ်။")

# Sidebar Settings
st.sidebar.header("⚙️ Editing Settings")
aspect_ratio = st.sidebar.selectbox("Aspect Ratio ရွေးချယ်ရန်", ["16:9 (YouTube)", "9:16 (Shorts/Reels)"])
quality_preset = st.sidebar.selectbox("Video Quality", ["Standard (Fast & Smooth)", "High Quality"])

# File Uploads
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("🎥 ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])
with col2:
    audio_file = st.file_uploader("🎙️ Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3", "wav"])

if st.button("🚀 Recap ဗီဒီယိုကို တိကျစွာ စတင်ဖန်တီးမည်"):
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
            status_text.text("ဗီဒီယိုနှင့် အသံဖိုင်များကို စစ်ဆေးနေပါပြီ...")
            video_clip = VideoFileClip(v_path)
            audio_clip = AudioFileClip(a_path)
            
            total_audio_duration = audio_clip.duration
            video_duration = video_clip.duration
            
            # Voiceover အရှည်နှင့် ကိုက်ညီစေရန် ဗီဒီယို အကွက်များကို အပိုင်းငယ်များခွဲ၍ ညှပ်မည်
            clips_to_concat = []
            # Recap တစ်ကွက်လျှင် ၃ စက္ကန့်မှ ၄ စက္ကန့်အထိထားခြင်းဖြင့် ဇာတ်လမ်းကို မြန်ဆန်စိတ်ဝင်စားဖွယ်ဖြစ်စေမည်
            segment_duration = 3.5  
            
            # မူရင်းဗီဒီယို တစ်ခုလုံးကို အပိုင်းလိုက် თანတူညီမျှ ဖြတ်ထုတ်ရန် ခြေလှမ်း (Step size) တွက်ချက်ခြင်း
            num_segments = int(total_audio_duration / segment_duration)
            if num_segments < 1:
                num_segments = 1
                
            step_size = (video_duration - segment_duration) / num_segments if video_duration > segment_duration else 0
            
            progress_bar.progress(40)
            status_text.text("ဇာတ်ဝင်ခန်းများကို အံဝင်ခွင်ကျ ဖြတ်ညှပ်ကပ် လုပ်နေပါပြီ...")

            for i in range(num_segments):
                start_time = i * step_size
                end_time = start_time + segment_duration
                
                if end_time > video_duration:
                    end_time = video_duration
                if start_time >= video_duration:
                    start_time = max(0, video_duration - segment_duration)
                
                sub_clip = video_clip.subclip(start_time, end_time)
                clips_to_concat.append(sub_clip)

            progress_bar.progress(70)
            status_text.text("ဗီဒီယိုနှင့် အသံကို ပေါင်းစပ်နေပါပြီ...")

            if clips_to_concat:
                final_video = concatenate_videoclips(clips_to_concat, method="compose")
                
                # အကယ်၍ ဖြတ်ထားတဲ့ ဗီဒီယိုက Voiceover ထက် ရှည်နေ거나 တိုနေရင် Voiceover အတိအကျအတိုင်း ညှပ်မည်
                if final_video.duration > total_audio_duration:
                    final_video = final_video.subclip(0, total_audio_duration)
                
                final_video = final_video.set_audio(audio_clip)
            else:
                final_video = video_clip.subclip(0, min(video_duration, total_audio_duration)).set_audio(audio_clip)

            progress_bar.progress(85)
            status_text.text("Video ကို ချောမွေ့စွာ (Smooth Export) ထုတ်နေပါပြီ...")

            output_path = "temp/final_recap.mp4"
            
            # မထစ်စေရန် မြန်ဆန်ပြီး Optimized ဖြစ်သော Settings များဖြင့် Save ခြင်း
            preset_val = "ultrafast" if quality_preset == "Standard (Fast & Smooth)" else "medium"
            
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset=preset_val,
                threads=4
            )

            progress_bar.progress(100)
            status_text.text("ပြီးဆုံးပါပြီ!")
            
            st.success("🎬 Movie Recap ဗီဒီယို အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Recap ဗီဒီယိုကို Download ရယူရန်",
                    data=file,
                    file_name="movie_recap_optimized.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
    else:
        st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုနှင့် အသံဖိုင် နှစ်ခုစလုံးကို တင်ပေးပါ။")
