import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="Professional Movie Recap Editor", layout="wide")

st.title("🎬 Professional 100% Synced Movie Recap Editor")
st.write("Voiceover နှင့် Video ကို Speed (Slow/Fast) အလိုအလျောက် ချိန်ညှိ၍ ၁၀၀% တိကျစွာ ချိတ်ဆက်ပေးသော စနစ်။")

# Sidebar Settings
st.sidebar.header("⚙️ Editing Settings")
aspect_ratio = st.sidebar.selectbox("Aspect Ratio ရွေးချယ်ရန်", ["16:9 (YouTube)", "9:16 (Shorts/Reels)"])
transition_speed = st.sidebar.slider("Recap Scene တစ်ကွက်၏ ကြာချိန် (စက္ကန့်)", 2.0, 6.0, 3.0)

# File Uploads
col1, col2 = st.columns(2)
with col1:
    video_file = st.file_uploader("🎥 ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])
with col2:
    audio_file = st.file_uploader("🎙️ Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3, wav"])

if st.button("🚀 ၁၀၀% တိကျသော Recap ဗီဒီယိုကို ဖန်တီးမည်"):
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
            status_text.text("ဗီဒီယိုနှင့် အသံဖိုင်များကို ခွဲခြမ်းစိတ်ဖြာနေပါပြီ...")
            video_clip = VideoFileClip(v_path)
            audio_clip = AudioFileClip(a_path)
            
            total_audio_duration = audio_clip.duration
            video_duration = video_clip.duration
            
            # Voiceover ရဲ့ စုစုပေါင်း အချိန်ပေါ်မူတည်၍ ဇာတ်ကွက်အရေအတွက်ကို အတိအကျ တွက်ချက်ခြင်း
            target_scene_duration = transition_speed
            num_scenes = int(total_audio_duration / target_scene_duration)
            if num_scenes < 1:
                num_scenes = 1
                
            actual_scene_duration = total_audio_duration / num_scenes
            
            clips_to_concat = []
            step_size = (video_duration - actual_scene_duration) / num_scenes if video_duration > actual_scene_duration else 0
            
            progress_bar.progress(50)
            status_text.text("Video Scenes များကို Voiceover အချိန်နှင့်အညီ Speed (Slow/Fast) ချိန်ညှိနေပါပြီ...")

            for i in range(num_scenes):
                start_time = i * step_size
                end_time = start_time + target_scene_duration
                
                if end_time > video_duration:
                    end_time = video_duration
                if start_time >= video_duration:
                    start_time = max(0, video_duration - target_scene_duration)
                
                # မူရင်း ဗီဒီယို အပိုင်းအစကို ဖြတ်ထုတ်ခြင်း
                sub_clip = video_clip.subclip(start_time, end_time)
                
                # [PRO FEATURE] Voiceover ရဲ့ သတ်မှတ်ထားသော အပိုင်းအစ အချိန်နှင့် 
                # ဖြတ်ထားသော ဗီဒီယို အပိုင်းအစ အချိန် အတိအကျ ကိုက်ညီစေရန် Speed (fx) ကို ချိန်ညှိခြင်း
                current_sub_duration = sub_clip.duration
                if current_sub_duration > 0:
                    speed_factor = current_sub_duration / actual_scene_duration
                    # MoviePy ၏ speedx ကိုသုံး၍ ဗီဒီယိုကို လိုအပ်သလို အမြန်/အနှေး (Fast/Slow) ပြောင်းလဲခြင်း
                    sub_clip = sub_clip.speedx(factor=speed_factor)
                
                clips_to_concat.append(sub_clip)

            progress_bar.progress(80)
            status_text.text("Voiceover အသံနှင့် ဗီဒီယိုများကို အပြီးသတ် ပေါင်းစပ်နေပါပြီ...")

            if clips_to_concat:
                final_video = concatenate_videoclips(clips_to_concat, method="compose")
                
                # Voiceover ကို မူသေအဖြစ် အပြည့်အစုံ တပ်ဆင်ခြင်း (၁၀၀% Sync ဖြစ်စေရန်)
                final_video = final_video.set_audio(audio_clip)
            else:
                final_video = video_clip.subclip(0, min(video_duration, total_audio_duration)).set_audio(audio_clip)

            progress_bar.progress(95)
            status_text.text("Final Video ကို ထုတ်လုပ်နေပါပြီ...")

            output_path = "temp/final_perfect_recap.mp4"
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="medium",
                threads=4
            )

            progress_bar.progress(100)
            status_text.text("ပြီးဆုံးပါပြီ!")
            
            st.success("🎬 ၁၀၀% တိကျစွာ ချိန်ကိုက်ထားသော Movie Recap ဗီဒီယို ထွက်ရှိလာပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 တိကျမှန်ကန်သော Recap ဗီဒီယိုကို Download ရယူရန်",
                    data=file,
                    file_name="movie_recap_perfect_sync.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
    else:
        st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုနှင့် အသံဖိုင် နှစ်ခုစလုံးကို တင်ပေးပါ။")
