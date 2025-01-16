import streamlit as st
from pydub import AudioSegment
from pydub.utils import which
import pyttsx3
import os
import tempfile

# Set the path to FFmpeg and FFprobe
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

def generate_audio_with_pauses(text, word_pause=1.82):
    """
    Generate an audio file from text with a 1.82-second pause between words using offline TTS.
    
    Args:
        text (str): The input text.
        word_pause (float): Pause duration in seconds between words.
    
    Returns:
        str: Path to the generated audio file.
    """
    engine = pyttsx3.init()
    temp_dir = tempfile.mkdtemp()
    audio_segments = []

    for word in text.split():
        try:
            # Save the word audio locally
            temp_file = os.path.join(temp_dir, f"{word}.wav")
            engine.save_to_file(word, temp_file)
            engine.runAndWait()

            # Load the audio and add a pause
            word_audio = AudioSegment.from_file(temp_file)
            audio_segments.append(word_audio)
            audio_segments.append(AudioSegment.silent(duration=word_pause * 1000))  # 1.82 seconds pause
        except Exception as e:
            st.error(f"Error generating audio for word '{word}': {e}")

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
