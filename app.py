import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="One-Click Movie Recap Editor", layout="wide")

st.title("🎬 Professional One-Click Movie Recap Editor")
st.write("Voiceover အသံဖိုင်နှင့် Movie ဗီဒီယိုကို အလိုအလျောက် ဖြတ်ညှပ်ကပ်ပြုလုပ်ပေးသော စနစ်။")

# Sidebar Settings
st.sidebar.header("⚙️ Editing Settings")
aspect_ratio = st.sidebar.selectbox("Aspect Ratio ရွေးချယ်ရန်", ["16:9 (YouTube)", "9:16 (Shorts/Reels)"])

# File Uploads
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("🎥 ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])
with col2:
    audio_file = st.file_uploader("🎙️ Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3", "wav"])

if st.button("🚀 Recap ဗီဒီယိုကို စတင်ဖန်တီးမည်"):
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
        
        progress_bar.progress(30)

        try:
            status_text.text("ဗီဒီယိုနှင့် အသံဖိုင်များကို စီစဉ်နေပါပြီ...")
            video_clip = VideoFileClip(v_path)
            audio_clip = AudioFileClip(a_path)
            
            total_audio_duration = audio_clip.duration
            video_duration = video_clip.duration
            
            clips_to_concat = []
            segment_duration = 5.0  # ဗီဒီယိုကွက် တစ်ကွက်လျှင် ၅ စက္ကန့်စီ ဖြတ်မည်
            
            current_time = 0.0
            # Voiceover အရှည်အတိုင်း ဇာတ်ဝင်ခန်းအမျိုးမျိုးကို အပိုင်းလိုက် ဖြတ်ထုတ်ပြီး ပေါင်းမည်
            while current_time < total_audio_duration and current_time < video_duration:
                end_time = current_time + segment_duration
                if end_time > video_duration:
                    end_time = video_duration
                
                sub_clip = video_clip.subclip(current_time, end_time)
                clips_to_concat.append(sub_clip)
                
                # နောက်ထပ် ခုန်ကူးမယ့် နေရာ (Recap ပုံစံ မြန်မြန်သွားစေရန်)
                current_time += segment_duration + 10.0 

            progress_bar.progress(70)
            status_text.text("ဇာတ်ဝင်ခန်းများကို ပေါင်းစပ်နေပါပြီ...")

            if clips_to_concat:
                final_video = concatenate_videoclips(clips_to_concat)
                
                # အကယ်၍ ဖြတ်ထားတဲ့ ဗီဒီယိုက Voiceover ထက် တိုနေရင် အသံနဲ့ အညီ ညှပ်မယ်
                if final_video.duration > total_audio_duration:
                    final_video = final_video.subclip(0, total_audio_duration)
                
                final_video = final_video.set_audio(audio_clip)
            else:
                final_video = video_clip.subclip(0, min(video_duration, total_audio_duration)).set_audio(audio_clip)

            progress_bar.progress(90)
            status_text.text("Final Video ကို ထုတ်လုပ်နေပါပြီ...")

            output_path = "temp/final_recap.mp4"
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="fast"
            )

            progress_bar.progress(100)
            status_text.text("ပြီးဆုံးပါပြီ!")
            
            st.success("🎬 Movie Recap ဗီဒီယို အောင်မြင်စွာ ထွက်ရှိလာပါပြီ!")
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
