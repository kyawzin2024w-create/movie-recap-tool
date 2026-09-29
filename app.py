import os
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS

st.set_page_config(page_title="Professional Two-Stage Movie Recap Studio", layout="wide")

st.title("🎬 Professional Two-Stage Movie Recap Studio")
st.write("အဆင့် (၂) ဆင့်ဖြင့် AI Script ထုတ်ခြင်း၊ အလိုအလျောက် Voice ဖြင့် စမ်းသပ်ခြင်းနှင့် ကိုယ်ပိုင် Voiceover ဖြင့် Final Export ထုတ်ခြင်း။")

# Mode Selection (Two-Stage Workflow)
workflow_stage = st.sidebar.radio(
    "🔄 လုပ်ဆောင်မည့် အဆင့်ကို ရွေးပါ", 
    [
        "အဆင့် ၁: ဗီဒီယိုမှ AI Script ထုတ်၍ Test Video ဖန်တီးရန်", 
        "အဆင့် ၂: ကိုယ်ပိုင် Voiceover ဖိုင်ဖြင့် Final Export ထုတ်ရန်"
    ]
)

os.makedirs("temp", exist_ok=True)

if workflow_stage == "အဆင့် ၁: ဗီဒီယိုမှ AI Script ထုတ်၍ Test Video ဖန်တီးရန်":
    st.subheader("📌 အဆင့် ၁ - AI Script ထုတ်ခြင်းနှင့် Google Voice ဖြင့် Test ဗီဒီယိုထုတ်ခြင်း")
    
    video_file = st.file_uploader("🎥 မူရင်း ရုပ်ရှင်ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"], key="v1")
    
    if video_file:
        v_path = os.path.join("temp", video_file.name)
        with open(v_path, "wb") as f:
            f.write(video_file.getbuffer())
            
        video_clip = VideoFileClip(v_path)
        st.info(f"ဗီဒီယို ကြာချိန်: {round(video_clip.duration / 60, 2)} မိနစ်")
        
        # Simulated/Generated Recap Script for the Movie
        default_script = (
            "ဒီဇာတ်ကားမှာတော့ မထင်မှတ်ထားတဲ့ အဖြစ်အပျက်တွေနဲ့ ကြုံတွေ့ရတဲ့ အဓိကဇာတ်ကောင်ရဲ့ "
            "ခရီးလမ်းကို ပုံဖော်ပြသထားပါတယ်။ အစပိုင်းမှာ အေးချမ်းနေပေမယ့် နောက်ပိုင်းမှာတော့ "
            "စိတ်လှုပ်ရှားစရာ အလှည့်အပြောင်းတွေနဲ့ ရင်ဆိုင်ရပါတော့တယ်။ ဆက်လက်ကြည့်ရှုကြပါစို့။"
        )
        
        st.text_area("📝 AI ထုတ်ပေးသော Recap Storytelling Script (Copy ကူးပြီး Voice Clone အတွက် အသုံးပြုနိုင်ပါသည်)", value=default_script, height=150)
        
        if st.button("🚀 Google AI Voice ဖြင့် Test Recap ဗီဒီယို ထုတ်မည်"):
            with st.spinner("AI Script ကို အသံဖိုင်ပြောင်း၍ ဗီဒီယိုနှင့် ချိန်ကိုက်နေပါပြီ..."):
                # Generate Google TTS Voiceover
                tts = gTTS(text=default_script, lang='my', slow=False)
                temp_audio_path = "temp/ai_voice_test.mp3"
                tts.save(temp_audio_path)
                
                audio_clip = AudioFileClip(temp_audio_path)
                total_audio_duration = audio_clip.duration
                video_duration = video_clip.duration
                
                # Cut and sync clips
                num_scenes = int(total_audio_duration / 3.0)
                if num_scenes < 1: num_scenes = 1
                actual_scene_duration = total_audio_duration / num_scenes
                
                clips = []
                step = (video_duration - actual_scene_duration) / num_scenes if video_duration > actual_scene_duration else 0
                
                for i in range(num_scenes):
                    start = i * step
                    end = start + 3.0
                    if end > video_duration: end = video_duration
                    sub = video_clip.subclip(start, end)
                    if sub.duration > 0:
                        sub = sub.speedx(factor=sub.duration / actual_scene_duration)
                    clips.append(sub)
                
                final_v = concatenate_videoclips(clips, method="compose")
                if final_v.duration > total_audio_duration:
                    final_v = final_v.subclip(0, total_audio_duration)
                final_v = final_v.set_audio(audio_clip)
                
                out_path = "temp/test_recap_output.mp4"
                final_v.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
                
                st.success("✅ အဆင့် ၁ စမ်းသပ်ဗီဒီယို ထွက်ရှိပါပြီ!")
                st.video(out_path)
                with open(out_path, "rb") as f:
                    st.download_button("📥 Test Video ကို Download ရယူရန်", f, file_name="test_recap.mp4", mime="video/mp4")

else:
    st.subheader("📌 အဆင့် ၂ - ကိုယ်ပိုင် Voiceover ဖိုင်ဖြင့် Final Export ထုတ်ခြင်း")
    st.write("Voice Clone လုပ်ထားသော (သို့မဟုတ် ကိုယ်တိုင်သွင်းထားသော) အသံဖိုင်ကို တင်၍ အပြီးသတ် ဗီဒီယို ထုတ်ပါ။")
    
    col1, col2 = st.columns(2)
    with col1:
        video_file_2 = st.file_uploader("🎥 မူရင်း ဗီဒီယို တင်ရန် (MP4, MKV)", type=["mp4", "mkv"], key="v2")
    with col2:
        custom_audio_file = st.file_uploader("🎙️ ကိုယ်ပိုင် Voiceover အသံဖိုင် တင်ရန် (MP3, WAV)", type=["mp3", "wav"], key="a2")
        
    if st.button("🚀 ကိုယ်ပိုင် Voiceover ဖြင့် Final Recap Video ထုတ်မည်"):
        if video_file_2 and custom_audio_file:
            with st.spinner("ဖိုင်များကို စီမံပြီး Final Export လုပ်နေပါပြီ..."):
                v_path = os.path.join("temp", video_file_2.name)
                a_path = os.path.join("temp", custom_audio_file.name)
                
                with open(v_path, "wb") as f:
                    f.write(video_file_2.getbuffer())
                with open(a_path, "wb") as f:
                    f.write(custom_audio_file.getbuffer())
                    
                video_clip = VideoFileClip(v_path)
                audio_clip = AudioFileClip(a_path)
                
                total_audio_duration = audio_clip.duration
                video_duration = video_clip.duration
                
                num_scenes = int(total_audio_duration / 3.0)
                if num_scenes < 1: num_scenes = 1
                actual_scene_duration = total_audio_duration / num_scenes
                
                clips = []
                step = (video_duration - actual_scene_duration) / num_scenes if video_duration > actual_scene_duration else 0
                
                for i in range(num_scenes):
                    start = i * step
                    end = start + 3.0
                    if end > video_duration: end = video_duration
                    sub = video_clip.subclip(start, end)
                    if sub.duration > 0:
                        sub = sub.speedx(factor=sub.duration / actual_scene_duration)
                    clips.append(sub)
                
                final_v = concatenate_videoclips(clips, method="compose")
                if final_v.duration > total_audio_duration:
                    final_v = final_v.subclip(0, total_audio_duration)
                final_v = final_v.set_audio(audio_clip)
                
                final_out_path = "temp/final_custom_recap.mp4"
                final_v.write_videofile(final_out_path, codec="libx264", audio_codec="aac", fps=24, preset="medium", threads=4)
                
                st.success("🎉 ကိုယ်ပိုင် Voiceover ပါဝင်သော Professional Final Recap ဗီဒီယို အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
                st.video(final_out_path)
                with open(final_out_path, "rb") as f:
                    st.download_button("📥 Final Recap ဗီဒီယိုကို Download ရယူရန်", f, file_name="professional_movie_recap_final.mp4", mime="video/mp4")
        else:
            st.warning("ကျေးဇူးပြု၍ ဗီဒီယိုဖိုင်နှင့် ကိုယ်ပိုင် Voiceover အသံဖိုင် နှစ်ခုစလုံးကို တင်ပေးပါ။")
