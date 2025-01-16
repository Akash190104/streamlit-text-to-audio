import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import which
import os
import tempfile
import time

# Set the path to FFmpeg and FFprobe
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

def generate_audio_with_pauses(text, word_pause=1.82):
    """
    Generate an audio file from text with a 1.82-second pause between words.
    
    Args:
        text (str): The input text.
        word_pause (float): Pause duration in seconds between words.
    
    Returns:
        str: Path to the generated audio file.
    """
    words = text.split()
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    for word in words:
        try:
            # Generate audio for each word
            tts = gTTS(word, lang='en')
            temp_file = os.path.join(temp_dir, f"{word}.mp3")
            tts.save(temp_file)
            word_audio = AudioSegment.from_file(temp_file)
            audio_segments.append(word_audio)
            audio_segments.append(AudioSegment.silent(duration=word_pause * 1000))  # 1.82 seconds pause
        except Exception as e:
            st.warning(f"Skipping word '{word}' due to an error: {e}")

    if not audio_segments:
        raise ValueError("No valid audio segments were created.")

    # Concatenate all audio segments
    final_audio = sum(audio_segments)
    output_file = os.path.join(temp_dir, "output_audio.mp3")
    final_audio.export(output_file, format="mp3")
    return output_file

# Streamlit UI
st.title("Text to Audio with Word Gaps")
st.write("Enter text and get an audio file where each word is spoken with a 1.82-second gap.")

# User input
user_input = st.text_area("Enter your text here:", "")
if st.button("Generate Audio"):
    if user_input.strip():
        try:
            # Generate audio
            output_audio_path = generate_audio_with_pauses(user_input)
            
            # Display and provide download option
            with open(output_audio_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
                st.download_button("Download Audio", audio_file, file_name="output_audio.mp3")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter some text.")
