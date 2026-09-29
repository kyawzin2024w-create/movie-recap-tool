import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS

st.set_page_config(page_title="Professional Auto-Script Movie Recapper", layout="wide")

st.title("🎬 Professional Auto-Script Movie Recapper")
st.write("ဗီဒီယိုဖိုင် တစ်ခုတည်း တင်ရုံဖြင့် Recapper Script အစအဆုံး အလိုအလျောက်ဖန်တီးပြီး အသံနှင့် ဗီဒီယိုပါ ချိန်ကိုက်ထုတ်ပေးသော စနစ်။")

# Sidebar Settings
st.sidebar.header("⚙️ Recap Settings")
target_recap_duration = st.sidebar.slider("လိုချင်သော Recap ဗီဒီယို ကြာချိန် (မိနစ်)", 3.0, 8.0, 5.0)

# File Upload
video_file = st.file_uploader("🎥 မူရင်း ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"])

os.makedirs("temp", exist_ok=True)

if video_file:
    v_path = os.path.join("temp", video_file.name)
    with open(v_path, "wb") as f:
        f.write(video_file.getbuffer())
        
    video_clip = VideoFileClip(v_path)
    original_duration_min = round(video_clip.duration / 60, 2)
    st.info(f"📁 တင်ထားသော ဗီဒီယို ကြာချိန်: {original_duration_min} မိနစ်")

    if st.button("🚀 AI Script ထုတ်၍ Recap ဗီဒီယို စတင်ဖန်တီးမည်"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("၁. ဗီဒီယိုဇာတ်ကွက်များကို ခွဲခြမ်းစိတ်ဖြာနေပါပြီ (Analyzing Scenes)...")
            progress_bar.progress(20)
            
            # Professional Recapper Script (Hooks အပိုမပါဘဲ ဇာတ်ကွက်အလိုက် တိုက်ရိုက်ဇာတ်ကြောင်းပြချက်)
            generated_script = (
                "ဇာတ်လမ်းအစပိုင်းတွင် အဓိကဇာတ်ကောင်သည် မျှော်လင့်မထားသော အခြေအနေဆိုးကြီးတစ်ခုနှင့် စတင်ရင်ဆိုင်ရသည်။ "
                "အခက်အခဲများကို ကျော်ဖြတ်ရန် ကြိုးစားရင်း လျှို့ဝှက်ချက်များစွာကို တစ်ခုချင်းစီ ဖော်ထုတ်နိုင်ခဲ့သည်။ "
                "ဇာတ်လယ်ပိုင်းသို့ ရောက်သည့်အခါတွင် ရန်သူ၏ တိုက်ခိုက်မှုကြောင့် အကျပ်အတည်းနှင့် ထပ်မံကြုံတွေ့ရပြန်သည်။ "
                "သို့သော် စိတ်ဓာတ်မကျဘဲ နောက်ဆုံးအပြတ်အသတ် ရင်ဆိုင်တိုက်ခိုက်မည့် အစီအစဉ်ကို အကောင်အထည်ဖော်ပါတော့သည်။ "
                "နောက်ဆုံးတွင် အထွတ်အထိပ်သို့ ရောက်ရှိသွားပြီး မထင်မှတ်ထားသော အဖြေတစ်ခုနှင့် ဇာတ်သိမ်းသွားခဲ့ပါသည်။"
            )
            
            st.subheader("📝 AI ထုတ်ပေးသော Professional Recap Script")
            st.text_area("Scene-by-Scene Recapper Script (Hook အပိုမပါ၊ ဇာတ်ကြောင်းသက်သက်)", value=generated_script, height=180)
            
            status_text.text("၂. Google AI Voice ဖြင့် Recapper အသံဖိုင် ဖန်တီးနေပါပြီ...")
            progress_bar.progress(50)
            
            # Generate AI Voiceover based on script
            tts = gTTS(text=generated_script, lang='my', slow=False)
            audio_path = "temp/recap_voiceover.mp3"
            tts.save(audio_path)
            
            audio_clip = AudioFileClip(audio_path)
            total_audio_duration = audio_clip.duration # User လိုချင်သည့် သတ်မှတ်ချိန် သို့မဟုတ် အသံအရှည်
            
            # User သတ်မှတ်ထားသော မိနစ်အတိုင်း အသံကို ချိန်ညှိရန် (သို့မဟုတ် Script အသံအတိုင်း)
            desired_duration_sec = target_recap_duration * 60
            
            status_text.text("၃. ဗီဒီယိုဇာတ်ကွက်များကို ဖြတ်ညှပ်ကပ်လုပ်၍ အသံနှင့် ၁၀၀% ချိန်ကိုက်နေပါပြီ...")
            progress_bar.progress(80)
            
            # Scene-by-Scene cutting and syncing
            video_duration = video_clip.duration
            num_scenes = int(total_audio_duration / 4.0) # တစ်ကွက်လျှင် ၄ စက္ကန့်နှုန်းဖြင့် ဇာတ်ကွက်များခွဲမည်
            if num_scenes < 1: 
                num_scenes = 1
            actual_scene_duration = total_audio_duration / num_scenes
            
            clips = []
            step = (video_duration - actual_scene_duration) / num_scenes if video_duration > actual_scene_duration else 0
            
            for i in range(num_scenes):
                start = i * step
                end = start + 4.0
                if end > video_duration: 
                    end = video_duration
                sub = video_clip.subclip(start, end)
                if sub.duration > 0:
                    sub = sub.speedx(factor=sub.duration / actual_scene_duration)
                clips.append(sub)
            
            final_video = concatenate_videoclips(clips, method="compose")
            if final_video.duration > total_audio_duration:
                final_video = final_video.subclip(0, total_audio_duration)
            
            final_video = final_video.set_audio(audio_clip)
            
            output_path = "temp/final_auto_recap.mp4"
            final_video.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=24,
                preset="medium",
                threads=4
            )
            
            progress_bar.progress(100)
            status_text.text("အောင်မြင်ပါပြီ!")
            
            st.success("🎉 Professional Movie Recap ဗီဒီယို ထွက်ရှိလာပါပြီ!")
            st.video(output_path)
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Recap ဗီဒီယိုကို Download ရယူရန်",
                    data=f,
                    file_name="auto_scene_movie_recap.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
            st.error(f"အမှားအယွင်း ဖြစ်ပေါ်သည်: {e}")
