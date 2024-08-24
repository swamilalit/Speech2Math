import streamlit as st
from audiorecorder import audiorecorder
import speech_recognition as sr
import io
from pydub import AudioSegment
import pandas as pd
import numpy as np
import re

# Load data
df_c = pd.read_csv(r"https://raw.githubusercontent.com/swamilalit/Speech2Math/main/data/data.csv")

def print_n_choose_k(n, k):
    # Convert n and k to superscript and subscript characters
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    
    # Return the result
    return f"{n_str}P{k_str}"

def print_combi(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(superscript_digits)
    k_str = str(k).translate(subscript_digits)
    
    # Return the result
    return f"{n_str}C{k_str}"

def print_integral(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(subscript_digits)
    k_str = str(k).translate(superscript_digits)
    
    # Return the result
    return f"{n_str}{chr(0x222B)}{k_str}"

def print_d_integral(n,k):
    superscript_digits = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    subscript_digits = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    n_str = str(n).translate(subscript_digits)
    k_str = str(k).translate(superscript_digits)
    
    # Return the result
    return f"{n_str}{chr(0x222B)}{chr(0x222B)}{k_str}"

# Function to escape special characters
def escape_special_characters(text):
    # Escape special characters for regular expressions
    escaped_text = re.escape(text)
    return escaped_text

st.title("Audio Recorder")
audio = audiorecorder("Click to record", "Click to stop recording")

if len(audio) > 0:
    # To play audio in frontend:
    st.audio(audio.export().read(), format='audio/wav')  

    # To get audio properties, use pydub AudioSegment properties:
    #st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")
    
    # Export the audio to a bytes buffer
    audio_bytes = audio.export().read()
    
    # Check if the audio_bytes is not empty
    if audio_bytes:
        #st.write("Audio successfully saved in bytes buffer.")
        
        try:
            # Initialize recognizer
            r = sr.Recognizer()
            #st.write("Recognizer called")
            
            # Convert audio bytes to AudioSegment
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Export AudioSegment to a WAV format bytes buffer
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            
            # Use the wav buffer with speech recognition
            with sr.AudioFile(wav_buffer) as source:
                audio_text = r.record(source)
                #st.write("Audio text recorded")

                # Recognize speech using Google Speech Recognition
                text = r.recognize_google(audio_text)
                st.write("Recognized Text:", text)
                st.write("Converting into mathematical equation:")
                text_lower = text.lower().split()  # Split the recognized text into words
                equation = ''
                skip_next_words = False
                
                # Loop through each word in the recognized text
                i = 0
                while i < len(text_lower):
                    word = text_lower[i]
                    if word == "^" :
                        i = i + 1
                        if text_lower[i] == "2":
                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                        elif text_lower[i] == "3":
                            equation +=  (chr(0x00B0 + int(text_lower[i])))
                        else:
                             equation +=  (chr(0x2070 + int(text_lower[i])))
                        i = i + 1
                        if i < len(text_lower):
                            continue
                        else:
                            break
                    escaped_word = escape_special_characters(word)
                    if df_c['Name'].str.contains(escaped_word, case=False).any():
                        remaining_text = ' '.join(text_lower[i:])
                        # Check if the remaining text matches any name in the DataFrame
                        for j in range(len(remaining_text.split()), 0, -1):
                            str_to_check = ' '.join(remaining_text.split()[:j])
                            if str_to_check in df_c['Name'].str.lower().values:
                                if str_to_check == "to the power":
                                    i = i + 3
                                    if text_lower[i] == "2":
                                        equation +=  (chr(0x00B0 + int(text_lower[i])))
                                    elif text_lower[i] == "3":
                                        equation +=  (chr(0x00B0 + int(text_lower[i])))
                                    else:
                                        equation +=  (chr(0x2070 + int(text_lower[i])))
                                    i = i + 1
                                elif str_to_check == "raised to" :
                                    i = i + 2
                                    if text_lower[i] == "2":
                                        equation +=  (chr(0x00B0 + int(text_lower[i])))
                                    elif text_lower[i] == "3":
                                        equation +=  (chr(0x00B0 + int(text_lower[i])))
                                    else:
                                        equation +=  (chr(0x2070 + int(text_lower[i])))
                                    i = i + 1
                                elif str_to_check == "square" :
                                    equation +=  (chr(0x00B0 + int(2)))
                                    i = i + 1
                                elif str_to_check == "cube":
                                    equation +=  (chr(0x00B0 + int(3)))
                                    i = i + 1
                                elif str_to_check == "permutation":
                                    var = print_n_choose_k(equation[-2], text_lower[i+1])
                                    equation= equation.replace(equation[-2],var,1)
                                    i = i + 2
                                elif str_to_check == "combination":
                                    var = print_combi(equation[-2], text_lower[i+1])
                                    equation= equation.replace(equation[-2],var,1)
                                    i = i + 2
                                elif str_to_check == "integral":
                                    var = print_integral(equation[-2], text_lower[i+1])
                                    equation= equation.replace(equation[-2],var,1)
                                    i = i + 2
                                elif str_to_check == "double integral":
                                    var = print_d_integral(equation[-2], text_lower[i+2])
                                    equation= equation.replace(equation[-2],var,1)
                                    i = i + 3
                                else:
                                    equation += df_c.loc[df_c['Name'].str.lower() == str_to_check, 'Symbol'].values[0] + ' '
                                    i += len(str_to_check.split())
                                skip_next_words = True
                                break
                    if not skip_next_words:
                        equation += word + ' '
                        i += 1
                    else:
                        skip_next_words = False
    
                st.write("Equation:", equation.strip())  #Strip trailing whitespace to remove extra space at the end
                st.markdown("""
                        <p style='text-align: center;'>
                        <a href="https://speech2math-app.streamlit.app/" target="_blank">
                        Go back
                        </a>
                    </p>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.write("Error during speech recognition:", e)
    else:
        st.write("Failed to save the audio to bytes buffer.")
else:
    st.write("No audio recorded.")
